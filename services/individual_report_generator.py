import os
import json
import logging
from datetime import datetime
from models import Bug, Repository

logger = logging.getLogger(__name__)

def ensure_repo_directory(repo_name):
    """
    Ensure the directory structure for a repository exists
    
    Args:
        repo_name (str): Repository name
        
    Returns:
        str: Path to the repository directory
    """
    # Sanitize repository name for use as a directory name
    safe_repo_name = repo_name.replace('/', '_').replace('\\', '_')
    
    # Create path
    repo_dir = os.path.join('results', safe_repo_name)
    
    # Create directory if it doesn't exist
    if not os.path.exists(repo_dir):
        os.makedirs(repo_dir)
        
    return repo_dir

def generate_individual_bug_reports(scan_id, repository):
    """
    Generate individual reports for each bug in a scan
    
    Args:
        scan_id (int): ID of the scan
        repository (Repository): Repository object
        
    Returns:
        int: Number of reports generated
    """
    logger.info(f"Generating individual bug reports for scan {scan_id}")
    
    # Create directory for repository
    repo_dir = ensure_repo_directory(repository.name)
    
    # Query bugs for this scan
    bugs = Bug.query.filter_by(scan_id=scan_id).all()
    
    # Generate report for each bug
    reports_generated = 0
    for bug in bugs:
        try:
            # Generate report
            report = generate_bug_report(bug, repository)
            
            # Create unique filename
            filename = f"bug_{bug.id}_{bug.bug_type.replace(' ', '_').lower()}.json"
            file_path = os.path.join(repo_dir, filename)
            
            # Write report to file
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
                
            reports_generated += 1
            
        except Exception as e:
            logger.error(f"Error generating individual report for bug {bug.id}: {str(e)}")
    
    logger.info(f"Generated {reports_generated} individual bug reports for scan {scan_id}")
    return reports_generated

def generate_bug_report(bug, repository):
    """
    Generate a detailed report for a single bug
    
    Args:
        bug (Bug): Bug object
        repository (Repository): Repository object
        
    Returns:
        dict: Report data
    """
    # Create CVSS-like severity score mapping
    severity_score_map = {
        'critical': {'score': '9.0-10.0', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H'},
        'high': {'score': '7.0-8.9', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'},
        'medium': {'score': '4.0-6.9', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L'},
        'low': {'score': '0.1-3.9', 'vector': 'CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:L/I:L/A:L'},
        'info': {'score': '0.0', 'vector': 'CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:N'}
    }
    
    # Get severity details
    severity_details = severity_score_map.get(bug.severity, severity_score_map['info'])
    
    # Generate report
    report = {
        "general_info": {
            "vulnerability_title": f"{bug.bug_type} in {os.path.basename(bug.file_path)}",
            "description": bug.description,
            "target": {
                "repository": repository.name,
                "repository_url": repository.url,
                "file_path": bug.file_path,
                "line_number": bug.line_number,
                "language": bug.language
            },
            "vulnerability_category": bug.bug_type,
            "timestamp": datetime.utcnow().isoformat()
        },
        "severity": {
            "level": bug.severity,
            "score": severity_details['score'],
            "vector": severity_details['vector']
        },
        "details": {
            "description": bug.description,
            "code_snippet": bug.code_snippet,
            "recommendation": bug.recommendation
        },
        "validation": {
            "steps": [
                f"1. Navigate to file {bug.file_path}",
                f"2. Go to line {bug.line_number}",
                f"3. Observe the problematic code: {bug.code_snippet and bug.code_snippet.splitlines()[0].strip() or 'N/A'}"
            ]
        }
    }
    
    return report