import re
import logging
from analyzers.common_analyzer import get_code_snippet

logger = logging.getLogger(__name__)

# Common Go anti-patterns
GO_PATTERNS = [
    {
        'pattern': r'if\s+err\s*!=\s*nil\s*{\s*return\s*(?:nil,)?\s*err\s*}',
        'bug_type': 'Error Handling',
        'severity': 'info',
        'description': 'Standard error handling pattern detected. Consider adding context to errors.',
        'recommendation': 'Use fmt.Errorf() or errors.Wrap() to add context to returned errors.'
    },
    {
        'pattern': r'defer\s+file\.Close\(\)',
        'bug_type': 'Unchecked Close',
        'severity': 'medium',
        'description': 'Unchecked Close() call in a defer statement.',
        'recommendation': 'Check the error returned by Close() in a defer statement.'
    },
    {
        'pattern': r'var\s+\w+\s+map\[.+\].+',
        'bug_type': 'Nil Map',
        'severity': 'medium',
        'description': 'Declaring a map without initialization will result in a nil map.',
        'recommendation': 'Initialize maps with make() or map literals, e.g., make(map[string]int).'
    },
    {
        'pattern': r'err\s*:=\s*.+\s*if\s+err\s*!=\s*nil\s*{\s*}',
        'bug_type': 'Empty Error Check',
        'severity': 'high',
        'description': 'Error check with empty block will ignore errors.',
        'recommendation': 'Either handle the error or explicitly return it.'
    },
    {
        'pattern': r'for\s+_,\s*\w+\s*:=\s*range',
        'bug_type': 'Range Loop Key Not Used',
        'severity': 'info',
        'description': 'Range loop where the key is not used.',
        'recommendation': 'Use the blank identifier for the key if it\'s not needed: for _, value := range ...'
    },
    {
        'pattern': r'fmt\.Println\(\s*"[^"]*"\s*,\s*err\s*\)',
        'bug_type': 'Error Not Formatted',
        'severity': 'low',
        'description': 'Using fmt.Println to print errors is not recommended.',
        'recommendation': 'Use fmt.Errorf() or log.Printf() to format errors properly.'
    }
]

def analyze_go_file(full_path, relative_path):
    """
    Analyze a Go file for bugs and issues
    
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
        for pattern_info in GO_PATTERNS:
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
        
        # Check for unused imports
        import_lines = []
        for i, line in enumerate(lines):
            if re.match(r'\s*import\s+\(', line):
                j = i + 1
                while j < len(lines) and not re.match(r'\s*\)', lines[j]):
                    import_line = lines[j].strip()
                    if import_line and not import_line.startswith('//'):
                        import_name = import_line.split('"')[1] if '"' in import_line else import_line
                        import_lines.append((j + 1, import_name))
                    j += 1
        
        # Check if imports are used
        for line_number, import_name in import_lines:
            package_name = import_name.split('/')[-1]
            if package_name and not any(package_name in line for line in lines):
                bugs.append({
                    'line_number': line_number,
                    'bug_type': 'Unused Import',
                    'severity': 'low',
                    'description': f'Import {import_name} appears to be unused.',
                    'code_snippet': get_code_snippet(full_path, line_number),
                    'recommendation': 'Remove unused imports.'
                })
    
    except Exception as e:
        logger.error(f"Error analyzing Go file {relative_path}: {str(e)}")
    
    return bugs
