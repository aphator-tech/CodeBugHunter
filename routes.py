import os
import logging
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import db
from models import Repository, Scan, Bug, LanguageStats
from services.repository import clone_repository, get_repository_name, cleanup_repository
from services.analyzer import analyze_repository
from services.report_generator import generate_report
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def register_routes(app):
    @app.route('/')
    def index():
        # Get recent scans
        recent_scans = Scan.query.order_by(Scan.timestamp.desc()).limit(5).all()
        return render_template('index.html', recent_scans=recent_scans)
    
    @app.route('/analyze', methods=['POST'])
    def analyze():
        repo_url = request.form.get('repo_url', '').strip()
        
        # Validate repository URL
        if not repo_url:
            flash('Please enter a repository URL', 'danger')
            return redirect(url_for('index'))
        
        # Check if valid GitHub URL
        parsed_url = urlparse(repo_url)
        if not (parsed_url.netloc == 'github.com' or parsed_url.netloc == 'www.github.com'):
            flash('Only GitHub repositories are supported at this time', 'danger')
            return redirect(url_for('index'))
        
        try:
            # Check if repository already exists
            repo = Repository.query.filter_by(url=repo_url).first()
            if not repo:
                repo_name = get_repository_name(repo_url)
                repo = Repository(url=repo_url, name=repo_name, status='pending')
                db.session.add(repo)
                db.session.commit()
            
            # Create a new scan
            scan = Scan(repository_id=repo.id)
            db.session.add(scan)
            db.session.commit()
            
            # Clone repository
            repo.status = 'analyzing'
            db.session.commit()
            
            repo_path = clone_repository(repo_url, os.path.join(app.config["REPO_TEMP_DIR"], str(repo.id)))
            
            # Analyze repository
            result = analyze_repository(repo_path, scan.id)
            
            # Update scan with results
            scan.total_files = result['total_files']
            scan.analyzed_files = result['analyzed_files']
            scan.total_bugs = result['total_bugs']
            
            # Update repository status
            repo.status = 'completed'
            repo.last_analyzed = scan.timestamp
            db.session.commit()
            
            # Clean up repository
            cleanup_repository(repo_path)
            
            # Redirect to results page
            return redirect(url_for('results', scan_id=scan.id))
            
        except Exception as e:
            logger.error(f"Error analyzing repository: {str(e)}")
            flash(f'Error analyzing repository: {str(e)}', 'danger')
            
            # Update repository status to failed
            if repo:
                repo.status = 'failed'
                db.session.commit()
                
            return redirect(url_for('index'))
    
    @app.route('/results/<int:scan_id>')
    def results(scan_id):
        scan = Scan.query.get_or_404(scan_id)
        repo = Repository.query.get(scan.repository_id)
        
        # Get bugs with pagination
        page = request.args.get('page', 1, type=int)
        bugs_per_page = 20
        bugs = Bug.query.filter_by(scan_id=scan_id).paginate(page=page, per_page=bugs_per_page, error_out=False)
        
        # Get language statistics
        language_stats = LanguageStats.query.filter_by(scan_id=scan_id).all()
        
        # Generate summary report
        report = generate_report(scan, bugs.items, language_stats)
        
        return render_template('results.html', 
                              scan=scan, 
                              repo=repo, 
                              bugs=bugs, 
                              language_stats=language_stats,
                              report=report)
    
    @app.route('/api/scans')
    def api_scans():
        scans = Scan.query.order_by(Scan.timestamp.desc()).all()
        result = []
        for scan in scans:
            repo = Repository.query.get(scan.repository_id)
            result.append({
                'id': scan.id,
                'repository': repo.name,
                'url': repo.url,
                'timestamp': scan.timestamp.isoformat(),
                'total_bugs': scan.total_bugs,
                'total_files': scan.total_files
            })
        return jsonify(result)
    
    @app.route('/api/scan/<int:scan_id>/bugs')
    def api_scan_bugs(scan_id):
        bugs = Bug.query.filter_by(scan_id=scan_id).all()
        result = []
        for bug in bugs:
            result.append({
                'id': bug.id,
                'file_path': bug.file_path,
                'line_number': bug.line_number,
                'bug_type': bug.bug_type,
                'severity': bug.severity,
                'description': bug.description,
                'language': bug.language
            })
        return jsonify(result)
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error='404 - Page Not Found'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', error='500 - Internal Server Error'), 500
