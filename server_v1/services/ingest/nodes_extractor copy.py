from typing import Dict, List, Optional, Set
from services.ingest.parser import get_parser
from core.logging import get_logger
import re

logger = get_logger(__name__)

MAX_CHUNK_SIZE = 1500  # characters
MIN_CHUNK_SIZE = 50    # Skip nodes smaller than this


def make_base_node(
    node_id: str,
    name: Optional[str],
    ast_type: str,
    file_path: str,
    language: str,
    code_str: str,
    start_line: int,
    end_line: int,
    start_byte: int,
    end_byte: int,
    size: int,
    depth: int
) -> Dict:
    """Unified node skeleton for all node types."""
    return {
        "id": node_id,
        "name": name,
        "code_str": code_str,
        "ast_type": ast_type,
        "file": file_path,
        "language": language,
        "start_line": start_line,
        "end_line": end_line,
        "start_byte": start_byte,
        "end_byte": end_byte,
        "size": size,
        "relationships": {
            "belongs_to": [],      # File node ID (list with single element)
            "parent": [],          # Parent node ID (list with single element or empty)
            "sibling": [],         # Nearby sibling node IDs (2-3 nodes)
            "function_call": [],   # Resolved function definition node IDs
            "class_call": [],      # Resolved class definition node IDs
            "implements": [],      # Interface/trait node IDs this implements
            "extends": [],         # Class node ID this extends from
            "imports_from": []     # Import paths (will be resolved to node IDs in file_traversal)
        },
        "metadata": {
            "depth": depth,
            "calls": [],           # Raw extracted call names (for debugging)
            "inherits": [],        # Raw class/interface names inherited
            "type_references": [], # Raw type names referenced
            "is_definition": False,
            "definition_type": None  # "function", "class", "interface", "type", etc.
        }
    }


def extract_nodes_from_file(file_path: str, language: str, root_node_id: str) -> List[Dict]:
    """
    Extract chunks using recursive cAST algorithm.
    
    Returns:
        List of nodes including FILE node and all AST nodes
    """
    try:
        logger.info(f"Processing file {file_path}")
        with open(file_path, 'rb') as f:
            code = f.read()
        code_str = code.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return []
    
    # Extract imports from entire file (before parsing)
    file_imports = extract_imports(code_str, language)
    
    # ========================================================================
    # CREATE FILE NODE FIRST (before parsing AST)
    # ========================================================================
    
    file_node_id = f"{file_path}:FILE"
    file_node = make_base_node(
        node_id=file_node_id,
        name=file_path.split('/')[-1],  # Just filename
        ast_type="file",
        file_path=file_path,
        language=language,
        code_str=f"File: {file_path}\nImports: ', '.join(file_imports[:5])\nLines: {len(code_str.splitlines())}",
        start_line=1,
        end_line=len(code_str.splitlines()),
        start_byte=0,
        end_byte=len(code_str),
        size=len(code_str),
        depth=0
    )
    
    # File node relationships
    file_node["relationships"]["belongs_to"] = [root_node_id]
    file_node["relationships"]["imports_from"] = file_imports

    print(file_path)
    
    # File node metadata
    file_node["metadata"]["is_definition"] = False
    
    # Parse AST
    parser = get_parser(language)
    if not parser:
        logger.warning(f"No parser for {language}, returning only FILE node")
        return [file_node]
    
    tree = parser.parse(code)
    
    # Store all nodes (including FILE node)
    all_nodes = [file_node]
    
    # Store chunks by ID for lookup
    chunks_dict: Dict[str, Dict] = {file_node_id: file_node}
    
    # Track definitions in this file (for call resolution)
    definitions: Dict[str, str] = {}  # name -> node_id
    
    def chunk_ast_node(
        node,
        sibling_ids: Optional[List[str]] = None,
        depth: int = 1
    ) -> List[str]:
        """
        Recursive cAST chunking with relationship building.
        
        Returns:
            List of chunk IDs created from this node
        """
        if sibling_ids is None:
            sibling_ids = []
        
        node_size = node.end_byte - node.start_byte
        
        # # Skip tiny nodes
        # if node_size < MIN_CHUNK_SIZE:
        #     return sibling_ids
        
        # === CASE 1: Node fits - create chunk ===
        if node_size <= MAX_CHUNK_SIZE:
            try:
                text = node.text.decode('utf-8', errors='ignore')
            except:
                return sibling_ids
            
            if not text.strip():
                return sibling_ids
            
            # Create chunk ID
            chunk_id = f"{file_path}:{node.start_point[0]}:{node.type}"
            
            # Skip duplicates
            if chunk_id in chunks_dict:
                return sibling_ids
            
            # Extract name
            name = extract_name_from_node(node, text, language)
            
            # Extract calls
            calls = extract_calls_from_text(text, language)
            
            # Extract inheritance/implementation
            inherits = extract_inheritance(text, language)
            
            # Determine if definition and its type
            is_def, def_type = get_definition_info(node.type, language)
            
            # Create chunk
            chunk = make_base_node(
                node_id=chunk_id,
                name=name,
                ast_type=node.type,
                file_path=file_path,
                language=language,
                code_str=text,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                start_byte=node.start_byte,
                end_byte=node.end_byte,
                size=node_size,
                depth=depth
            )
            
            # Set relationships
            chunk["relationships"]["belongs_to"] = [file_node_id]
            
            
            # Add nearby siblings (last 2-3 only)
            nearby_siblings = sibling_ids[-3:] if len(sibling_ids) >= 3 else sibling_ids
            chunk["relationships"]["sibling"] = nearby_siblings.copy()
            
            # Imports only for import statement nodes
            if node.type in ['import_statement', 'import_declaration', 'import_from_statement']:
                chunk["relationships"]["imports_from"] = file_imports
            
            # Set metadata
            chunk["metadata"]["calls"] = list(calls)
            chunk["metadata"]["inherits"] = inherits
            chunk["metadata"]["is_definition"] = is_def
            chunk["metadata"]["definition_type"] = def_type
            
            # Store chunk
            chunks_dict[chunk_id] = chunk
            all_nodes.append(chunk)
            
            # Track definitions (for later call resolution)
            if is_def and name:
                definitions[name] = chunk_id
            
            # Add bidirectional sibling links (only to nearby siblings)
            for sib_id in nearby_siblings:
                if sib_id in chunks_dict:
                    # Only add if not already present
                    if chunk_id not in chunks_dict[sib_id]["relationships"]["sibling"]:
                        chunks_dict[sib_id]["relationships"]["sibling"].append(chunk_id)
            
            return sibling_ids + [chunk_id]
        
        # === CASE 2: Node too large - RECURSE to children ===
        else:
            child_sibling_ids = []
            for child in node.children:
                child_sibling_ids = chunk_ast_node(
                    child,
                    sibling_ids=child_sibling_ids,
                    depth=depth + 1
                )
            return sibling_ids
    
    # Start recursion (FILE node is parent of top-level)
    chunk_ast_node(
        tree.root_node,
        sibling_ids=[],
        depth=1
    )
    
    # ========================================================================
    # POST-PROCESSING: Resolve calls to definition node IDs
    # ========================================================================
    
    for chunk_id, chunk in chunks_dict.items():
        if chunk_id == file_node_id:
            continue  # Skip FILE node
        
        raw_calls = chunk["metadata"].get("calls", [])
        
        for call_name in raw_calls:
            # Check if this call matches a definition in the file
            if call_name in definitions:
                def_node_id = definitions[call_name]
                
                # Determine if it's a function or class call
                def_node = chunks_dict[def_node_id]
                def_type = def_node["metadata"].get("definition_type")
                
                if def_type in ["function", "method"]:
                    if def_node_id not in chunk["relationships"]["function_call"]:
                        chunk["relationships"]["function_call"].append(def_node_id)
                
                elif def_type in ["class", "interface", "enum"]:
                    if def_node_id not in chunk["relationships"]["class_call"]:
                        chunk["relationships"]["class_call"].append(def_node_id)
    
    # ========================================================================
    # POST-PROCESSING: Resolve inheritance relationships
    # ========================================================================
    
    for chunk_id, chunk in chunks_dict.items():
        if chunk_id == file_node_id:
            continue
        
        inherits = chunk["metadata"].get("inherits", [])
        
        for inherit_name in inherits:
            if inherit_name in definitions:
                parent_class_id = definitions[inherit_name]
                parent_node = chunks_dict[parent_class_id]
                parent_def_type = parent_node["metadata"].get("definition_type")
                
                # Distinguish between extends (class) and implements (interface)
                if parent_def_type == "interface":
                    if parent_class_id not in chunk["relationships"]["implements"]:
                        chunk["relationships"]["implements"].append(parent_class_id)
                else:
                    if parent_class_id not in chunk["relationships"]["extends"]:
                        chunk["relationships"]["extends"].append(parent_class_id)
    
    logger.info(f"Extracted {len(all_nodes)} nodes (including FILE) from {file_path}")
    return all_nodes


def extract_imports(code_str: str, language: str) -> List[Dict[str, any]]:
    """
    Extract all imports with their specific items (functions, classes, variables).
    
    Returns:
        List of dicts containing:
        - 'module': The module/file path being imported from
        - 'items': List of specific items imported (functions, classes, etc.)
        - 'import_type': Type of import (from_import, direct_import, etc.)
        - 'raw_statement': The original import statement
    """
    imports = []
    
    if language == 'python':
        # Pattern: from module import item1, item2, item3
        from_import_pattern = r'from\s+([a-zA-Z0-9_.]+)\s+import\s+([^;\n]+)'
        matches = re.findall(from_import_pattern, code_str, re.MULTILINE)
        for module, items_str in matches:
            # Split items and clean them
            items = [item.strip().split(' as ')[0].strip() 
                    for item in items_str.split(',')]
            imports.append({
                'module': module,
                'items': items,
                'import_type': 'from_import',
                'raw_statement': f'from {module} import {items_str}'
            })
        
        # Pattern: import module1, module2
        direct_import_pattern = r'import\s+([a-zA-Z0-9_., ]+)'
        matches = re.findall(direct_import_pattern, code_str, re.MULTILINE)
        for modules_str in matches:
            # Skip if it's part of a 'from ... import' statement
            if 'from' in code_str[max(0, code_str.find(modules_str)-10):code_str.find(modules_str)]:
                continue
            modules = [m.strip().split(' as ')[0].strip() 
                      for m in modules_str.split(',')]
            for module in modules:
                imports.append({
                    'module': module,
                    'items': [module],  # For direct import, the module itself is the item
                    'import_type': 'direct_import',
                    'raw_statement': f'import {module}'
                })
    
    elif language in ['javascript', 'typescript']:
        # Pattern: import { item1, item2 } from 'module'
        named_import_pattern = r'import\s+\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"]'
        matches = re.findall(named_import_pattern, code_str, re.MULTILINE)
        for items_str, module in matches:
            items = [item.strip().split(' as ')[0].strip() 
                    for item in items_str.split(',')]
            imports.append({
                'module': module,
                'items': items,
                'import_type': 'named_import',
                'raw_statement': f'import {{ {items_str} }} from "{module}"'
            })
        
        # Pattern: import defaultItem from 'module'
        default_import_pattern = r'import\s+([a-zA-Z0-9_$]+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        matches = re.findall(default_import_pattern, code_str, re.MULTILINE)
        for item, module in matches:
            # Skip if it's part of a named import or namespace import
            if '{' in code_str[max(0, code_str.find(item)-20):code_str.find(item)] or \
               '*' in code_str[max(0, code_str.find(item)-20):code_str.find(item)]:
                continue
            imports.append({
                'module': module,
                'items': [item],
                'import_type': 'default_import',
                'raw_statement': f'import {item} from "{module}"'
            })
        
        # Pattern: import * as namespace from 'module'
        namespace_import_pattern = r'import\s+\*\s+as\s+([a-zA-Z0-9_$]+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        matches = re.findall(namespace_import_pattern, code_str, re.MULTILINE)
        for namespace, module in matches:
            imports.append({
                'module': module,
                'items': [f'* as {namespace}'],
                'import_type': 'namespace_import',
                'raw_statement': f'import * as {namespace} from "{module}"'
            })
        
        # Pattern: const { item1, item2 } = require('module')
        require_destructure_pattern = r'(?:const|let|var)\s+\{([^}]+)\}\s*=\s*require\([\'"]([^\'"]+)[\'"]\)'
        matches = re.findall(require_destructure_pattern, code_str, re.MULTILINE)
        for items_str, module in matches:
            items = [item.strip().split(':')[0].strip() 
                    for item in items_str.split(',')]
            imports.append({
                'module': module,
                'items': items,
                'import_type': 'require_destructure',
                'raw_statement': f'const {{ {items_str} }} = require("{module}")'
            })
        
        # Pattern: const item = require('module')
        require_pattern = r'(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*require\([\'"]([^\'"]+)[\'"]\)'
        matches = re.findall(require_pattern, code_str, re.MULTILINE)
        for item, module in matches:
            # Skip if it's destructuring
            if '{' not in code_str[max(0, code_str.find(item)-5):code_str.find(item)]:
                imports.append({
                    'module': module,
                    'items': [item],
                    'import_type': 'require',
                    'raw_statement': f'const {item} = require("{module}")'
                })
        
        # Pattern: export { item1 } from 'module'
        re_export_pattern = r'export\s+\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"]'
        matches = re.findall(re_export_pattern, code_str, re.MULTILINE)
        for items_str, module in matches:
            items = [item.strip().split(' as ')[0].strip() 
                    for item in items_str.split(',')]
            imports.append({
                'module': module,
                'items': items,
                'import_type': 're_export',
                'raw_statement': f'export {{ {items_str} }} from "{module}"'
            })
    
    return imports


def extract_name_from_node(node, text: str, language: str) -> Optional[str]:
    """Extract identifier name from node."""
    # Try direct children first
    for child in node.children:
        if child.type in ['identifier', 'type_identifier', 'property_identifier', 'field_identifier']:
            try:
                return child.text.decode('utf-8', errors='ignore')
            except:
                pass
    
    # Fallback to regex
    patterns = {
        'python': [r'def\s+(\w+)', r'class\s+(\w+)', r'async\s+def\s+(\w+)'],
        'javascript': [
            r'function\s+(\w+)', r'class\s+(\w+)',
            r'const\s+(\w+)\s*=', r'let\s+(\w+)\s*=', r'var\s+(\w+)\s*=',
            r'(\w+)\s*=\s*\([^)]*\)\s*=>'
        ],
        'typescript': [
            r'function\s+(\w+)', r'class\s+(\w+)', r'interface\s+(\w+)',
            r'type\s+(\w+)\s*=', r'const\s+(\w+)\s*(?::\s*[^=]+)?=',
            r'enum\s+(\w+)'
        ]
    }
    
    for pattern in patterns.get(language, []):
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return None


def extract_calls_from_text(text: str, language: str) -> Set[str]:
    """Extract function/class calls from text."""
    calls = set()
    
    # Basic pattern: function_name(
    basic_call_pattern = r'(\w+)\s*\('
    matches = re.findall(basic_call_pattern, text)
    calls.update(matches)
    
    # Language-specific
    if language in ['javascript', 'typescript']:
        # JSX components
        jsx_pattern = r'<([A-Z]\w+)'
        jsx_matches = re.findall(jsx_pattern, text)
        calls.update(jsx_matches)
        
        # Method calls
        method_pattern = r'\.(\w+)\s*\('
        method_matches = re.findall(method_pattern, text)
        calls.update(method_matches)
        
        # new Constructor()
        constructor_pattern = r'new\s+(\w+)\s*\('
        constructor_matches = re.findall(constructor_pattern, text)
        calls.update(constructor_matches)
    
    elif language == 'python':
        # Decorators
        decorator_pattern = r'@(\w+)'
        decorator_matches = re.findall(decorator_pattern, text)
        calls.update(decorator_matches)
    
    # Filter keywords
    keywords = {
        'if', 'else', 'for', 'while', 'return', 'function', 'class',
        'const', 'let', 'var', 'def', 'import', 'from', 'export',
        'try', 'catch', 'finally', 'throw', 'async', 'await',
        'new', 'this', 'super', 'typeof', 'instanceof',
        'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict'
    }
    
    return {c for c in calls if c.lower() not in keywords and len(c) > 1}


def extract_inheritance(text: str, language: str) -> List[str]:
    """Extract class inheritance and interface implementation."""
    inherits = []
    
    if language in ['javascript', 'typescript']:
        # class X extends Y
        extends_pattern = r'class\s+\w+\s+extends\s+(\w+)'
        extends_matches = re.findall(extends_pattern, text)
        inherits.extend(extends_matches)
        
        # class X implements Y, Z
        implements_pattern = r'implements\s+([\w\s,]+)'
        implements_matches = re.findall(implements_pattern, text)
        for match in implements_matches:
            interfaces = [i.strip() for i in match.split(',')]
            inherits.extend(interfaces)
    
    elif language == 'python':
        # class X(Y, Z):
        class_pattern = r'class\s+\w+\(([^)]+)\)'
        class_matches = re.findall(class_pattern, text)
        for match in class_matches:
            bases = [b.strip() for b in match.split(',')]
            inherits.extend(bases)
    
    return inherits


def get_definition_info(ast_type: str, language: str) -> tuple[bool, Optional[str]]:
    """
    Check if node is a definition and return its type.
    
    Returns:
        (is_definition, definition_type)
    """
    definition_map = {
        # Functions
        'function_definition': 'function',
        'function_declaration': 'function',
        'function_expression': 'function',
        'arrow_function': 'function',
        'method_definition': 'method',
        
        # Classes
        'class_definition': 'class',
        'class_declaration': 'class',
        
        # Interfaces
        'interface_declaration': 'interface',
        
        # Types
        'type_alias_declaration': 'type',
        
        # Enums
        'enum_declaration': 'enum',
        
        # Variables
        'lexical_declaration': 'variable',
        'variable_declaration': 'variable'
    }
    
    def_type = definition_map.get(ast_type)
    return (def_type is not None, def_type)