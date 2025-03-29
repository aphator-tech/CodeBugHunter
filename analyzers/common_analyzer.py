import os
import re
import logging

logger = logging.getLogger(__name__)

# Patterns for common issues across all languages
COMMON_PATTERNS = [
    {
        'pattern': r'TODO|FIXME',
        'bug_type': 'Pending Implementation',
        'severity': 'info',
        'description': 'Found a TODO or FIXME comment that indicates incomplete code.',
        'recommendation': 'Review and implement the pending task.'
    },
    {
        'pattern': r'(?:username|password|secret|api.?key|token)(?:\s+)?=(?:\s+)?[\"\']([^\"\'\s]+)[\"\'"]',
        'bug_type': 'Hard-coded Credential',
        'severity': 'critical',
        'description': 'Detected a potential hard-coded credential in the code.',
        'recommendation': 'Remove hard-coded credentials and use environment variables or a secure vault.'
    },
    {
        'pattern': r'console\.log\(|print\(|fmt\.Print|System\.out\.print',
        'bug_type': 'Debug Statement',
        'severity': 'low',
        'description': 'Found a debug print statement that should be removed in production code.',
        'recommendation': 'Remove debug statements or replace with proper logging.'
    },
    {
        'pattern': r'catch\s*\(\s*(?:e|err|error|ex|exception)\s*\)\s*{}',
        'bug_type': 'Empty Catch Block',
        'severity': 'medium',
        'description': 'Empty catch block that silently swallows exceptions.',
        'recommendation': 'Handle exceptions properly or at least log them.'
    }
]

def get_code_snippet(file_path, line_number, context=3):
    """
    Extract a code snippet from a file around a specific line
    
    Args:
        file_path (str): Path to the file
        line_number (int): Line number to center snippet around
        context (int): Number of lines to include before and after
        
    Returns:
        str: The code snippet
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        start = max(0, line_number - context - 1)
        end = min(len(lines), line_number + context)
        
        snippet_lines = lines[start:end]
        snippet = ''
        
        for i, line in enumerate(snippet_lines):
            line_num = start + i + 1
            prefix = f"{line_num}: " if line_num == line_number else f"{line_num}  "
            snippet += prefix + line
            
        return snippet
    except Exception as e:
        logger.error(f"Error extracting code snippet from {file_path}: {str(e)}")
        return "Unable to extract code snippet"

def analyze_common_issues(full_path, relative_path):
    """
    Analyze a file for common issues across all languages
    
    Args:
        full_path (str): Full path to the file
        relative_path (str): Path relative to repository root
        
    Returns:
        list: Found bugs
    """
    bugs = []
    
    try:
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check each pattern
        for pattern_info in COMMON_PATTERNS:
            pattern = pattern_info['pattern']
            for i, line in enumerate(lines):
                match = re.search(pattern, line)
                if match:
                    line_number = i + 1
                    bug = {
                        'line_number': line_number,
                        'bug_type': pattern_info['bug_type'],
                        'severity': pattern_info['severity'],
                        'description': pattern_info['description'],
                        'code_snippet': get_code_snippet(full_path, line_number),
                        'recommendation': pattern_info['recommendation']
                    }
                    bugs.append(bug)
    
    except Exception as e:
        logger.error(f"Error analyzing common issues in {relative_path}: {str(e)}")
    
    return bugs

def check_file_size(full_path, relative_path):
    """
    Check if a file is too large, which could indicate code quality issues
    
    Args:
        full_path (str): Full path to the file
        relative_path (str): Path relative to repository root
        
    Returns:
        dict or None: Bug information if file is too large, None otherwise
    """
    try:
        file_size = os.path.getsize(full_path)
        line_count = 0
        
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            for _ in f:
                line_count += 1
        
        # Check for large files (>1000 lines)
        if line_count > 1000:
            return {
                'line_number': 1,
                'bug_type': 'Large File',
                'severity': 'medium',
                'description': f'File is very large ({line_count} lines) which may indicate poor code organization.',
                'code_snippet': None,
                'recommendation': 'Consider breaking down large files into smaller, more manageable modules.'
            }
    except Exception as e:
        logger.error(f"Error checking file size for {relative_path}: {str(e)}")
    
    return None
