from typing import Dict, List
import re

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