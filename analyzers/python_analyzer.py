import re
import ast
import logging
from analyzers.common_analyzer import get_code_snippet

logger = logging.getLogger(__name__)

# Common Python anti-patterns
PYTHON_PATTERNS = [
    {
        'pattern': r'except\s*:',
        'bug_type': 'Bare Except',
        'severity': 'high',
        'description': 'Using bare except clause will catch all exceptions, including KeyboardInterrupt and SystemExit.',
        'recommendation': 'Specify the exceptions you want to catch, e.g., except Exception:'
    },
    {
        'pattern': r'exec\s*\(',
        'bug_type': 'Use of exec()',
        'severity': 'critical',
        'description': 'Use of exec() function can be dangerous and lead to code injection vulnerabilities.',
        'recommendation': 'Avoid using exec() and find a safer alternative.'
    },
    {
        'pattern': r'import\s+\*',
        'bug_type': 'Wildcard Import',
        'severity': 'medium',
        'description': 'Wildcard imports make it unclear which names are present in the namespace.',
        'recommendation': 'Import only the specific names you need.'
    },
    {
        'pattern': r'\.\.(/|\\)+',
        'bug_type': 'Path Traversal',
        'severity': 'high',
        'description': 'Potential path traversal vulnerability.',
        'recommendation': 'Validate and sanitize file paths to prevent directory traversal attacks.'
    },
    {
        'pattern': r'os\.system\(|subprocess\.call\(|subprocess\.Popen\(',
        'bug_type': 'Command Execution',
        'severity': 'high',
        'description': 'Use of system commands may lead to command injection vulnerabilities.',
        'recommendation': 'Validate and sanitize user input before using it in commands.'
    }
]

class PythonAstVisitor(ast.NodeVisitor):
    def __init__(self, file_path):
        self.bugs = []
        self.file_path = file_path
    
    def visit_Compare(self, node):
        """Check for identity comparisons with literals"""
        for op in node.ops:
            if isinstance(op, (ast.Is, ast.IsNot)):
                for expr in [node.left] + node.comparators:
                    if isinstance(expr, (ast.Constant, ast.Num, ast.Str, ast.NameConstant)):
                        self.bugs.append({
                            'line_number': node.lineno,
                            'bug_type': 'Identity Comparison with Literal',
                            'severity': 'medium',
                            'description': 'Using "is" or "is not" with literals can lead to unexpected results. Use "==" or "!=" instead.',
                            'code_snippet': get_code_snippet(self.file_path, node.lineno),
                            'recommendation': 'Replace "is" with "==" or "is not" with "!=" when comparing with literals.'
                        })
        self.generic_visit(node)
    
    def visit_BinOp(self, node):
        """Check for potential bugs in binary operations"""
        if isinstance(node.op, ast.Div):
            self.bugs.append({
                'line_number': node.lineno,
                'bug_type': 'Potential Division by Zero',
                'severity': 'medium',
                'description': 'Division operation that might cause a ZeroDivisionError.',
                'code_snippet': get_code_snippet(self.file_path, node.lineno),
                'recommendation': 'Add a check to ensure the denominator is not zero before division.'
            })
        self.generic_visit(node)
    
    def visit_Try(self, node):
        """Check for potential issues in try-except blocks"""
        for handler in node.handlers:
            if handler.type is None:
                self.bugs.append({
                    'line_number': handler.lineno,
                    'bug_type': 'Bare Except',
                    'severity': 'high',
                    'description': 'Using bare except clause will catch all exceptions, including KeyboardInterrupt and SystemExit.',
                    'code_snippet': get_code_snippet(self.file_path, handler.lineno),
                    'recommendation': 'Specify the exceptions you want to catch, e.g., except Exception:'
                })
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Check for potentially dangerous imports"""
        dangerous_imports = ['pickle', 'marshal', 'shelve']
        for alias in node.names:
            if alias.name in dangerous_imports:
                self.bugs.append({
                    'line_number': node.lineno,
                    'bug_type': 'Dangerous Import',
                    'severity': 'medium',
                    'description': f'Importing {alias.name} can be insecure when used with untrusted data.',
                    'code_snippet': get_code_snippet(self.file_path, node.lineno),
                    'recommendation': f'Be careful when using {alias.name} with data from untrusted sources.'
                })
        self.generic_visit(node)

def analyze_python_file(full_path, relative_path):
    """
    Analyze a Python file for bugs and issues
    
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
        for pattern_info in PYTHON_PATTERNS:
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
        
        # AST-based checks
        try:
            tree = ast.parse(content)
            visitor = PythonAstVisitor(full_path)
            visitor.visit(tree)
            bugs.extend(visitor.bugs)
        except SyntaxError as e:
            logger.warning(f"Syntax error in {relative_path}: {str(e)}")
            bugs.append({
                'line_number': getattr(e, 'lineno', 1),
                'bug_type': 'Syntax Error',
                'severity': 'high',
                'description': f'Python syntax error: {str(e)}',
                'code_snippet': get_code_snippet(full_path, getattr(e, 'lineno', 1)),
                'recommendation': 'Fix the syntax error to ensure the code can be interpreted.'
            })
    
    except Exception as e:
        logger.error(f"Error analyzing Python file {relative_path}: {str(e)}")
    
    return bugs
