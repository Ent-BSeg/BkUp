from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with backup projects
    backup_projects = db.relationship('BackupProject', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class BackupProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    folder_name = db.Column(db.String(255), nullable=False)
    container_names = db.Column(db.Text, nullable=False)  # Comma-separated container names
    source_path = db.Column(db.String(255), nullable=False)
    destination_path = db.Column(db.String(255), nullable=False)
    run_time = db.Column(db.String(50), nullable=False)  # Time in HH:MM format
    service_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_backup = db.Column(db.DateTime, nullable=True)
    
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Get container names as a list
    @property
    def containers_list(self):
        if not self.container_names:
            return []
        return [c.strip() for c in self.container_names.split(',') if c.strip()]
    
    def __repr__(self):
        return f'<BackupProject {self.project_name}>'
