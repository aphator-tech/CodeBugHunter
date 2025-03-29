import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

def generate_report(scan, bugs, language_stats):
    """
    Generate a comprehensive report from scan results
    
    Args:
        scan: The Scan object
        bugs: List of Bug objects
        language_stats: List of LanguageStats objects
        
    Returns:
        dict: Report data
    """
    logger.info(f"Generating report for scan {scan.id}")
    
    # Initialize report structure
    report = {
        'summary': {
            'total_files': scan.total_files,
            'analyzed_files': scan.analyzed_files,
            'total_bugs': scan.total_bugs,
            'timestamp': scan.timestamp
        },
        'severity_breakdown': defaultdict(int),
        'bug_types': defaultdict(int),
        'language_breakdown': defaultdict(lambda: {'count': 0, 'bugs': 0, 'bug_density': 0}),
        'most_affected_files': defaultdict(int),
        'critical_bugs': []
    }
    
    # Process bugs for statistics
    for bug in bugs:
        # Severity breakdown
        report['severity_breakdown'][bug.severity] += 1
        
        # Bug types
        report['bug_types'][bug.bug_type] += 1
        
        # Most affected files
        report['most_affected_files'][bug.file_path] += 1
        
        # Critical bugs
        if bug.severity == 'critical':
            report['critical_bugs'].append({
                'file_path': bug.file_path,
                'line_number': bug.line_number,
                'description': bug.description,
                'type': bug.bug_type
            })
    
    # Process language statistics
    for stat in language_stats:
        lang_name = stat.language
        file_count = stat.file_count
        bug_count = stat.bug_count
        
        # Calculate bug density per file
        bug_density = bug_count / file_count if file_count > 0 else 0
        
        report['language_breakdown'][lang_name] = {
            'count': file_count,
            'bugs': bug_count,
            'bug_density': round(bug_density, 2)
        }
    
    # Sort most affected files and get top 10
    sorted_files = sorted(report['most_affected_files'].items(), key=lambda x: x[1], reverse=True)
    report['most_affected_files'] = dict(sorted_files[:10])
    
    # Calculate overall bug density
    report['overall_bug_density'] = round(scan.total_bugs / scan.analyzed_files, 2) if scan.analyzed_files > 0 else 0
    
    logger.info(f"Report generated successfully for scan {scan.id}")
    
    return report
