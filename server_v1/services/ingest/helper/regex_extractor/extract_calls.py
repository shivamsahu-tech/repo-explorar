from typing import Set
import re


# This extracts the names of any types of calls from the node.text
def extract_calls_from_text(text: str, language: str) -> Set[str]:
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
        calls.update(re.findall(decorator_pattern, text))

        # Decorators with arguments: @cache(ttl=10)
        decorator_args_pattern = r'@(\w+)\s*\('
        calls.update(re.findall(decorator_args_pattern, text))

        # Direct function calls: run(), process_data()
        direct_call_pattern = r'\b([a-z_]\w*)\s*\('
        calls.update(re.findall(direct_call_pattern, text))

        # Method calls: obj.method()
        method_pattern = r'\.(\w+)\s*\('
        calls.update(re.findall(method_pattern, text))

        # Class instantiation: User(), Client()
        class_instantiation_pattern = r'\b([A-Z]\w*)\s*\('
        calls.update(re.findall(class_instantiation_pattern, text))

        # Static/Class method calls: Class.method()
        class_method_pattern = r'([A-Z]\w*)\.(\w+)\s*\('
        calls.update([m[1] for m in re.findall(class_method_pattern, text)])
    
    # Filter keywords
    keywords = {
        'if', 'else', 'for', 'while', 'return', 'function', 'class',
        'const', 'let', 'var', 'def', 'import', 'from', 'export',
        'try', 'catch', 'finally', 'throw', 'async', 'await',
        'new', 'this', 'super', 'typeof', 'instanceof',
        'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict'
    }
    
    return {c for c in calls if c.lower() not in keywords and len(c) > 1}

