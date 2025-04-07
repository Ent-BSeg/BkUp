import os
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import app, db
from models import User, BackupProject
from forms import LoginForm, RegistrationForm, BackupProjectForm
from backup_service import BackupService
import logging

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Add current date to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)
    
    # Check if we need to show registration form for first user
    user_count = User.query.count()
    if user_count == 0:
        return redirect(url_for('register'))
    
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Only allow registration if no users exist (first time)
    user_count = User.query.count()
    if user_count > 0 and not current_user.is_authenticated:
        flash('Registration is disabled. Please contact an administrator.', 'danger')
        return redirect(url_for('login'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    projects = BackupProject.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', title='Dashboard', projects=projects)

@app.route('/project/create', methods=['GET', 'POST'])
@login_required
def create_project():
    form = BackupProjectForm()
    if form.validate_on_submit():
        project = BackupProject(
            project_name=form.project_name.data,
            folder_name=form.folder_name.data,
            container_names=form.container_names.data,
            source_path=form.source_path.data,
            destination_path=form.destination_path.data,
            run_time=form.run_time.data,
            service_enabled=form.service_enabled.data,
            user_id=current_user.id
        )
        
        db.session.add(project)
        db.session.commit()
        
        # Create system service if enabled
        if form.service_enabled.data:
            if BackupService.create_service_file(project):
                flash('Project created and service enabled successfully!', 'success')
            else:
                flash('Project created but failed to create service file. Check logs.', 'warning')
        else:
            flash('Project created successfully!', 'success')
        
        return redirect(url_for('dashboard'))
    
    return render_template('create_project.html', title='Create Backup Project', form=form)

@app.route('/project/<int:project_id>')
@login_required
def project_details(project_id):
    project = BackupProject.query.get_or_404(project_id)
    
    # Security check - only allow owner to view
    if project.user_id != current_user.id:
        flash('You do not have permission to view this project', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('project_details.html', title=project.project_name, project=project)

@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = BackupProject.query.get_or_404(project_id)
    
    # Security check - only allow owner to edit
    if project.user_id != current_user.id:
        flash('You do not have permission to edit this project', 'danger')
        return redirect(url_for('dashboard'))
    
    form = BackupProjectForm(obj=project)
    if form.validate_on_submit():
        project.project_name = form.project_name.data
        project.folder_name = form.folder_name.data
        project.container_names = form.container_names.data
        project.source_path = form.source_path.data
        project.destination_path = form.destination_path.data
        project.run_time = form.run_time.data
        
        # Check if service status changed
        service_changed = project.service_enabled != form.service_enabled.data
        project.service_enabled = form.service_enabled.data
        
        db.session.commit()
        
        # Update or create service if needed
        if service_changed:
            if project.service_enabled:
                if BackupService.create_service_file(project):
                    flash('Project updated and service enabled successfully!', 'success')
                else:
                    flash('Project updated but failed to create service. Check logs.', 'warning')
            else:
                if BackupService.delete_service(project):
                    flash('Project updated and service disabled successfully!', 'success')
                else:
                    flash('Project updated but failed to disable service. Check logs.', 'warning')
        else:
            # Service status didn't change, but we still need to update if it's enabled
            if project.service_enabled:
                if BackupService.update_service(project):
                    flash('Project and service updated successfully!', 'success')
                else:
                    flash('Project updated but failed to update service. Check logs.', 'warning')
            else:
                flash('Project updated successfully!', 'success')
        
        return redirect(url_for('project_details', project_id=project.id))
    
    return render_template('edit_project.html', title='Edit Project', form=form, project=project)

@app.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = BackupProject.query.get_or_404(project_id)
    
    # Security check - only allow owner to delete
    if project.user_id != current_user.id:
        flash('You do not have permission to delete this project', 'danger')
        return redirect(url_for('dashboard'))
    
    # Delete service file first if it exists
    if project.service_enabled:
        BackupService.delete_service(project)
    
    # Delete the project
    db.session.delete(project)
    db.session.commit()
    
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/project/<int:project_id>/run', methods=['POST'])
@login_required
def run_project(project_id):
    project = BackupProject.query.get_or_404(project_id)
    
    # Security check - only allow owner to run
    if project.user_id != current_user.id:
        flash('You do not have permission to run this project', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Execute backup
        if BackupService.execute_backup(project.id):
            flash('Backup executed successfully!', 'success')
        else:
            flash('Backup failed. Check logs for details.', 'danger')
    except Exception as e:
        logger.error(f"Error running backup: {e}")
        flash(f'Error running backup: {str(e)}', 'danger')
    
    return redirect(url_for('project_details', project_id=project.id))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
