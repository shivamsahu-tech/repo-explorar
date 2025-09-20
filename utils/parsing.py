import os
from typing import List, Dict
from tree_sitter_language_pack import get_parser as get_lang_parser

IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'dist', 'build'}
LANGUAGES = {'py': 'python', 'js': 'javascript'}

NODE_TYPES = {
    'python': {'function_definition': 'FUNCTION', 'class_definition': 'CLASS', 'call': 'CALL'},
    'javascript': {'function_declaration': 'FUNCTION', 'class_declaration': 'CLASS', 'call_expression': 'CALL'}
}



parsers_cache = {}

def get_parser(language: str):
    if language not in parsers_cache:
        try:
            # `get_lang_parser` returns a configured Parser instance
            parser = get_lang_parser(language)
            print("built parser", parser)
            parsers_cache[language] = parser
        except Exception as e:
            print(f"Failed to build parser for {language}: {e}")
            parsers_cache[language] = None

    return parsers_cache.get(language)



def extract_name(node, code: str) -> str:
    for child in node.children:
        if child.type == 'identifier':
            return child.text.decode('utf-8')
    return 'unknown'

def extract_nodes_from_file(file_path: str, language: str) -> List[Dict]:
    with open(file_path, 'rb') as f:
            code = f.read()
    
    parser = get_parser(language)
    if not parser:
        return []
    tree = parser.parse(code)
    nodes = []
    
    def traverse(node, depth=0):
        node_type = NODE_TYPES.get(language, {}).get(node.type)
        if node_type:
            text = code[node.start_byte:node.end_byte]
            name = extract_name(node, code)
            
            nodes.append({
                'id': f"{file_path}:{node.start_point[0]}:{node_type}",
                'type': node_type,
                'name': name,
                'text': text,
                'file': file_path,
                'start_line': node.start_point[0] + 1,
                'end_line': node.end_point[0] + 1,
                'language': language
            })
        
        for child in node.children:
            traverse(child, depth + 1)
    
    traverse(tree.root_node)    
    return nodes

def extract_all_nodes(repo_path: str) -> List[Dict]:
    all_nodes = []
    
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            ext = file.split('.')[-1].lower()
            if ext in LANGUAGES:
                file_path = os.path.join(root, file)
                language = LANGUAGES[ext]
                nodes = extract_nodes_from_file(file_path, language)
                all_nodes.extend(nodes)
    
    return all_nodes