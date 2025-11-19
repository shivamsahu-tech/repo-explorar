from typing import Optional
import re

# Extract the name from the text chunk, like function name in the function chunk
def extract_name_from_node(node, text: str, language: str) -> Optional[str]:

    # Try direct children first
    for child in node.children:
        if child.type in ['identifier', 'type_identifier', 'property_identifier', 'field_identifier']:
            try:
                return child.text.decode('utf-8', errors='ignore')
            except:
                pass
    
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