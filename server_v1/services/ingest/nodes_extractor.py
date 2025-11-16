import os
import re
from typing import Dict, List, Tuple
from core.logging import get_logger
from services.ingest.parser import get_parser
from config import PATTERN_CONFIG, NODE_TYPES

logger = get_logger(__name__)


#  It extract nodes from a single file
def extract_nodes_from_file(file_path: str, language: str) -> List[Dict]:

    try: 
        logger.info(f"Processing file {file_path}")
        with open(file_path, 'rb') as f:
            code = f.read()
        code_str = code.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"Error reading file {file_path} : {e}")
        return []
    
    parser = get_parser(language)

    if not parser:
        return []
    
    tree = parser.parse(code)
    nodes = []

    logger.info(f"Build syntax tree for file : {file_path}")
    imports = extract_patterns(code_str, language, 'imports')
    comments = extract_patterns(code_str, language, 'comments')
    logger.info(f"Extracted imports and comments using regest from file : {file_path}")


    # one node
    file_node = {
        'id': f"{file_path}:FILE",
        'type': "FILE",
        'name': os.path.basename(file_path),
        'text': f"File: {file_path}\nImports: {imports}\nDocumentation: {' '.join(comments[:3])}\nContent preview: {code_str[:500]}",
        'file':file_path,
        'language': language,
        'imports': imports,
        'comments': comments,
        'size': len(code_str),
        'start_line': 1,
        'end_line': len(code_str.splitlines()),
        'relationships':[]
    }

    nodes.append(file_node)


    # Now traverse the tree to extract all nodes, using dfs
    def traverse_dfs(node, depth=0, parent_context=""):
        node_info = create_node_info(node, code, file_path, language, depth, parent_context)

        if node_info:
            node_info['relationships'] = []
            nodes.append(node_info)
            new_parent_context = f"{parent_context}.{node_info['name']}" if parent_context else node_info['name']
        else: 
            new_parent_context = parent_context
        
        for child in node.children:
            traverse_dfs(child, depth+1, new_parent_context)
    
    traverse_dfs(tree.root_node)
    return nodes


# Extract comments or imports using REGEX
def extract_patterns(code_str: str, language: str, pattern_type: str) -> List[str]:

    regex_patterns = PATTERN_CONFIG.get(pattern_type, {}).get(language, [])

    if not regex_patterns:
        return []
    
    extracted: List[str] = []

    for pattern in regex_patterns:
        matches = re.findall(pattern, code_str, flags=re.DOTALL) # DOTALL for multiline

        if not matches:
            continue
        
        if isinstance(matches[0], tuple):
            # If there is multiple matches/multiple capture group :  r'(?:from\s+(\S+)\s+)?import\s+([^\n]+)', "from os import path \n import sys" ==> [("os", "path"), (None, "sys")]
            for group in matches:
                for item in group:
                    if item and item.strip():
                        extracted.append(item.strip())
        else:
            # If there is only one matches : re.findall(r'#\s*(.+)', "hello # comment") ==> ["comment"]
            for item in matches:
                if item and item.strip():
                    extracted.append(item.strip())
    
    return extracted












# todo both
def extract_name_and_context(node, code: bytes, context_window: int = 300) -> Tuple[str, str]:
    """Extract both node name and contextual text in one pass."""
    # Extract name
    name = 'unknown'
    for child in node.children:
        if child.type == 'identifier':
            name = child.text.decode('utf-8')
            break
    
    # Handle complex patterns for assignments/declarations
    if name == 'unknown' and node.type in ['assignment', 'variable_declaration']:
        for child in node.children:
            if child.type in ['identifier', 'variable_declarator']:
                for grandchild in child.children:
                    if grandchild.type == 'identifier':
                        name = grandchild.text.decode('utf-8')
                        break
                if name != 'unknown':
                    break
    
    # Extract contextual text
    start_context = max(0, node.start_byte - context_window)
    end_context = min(len(code), node.end_byte + context_window)
    context_text = code[start_context:end_context].decode('utf-8', errors='ignore')
    
    return name, context_text[:2000]

def create_node_info(node, code: bytes, file_path: str, language: str, depth: int, parent_context: str) -> Dict:
    """Create comprehensive node information."""
    node_type = NODE_TYPES.get(language, {}).get(node.type)
    if not node_type:
        return None
    
    name, contextual_text = extract_name_and_context(node, code)
    
    node_info = {
        'id': f"{file_path}:{node.start_point[0]}:{node_type}:{name}",
        'type': node_type,
        'name': name,
        'text': contextual_text,
        'file': file_path,
        'start_line': node.start_point[0] + 1,
        'end_line': node.end_point[0] + 1,
        'language': language,
        'depth': depth,
        'parent_context': parent_context,
        'size': node.end_byte - node.start_byte
    }
    
    # Add language-specific enhancements
    if node_type in ['FUNCTION', 'CLASS']:
        raw_text = code[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')
        if language == 'python':
            docstring_match = re.search(r'"""(.*?)"""', raw_text, re.DOTALL)
            if docstring_match:
                node_info['docstring'] = docstring_match.group(1).strip()
    
    return node_info

