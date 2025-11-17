# services/ingest/file_traversal.py
import os
from typing import Dict, List, Set, Optional
from pathlib import Path
from core.logging import get_logger
from services.ingest.nodes_extractor import extract_nodes_from_file
from services.ingest.nodes_extractor import make_base_node

logger = get_logger(__name__)

IGNORE_DIRS = {
    '.git', 'node_modules', '__pycache__', '.venv', 'dist', 
    'build', '.next', 'coverage', '.cache', 'out', '.vscode',
    '.idea', 'venv', 'env', '__mocks__', '.pytest_cache'
}

LANGUAGES = {
    'py': 'python', 
    'js': 'javascript', 
    'ts': 'typescript', 
    'jsx': 'javascript',
    'tsx': 'typescript'
}

DOC_EXTENSIONS = ('.md', '.txt', '.rst', '.markdown')
CONFIG_EXTENSIONS = ('.json', '.yaml', '.yml', '.toml', '.ini', '.cfg')

STANDARD_LIBS = {
    'python': {'os', 'sys', 'json', 're', 'typing', 'collections', 'itertools', 
               'functools', 'pathlib', 'datetime', 'math', 'random', 'unittest',
               'pytest', 'numpy', 'pandas', 'requests', 'flask', 'django'},
    'javascript': {'react', 'react-dom', 'vue', 'angular', 'axios', 'lodash',
                   'express', 'next', 'node'},
    'typescript': {'react', 'react-dom', 'vue', 'angular', 'axios', 'lodash',
                   'express', 'next', 'node'}
}


def resolve_import_path_to_file(import_module: str, current_file: str, 
                                 repo_path: str, language: str) -> Optional[str]:
    """
    Resolve an import module path to an actual file path.
    
    Args:
        import_module: The module being imported (e.g., './Handler', 'src.utils')
        current_file: The file containing the import
        repo_path: Root directory of the repository
        language: Programming language
    
    Returns:
        Resolved file path relative to repo_path, or None if not found
    """
    current_dir = os.path.dirname(current_file)
    
    if language == 'python':
        # Convert module notation to file path (e.g., 'src.utils' -> 'src/utils.py')
        if import_module.startswith('.'):
            # Relative import
            level = len(import_module) - len(import_module.lstrip('.'))
            module_path = import_module.lstrip('.')
            base_dir = current_dir
            for _ in range(level - 1):
                base_dir = os.path.dirname(base_dir)
            file_path = os.path.join(base_dir, module_path.replace('.', os.sep))
        else:
            # Absolute import from project root
            file_path = os.path.join(repo_path, import_module.replace('.', os.sep))
        
        # Try different variations
        possible_paths = [
            file_path + '.py',
            os.path.join(file_path, '__init__.py'),
        ]
    
    else:  # javascript/typescript
        if import_module.startswith('.'):
            # Relative import
            file_path = os.path.normpath(os.path.join(current_dir, import_module))
        else:
            # Might be absolute or node_modules - skip external packages
            return None
        
        # Try different extensions
        extensions = ['.ts', '.tsx', '.js', '.jsx']
        possible_paths = [
            file_path + ext for ext in extensions
        ] + [
            os.path.join(file_path, 'index' + ext) for ext in extensions
        ]
    
    # Check which path exists and return relative to repo_path
    for path in possible_paths:
        if os.path.isfile(path):
            return os.path.relpath(path, repo_path)
    
    return None


def is_external_import(import_module: str, language: str) -> bool:
    """Check if an import is from external package/standard library."""
    # Check standard libraries
    module_root = import_module.split('.')[0].split('/')[0]
    if module_root in STANDARD_LIBS.get(language, set()):
        return True
    
    # For JS/TS, anything not starting with . or / is external
    if language in ['javascript', 'typescript']:
        if not import_module.startswith('.') and not import_module.startswith('/'):
            return True
    
    return False


def find_imported_items_in_file(file_nodes: List[Dict], imported_items: List[str]) -> List[str]:
    """
    Find the node IDs of specific imported items within a file's nodes.
    
    Args:
        file_nodes: All nodes from the imported file
        imported_items: List of item names to find (functions, classes, etc.)
    
    Returns:
        List of node IDs that match the imported items
    """
    matched_node_ids = []
    
    for item_name in imported_items:
        # Skip namespace imports like "* as utils"
        if item_name.startswith('*'):
            continue
            
        # Look for matching definitions in the file
        for node in file_nodes:
            node_name = node.get('name')
            ast_type = node.get('ast_type', '')
            
            # Skip FILE nodes
            if ast_type == 'file':
                continue
            
            # Match by name
            if node_name == item_name:
                # Check various node types that could be exported
                if ast_type in [
                    'function', 'function_declaration', 'function_definition',
                    'class', 'class_declaration', 'class_definition',
                    'variable', 'variable_declaration', 'variable_declarator',
                    'const', 'let', 'var',
                    'arrow_function', 'method_definition',
                    'export_statement', 'export_specifier',
                    'interface', 'type_alias', 'enum'
                ]:
                    matched_node_ids.append(node['id'])
                    logger.debug(f"Found match: {item_name} -> {node['id']} (type: {ast_type})")
                    break
    
    return matched_node_ids


def resolve_imports_to_node_ids(all_nodes: List[Dict], repo_path: str) -> List[Dict]:
    """
    Resolve all imports_from to actual node IDs for internal imports.
    
    Args:
        all_nodes: List of all extracted nodes
        repo_path: Root directory of the repository
    
    Returns:
        Updated list of nodes with resolved import references
    """
    # Build file to nodes mapping
    file_to_nodes = {}
    for node in all_nodes:
        file_path = node.get('file', '')
        if file_path:
            relative_path = os.path.relpath(file_path, repo_path)
            if relative_path not in file_to_nodes:
                file_to_nodes[relative_path] = []
            file_to_nodes[relative_path].append(node)
    
    logger.info(f"Resolving imports across {len(file_to_nodes)} files...")
    
    # Process each node that has imports
    for node in all_nodes:
        imports_from = node.get('relationships', {}).get('imports_from', [])
        
        if not imports_from:
            continue
        
        current_file = node.get('file', '')
        language = node.get('language', '')
        resolved_imports = []
        
        for import_info in imports_from:
            module = import_info.get('module', '')
            items = import_info.get('items', [])
            
            # Check if it's an external import
            if is_external_import(module, language):
                # Keep external imports but mark them
                import_info['is_external'] = True
                import_info['resolved_node_ids'] = []
                resolved_imports.append(import_info)
                continue
            
            # Try to resolve to actual file
            resolved_file = resolve_import_path_to_file(
                module, current_file, repo_path, language
            )
            
            if not resolved_file:
                logger.warning(f"Could not resolve import '{module}' from {current_file}")
                import_info['is_external'] = False
                import_info['resolved_node_ids'] = []
                import_info['resolution_failed'] = True
                resolved_imports.append(import_info)
                continue
            
            # Get all nodes from the imported file
            imported_file_nodes = file_to_nodes.get(resolved_file, [])
            
            if not imported_file_nodes:
                logger.warning(f"No nodes found for resolved file: {resolved_file}")
                import_info['is_external'] = False
                import_info['resolved_node_ids'] = []
                import_info['resolution_failed'] = True
                resolved_imports.append(import_info)
                continue
            
            # Find specific imported items in the file
            if items and items != ['*']:
                resolved_node_ids = find_imported_items_in_file(imported_file_nodes, items)
                
                # Debug: Log available nodes if nothing found
                if not resolved_node_ids:
                    logger.warning(f"Could not find items {items} in {resolved_file}")
                    logger.debug(f"Available nodes in {resolved_file}:")
                    for n in imported_file_nodes[:10]:  # Show first 10 nodes
                        logger.debug(f"  - {n.get('name')} ({n.get('ast_type')})")
            else:
                # Import entire file - reference the FILE node
                file_node = next((n for n in imported_file_nodes if n['ast_type'] == 'file'), None)
                resolved_node_ids = [file_node['id']] if file_node else []
            
            # Update import info with resolved data
            import_info['is_external'] = False
            import_info['resolved_file'] = resolved_file
            import_info['resolved_node_ids'] = resolved_node_ids
            resolved_imports.append(import_info)
            
            logger.debug(f"Resolved {module} -> {len(resolved_node_ids)} node(s)")
        
        # Update the node with resolved imports
        node['relationships']['imports_from'] = resolved_imports
    
    logger.info("Import resolution complete!")
    return all_nodes


def extract_all_nodes(repo_path: str) -> List[Dict]:
    """Extract all nodes with cross-file relationship tracking."""
    all_nodes = []
    file_relationships = {}

    root_node_id = f"{repo_path}:ROOT"
    root_node = make_base_node(
        node_id=root_node_id,
        name="ROOT",  # Just filename
        ast_type="ROOT",
        file_path=repo_path,
        language="",
        code_str="",
        start_line=0,
        end_line=0,
        start_byte=0,
        end_byte=0,
        size=0,
        depth=0
    )

    all_nodes.append(root_node)
    
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
                
                nodes = extract_nodes_from_file(file_path, language, root_node_id)
                
                # Track file relationships
                file_node = next((n for n in nodes if n.get('ast_type') == 'file'), None)
                if file_node:
                    imports = file_node.get('relationships', {}).get('imports_from', [])
                    file_relationships[relative_path] = imports
                
                all_nodes.extend(nodes)
            
            elif file.lower().endswith(('.md', '.txt')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Simple chunking (you can replace with your chunk_text function)
                    chunk_size = 1000
                    for i in range(0, len(content), chunk_size):
                        chunk = content[i:i+chunk_size]
                        all_nodes.append({
                            'id': f"{file_path}:FILE_CHUNK_{i}",
                            'ast_type': 'FILE_CHUNK',
                            'name': f"{os.path.basename(file_path)}_chunk_{i//chunk_size}",
                            'code_str': chunk,
                            'file': file_path,
                            'language': 'markdown',
                            'start_line': 1,
                            'end_line': len(chunk.splitlines()),
                            'relationships': {},
                            'metadata': {}
                        })
                except Exception as e:
                    print(f"Failed to read {file_path}: {e}")
    
    print(f"Extracted {len(all_nodes)} nodes from {len(file_relationships)} files")
    
    # Resolve all imports to node IDs
    all_nodes = resolve_imports_to_node_ids(all_nodes, repo_path)
    
    return all_nodes