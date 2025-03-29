import os
import logging
from app import db
from models import Bug, LanguageStats
from services.repository import list_files
from services.language_detector import detect_language, analyze_language_stats
from analyzers.python_analyzer import analyze_python_file
from analyzers.javascript_analyzer import analyze_javascript_file
from analyzers.go_analyzer import analyze_go_file
from analyzers.common_analyzer import analyze_common_issues

logger = logging.getLogger(__name__)

def analyze_repository(repo_path, scan_id):
    """
    Analyze a repository for bugs and issues
    
    Args:
        repo_path (str): Path to the cloned repository
        scan_id (int): ID of the scan in the database
        
    Returns:
        dict: Analysis results with statistics
    """
    logger.info(f"Starting analysis of repository at {repo_path}")
    
    # List all files in the repository
    file_list = list_files(repo_path)
    
    # Language statistics
    language_stats = analyze_language_stats(repo_path, file_list)
    
    # Store language statistics
    for language, stats in language_stats.items():
        lang_stat = LanguageStats(
            scan_id=scan_id,
            language=language,
            file_count=stats['file_count'],
            line_count=stats['line_count'],
            bug_count=0  # Will be updated later
        )
        db.session.add(lang_stat)
    
    db.session.commit()
    
    # Initialize counters
    total_files = len(file_list)
    analyzed_files = 0
    total_bugs = 0
    
    # Analyze each file
    for file_path in file_list:
        analyzed_files += 1
        full_path = os.path.join(repo_path, file_path)
        
        if not os.path.isfile(full_path):
            continue
            
        language = detect_language(file_path)
        
        # Analyze file based on language
        bugs = []
        
        # Common analysis for all file types
        common_bugs = analyze_common_issues(full_path, file_path)
        bugs.extend(common_bugs)
        
        # Language-specific analysis
        if language == 'Python':
            python_bugs = analyze_python_file(full_path, file_path)
            bugs.extend(python_bugs)
        elif language in ['JavaScript', 'TypeScript', 'React', 'React TypeScript']:
            js_bugs = analyze_javascript_file(full_path, file_path)
            bugs.extend(js_bugs)
        elif language == 'Go':
            go_bugs = analyze_go_file(full_path, file_path)
            bugs.extend(go_bugs)
        
        # Save bugs to database
        for bug_info in bugs:
            bug = Bug(
                scan_id=scan_id,
                file_path=file_path,
                line_number=bug_info.get('line_number'),
                bug_type=bug_info.get('bug_type'),
                severity=bug_info.get('severity'),
                description=bug_info.get('description'),
                code_snippet=bug_info.get('code_snippet'),
                recommendation=bug_info.get('recommendation'),
                language=language
            )
            db.session.add(bug)
            total_bugs += 1
            
            # Update language statistics bug count
            lang_stat = LanguageStats.query.filter_by(scan_id=scan_id, language=language).first()
            if lang_stat:
                lang_stat.bug_count += 1
        
        # Commit bugs for this file
        db.session.commit()
    
    logger.info(f"Analysis completed: {analyzed_files}/{total_files} files analyzed, {total_bugs} bugs found")
    
    return {
        'total_files': total_files,
        'analyzed_files': analyzed_files,
        'total_bugs': total_bugs
    }
