import os
import logging
import re

logger = logging.getLogger(__name__)

# Language detection based on file extensions
LANGUAGE_EXTENSIONS = {
    'py': 'Python',
    'js': 'JavaScript',
    'ts': 'TypeScript',
    'jsx': 'React',
    'tsx': 'React TypeScript',
    'html': 'HTML',
    'css': 'CSS',
    'scss': 'SCSS',
    'sass': 'SASS',
    'json': 'JSON',
    'xml': 'XML',
    'yaml': 'YAML',
    'yml': 'YAML',
    'md': 'Markdown',
    'go': 'Go',
    'rb': 'Ruby',
    'php': 'PHP',
    'java': 'Java',
    'c': 'C',
    'cpp': 'C++',
    'h': 'C/C++ Header',
    'hpp': 'C++ Header',
    'cs': 'C#',
    'rs': 'Rust',
    'swift': 'Swift',
    'kt': 'Kotlin',
    'sql': 'SQL'
}

def detect_language(file_path):
    """
    Detect the programming language of a file based on its extension
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Detected language or 'Unknown'
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lstrip('.').lower()
    
    # Special case for Dockerfiles
    if os.path.basename(file_path).lower() == 'dockerfile':
        return 'Dockerfile'
    
    # Special case for Makefiles
    if os.path.basename(file_path).lower() == 'makefile':
        return 'Makefile'
    
    return LANGUAGE_EXTENSIONS.get(ext, 'Unknown')

def count_lines(file_path):
    """
    Count the number of lines in a file
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        int: Number of lines in the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception as e:
        logger.error(f"Error counting lines in {file_path}: {str(e)}")
        return 0

def analyze_language_stats(repo_path, file_list):
    """
    Analyze language statistics for a repository
    
    Args:
        repo_path (str): Path to the repository
        file_list (list): List of files to analyze
        
    Returns:
        dict: Language statistics
    """
    stats = {}
    
    for file_path in file_list:
        full_path = os.path.join(repo_path, file_path)
        if not os.path.isfile(full_path):
            continue
            
        language = detect_language(file_path)
        line_count = count_lines(full_path)
        
        if language not in stats:
            stats[language] = {
                'file_count': 0,
                'line_count': 0
            }
        
        stats[language]['file_count'] += 1
        stats[language]['line_count'] += line_count
    
    return stats
