import os
import re
from typing import List, Dict, Set, Optional, Tuple
from tree_sitter_language_pack import get_parser as get_lang_parser


IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'dist', 'build', '.next', 'coverage'}
LANGUAGES = {'py': 'python', 'js': 'javascript', 'ts': 'typescript', 'jsx': 'javascript', 'tsx': 'typescript'}

# Consolidated configuration
CONFIG = {
    'node_types': {
        'python': {
            'function_definition': 'FUNCTION', 'class_definition': 'CLASS', 'call': 'CALL',
            'import_statement': 'IMPORT', 'import_from_statement': 'IMPORT',
            'assignment': 'ASSIGNMENT', 'expression_statement': 'EXPRESSION'
        },
        'javascript': {
            'function_declaration': 'FUNCTION', 'function_expression': 'FUNCTION', 'arrow_function': 'FUNCTION',
            'class_declaration': 'CLASS', 'call_expression': 'CALL', 'import_statement': 'IMPORT',
            'variable_declaration': 'ASSIGNMENT', 'assignment_expression': 'ASSIGNMENT'
        }
    },
    'patterns': {
        'comments': {
            'python': [r'"""(.*?)"""', r"'''(.*?)'''", r'#\s*(.+)'],
            'javascript': [r'/\*\*(.*?)\*/', r'/\*(.*?)\*/', r'//\s*(.+)']
        },
        'imports': {
            'python': [r'(?:from\s+(\S+)\s+)?import\s+([^\n]+)', r'import\s+([^\n]+)'],
            'javascript': [r'(?:import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"])', r'require\([\'"]([^\'"]+)[\'"]\)']
        }
    }
}

parsers_cache = {}

def get_parser(language: str):
    """Cached parser retrieval."""
    if language not in parsers_cache:
        try:
            parsers_cache[language] = get_lang_parser(language)
        except Exception as e:
            print(f"Failed to build parser for {language}: {e}")
            parsers_cache[language] = None
    return parsers_cache.get(language)

def extract_patterns(text: str, language: str, pattern_type: str) -> List[str]:
    """Unified pattern extraction for comments, imports, etc."""
    patterns = CONFIG['patterns'].get(pattern_type, {}).get(language, [])
    results = []
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if isinstance(matches[0] if matches else None, tuple):
            results.extend([match for group in matches for match in group if match])
        else:
            results.extend([match.strip() for match in matches if match.strip()])
    
    return results



def smart_truncate(text: str, max_length: int = 2000) -> str:
    """Intelligent text truncation preserving structure."""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    
    # Find best cut point (prioritized list)
    for cut_char, threshold in [('\n\n', 0.8), ('\n', 0.75), ('.', 0.7), (',', 0.65), (' ', 0.6)]:
        cut_point = truncated.rfind(cut_char)
        if cut_point > max_length * threshold:
            return truncated[:cut_point + 1].strip()
    
    return truncated + "..."

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
    
    return name, smart_truncate(context_text)

def create_node_info(node, code: bytes, file_path: str, language: str, depth: int, parent_context: str) -> Dict:
    """Create comprehensive node information."""
    node_type = CONFIG['node_types'].get(language, {}).get(node.type)
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



def extract_nodes_from_file(file_path: str, language: str) -> List[Dict]:
    """Enhanced node extraction with unified processing."""
    try:
        with open(file_path, 'rb') as f:
            code = f.read()
        code_str = code.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []
    
    parser = get_parser(language)
    if not parser:
        return []
    
    tree = parser.parse(code)
    nodes = []
    
    # Create file-level context node
    imports = extract_patterns(code_str, language, 'imports')
    comments = extract_patterns(code_str, language, 'comments')
    
    file_node = {
        'id': f"{file_path}:FILE",
        'type': 'FILE',
        'name': os.path.basename(file_path),
        'text': smart_truncate(f"File: {file_path}\nImports: {imports}\nDocumentation: {' '.join(comments[:3])}\nContent preview: {code_str[:500]}"),
        'file': file_path,
        'language': language,
        'imports': imports,
        'comments': comments,
        'size': len(code_str),
        'start_line': 1,
        'end_line': len(code_str.splitlines()),
        'relationships': []
    }
    nodes.append(file_node)
    
    # Traverse and extract all nodes
    def traverse(node, depth=0, parent_context=""):
        node_info = create_node_info(node, code, file_path, language, depth, parent_context)
        
        if node_info:
            node_info['relationships'] = []  # Placeholder for future relationship analysis
            nodes.append(node_info)
            new_parent_context = f"{parent_context}.{node_info['name']}" if parent_context else node_info['name']
        else:
            new_parent_context = parent_context
        
        for child in node.children:
            traverse(child, depth + 1, new_parent_context)
    
    traverse(tree.root_node)
    return nodes


def chunk_text(text, chunk_size=1000, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def extract_all_nodes(repo_path: str) -> List[Dict]:
    """Extract all nodes with cross-file relationship tracking."""
    all_nodes = []
    file_relationships = {}
    
    print(f"Starting enhanced extraction from {repo_path}")
    
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            ext = file.split('.')[-1].lower()
            if ext in LANGUAGES:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                language = LANGUAGES[ext]
                
                print(f"Processing {relative_path}...")
                nodes = extract_nodes_from_file(file_path, language)
                
                # Track file relationships
                file_node = next((n for n in nodes if n['type'] == 'FILE'), None)
                if file_node:
                    file_relationships[relative_path] = file_node.get('imports', [])
                
                all_nodes.extend(nodes)
            elif file.lower().endswith(('.md', 'txt')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    for i, chunk in enumerate(chunk_text(content, 1000, 100)):
                        nodes.append({
                            'id': f"{file_path}:FILE_CHUNK_{i}",
                            'type': 'FILE_CHUNK',
                            'name': f"{os.path.basename(file_path)}_chunk_{i}",
                            'text': chunk,
                            'file': file_path,
                            'language': language,
                            'start_line': 1 + i*100, 
                            'end_line': 1 + i*100 + len(chunk.splitlines()),
                        })

                except Exception as e:
                    print(f"Failed to read {file_path}: {e}")
    
    # Add cross-file relationships to all file nodes
    for node in all_nodes:
        if node['type'] == 'FILE':
            node['file_relationships'] = file_relationships
    
    print(f"Extracted {len(all_nodes)} nodes from {len(file_relationships)} files")
    return all_nodes