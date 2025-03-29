from datetime import datetime
from app import db
from flask_login import UserMixin

class Repository(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))
    last_analyzed = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, analyzing, completed, failed
    
    # Relationship with scans
    scans = db.relationship('Scan', backref='repository', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Repository {self.url}>'

class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repository.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_files = db.Column(db.Integer, default=0)
    analyzed_files = db.Column(db.Integer, default=0)
    total_bugs = db.Column(db.Integer, default=0)
    
    # Relationship with bugs
    bugs = db.relationship('Bug', backref='scan', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Scan {self.id} for Repository {self.repository_id}>'

class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    line_number = db.Column(db.Integer)
    bug_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # critical, high, medium, low, info
    description = db.Column(db.Text, nullable=False)
    code_snippet = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    language = db.Column(db.String(30))
    
    def __repr__(self):
        return f'<Bug {self.id} in {self.file_path}>'

class LanguageStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), nullable=False)
    language = db.Column(db.String(30), nullable=False)
    file_count = db.Column(db.Integer, default=0)
    line_count = db.Column(db.Integer, default=0)
    bug_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<LanguageStats {self.language} for Scan {self.scan_id}>'
