import re
import logging
from analyzers.common_analyzer import get_code_snippet

logger = logging.getLogger(__name__)

# Common JavaScript/TypeScript anti-patterns
JS_PATTERNS = [
    {
        'pattern': r'eval\s*\(',
        'bug_type': 'Use of eval()',
        'severity': 'critical',
        'description': 'Use of eval() function can lead to code injection vulnerabilities.',
        'recommendation': 'Avoid using eval() and find a safer alternative.'
    },
    {
        'pattern': r'==\s*null',
        'bug_type': 'Loose Null Check',
        'severity': 'low',
        'description': 'Using == with null will also match undefined.',
        'recommendation': 'Use === for strict equality checking.'
    },
    {
        'pattern': r'document\.write\(',
        'bug_type': 'document.write()',
        'severity': 'medium',
        'description': 'document.write() can overwrite the entire document and is considered bad practice.',
        'recommendation': 'Use DOM manipulation methods instead, like appendChild().'
    },
    {
        'pattern': r'innerHTML\s*=',
        'bug_type': 'innerHTML Assignment',
        'severity': 'high',
        'description': 'Direct assignment to innerHTML can lead to XSS vulnerabilities.',
        'recommendation': 'Use textContent for text or sanitize HTML input before using innerHTML.'
    },
    {
        'pattern': r'setTimeout\(\s*["\'](.*?)["\']\s*\)',
        'bug_type': 'setTimeout with String',
        'severity': 'medium',
        'description': 'Using setTimeout with a string argument is similar to using eval().',
        'recommendation': 'Use a function reference instead of a string in setTimeout.'
    },
    {
        'pattern': r'new\s+Function\(',
        'bug_type': 'new Function()',
        'severity': 'high',
        'description': 'Creating functions from strings is similar to eval() and can lead to injection attacks.',
        'recommendation': 'Avoid creating functions from strings.'
    },
    {
        'pattern': r'alert\(|confirm\(|prompt\(',
        'bug_type': 'Browser Dialog',
        'severity': 'low',
        'description': 'Use of browser dialogs (alert, confirm, prompt) creates a poor user experience.',
        'recommendation': 'Use custom UI components instead of browser dialogs.'
    },
    {
        'pattern': r'localStorage\.|sessionStorage\.',
        'bug_type': 'Web Storage API',
        'severity': 'info',
        'description': 'Use of Web Storage API (localStorage, sessionStorage) should be carefully reviewed.',
        'recommendation': 'Ensure sensitive data is not stored in Web Storage and consider encryption if needed.'
    }
]

def check_for_strict_equality(content):
    """
    Check for loose equality comparisons in JavaScript
    
    Args:
        content (str): File content
        
    Returns:
        list: Found bugs related to loose equality
    """
    bugs = []
    lines = content.split('\n')
    
    # Regular expression for loose equality (== or !=) but not strict equality (=== or !==)
    pattern = r'[^=!]=[^=]|[^!]=[^=]'
    
    for i, line in enumerate(lines):
        match = re.search(pattern, line)
        if match and ' = ' not in line:  # Avoid matching simple assignments
            line_number = i + 1
            bugs.append({
                'line_number': line_number,
                'bug_type': 'Loose Equality',
                'severity': 'low',
                'description': 'Use of loose equality (== or !=) instead of strict equality (=== or !==).',
                'code_snippet': line.strip(),
                'recommendation': 'Use === and !== for strict type checking.'
            })
    
    return bugs

def analyze_javascript_file(full_path, relative_path):
    """
    Analyze a JavaScript/TypeScript file for bugs and issues
    
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
        
        # Pattern-based checks
        for pattern_info in JS_PATTERNS:
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
        
        # Check for loose equality
        equality_bugs = check_for_strict_equality(content)
        bugs.extend(equality_bugs)
        
        # Check for console.log statements
        for i, line in enumerate(lines):
            if 'console.log(' in line:
                line_number = i + 1
                bugs.append({
                    'line_number': line_number,
                    'bug_type': 'Console Statement',
                    'severity': 'low',
                    'description': 'console.log() statements should be removed in production code.',
                    'code_snippet': get_code_snippet(full_path, line_number),
                    'recommendation': 'Remove console.log() statements or use a proper logging library.'
                })
    
    except Exception as e:
        logger.error(f"Error analyzing JavaScript file {relative_path}: {str(e)}")
    
    return bugs
