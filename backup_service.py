import os
import subprocess
import logging
import time
from datetime import datetime
import shutil
from models import BackupProject
from app import db

logger = logging.getLogger(__name__)

class BackupService:
    """Service to manage the backup process for projects"""
    
    @staticmethod
    def create_service_file(project):
        """Create a systemd service file for the backup project"""
        service_name = f"{project.project_name}_Backup"
        service_content = f"""[Unit]
Description=Backup Service for {project.project_name}
After=network.target

[Service]
Type=oneshot
User=root
ExecStart=/usr/bin/python3 /app/backup_service.py execute {project.id}

[Install]
WantedBy=multi-user.target
"""
        
        # Create service file path
        service_file_path = f"/etc/systemd/system/{service_name}.service"
        
        try:
            # Write service file
            with open(service_file_path, 'w') as f:
                f.write(service_content)
            
            # Create timer file
            timer_content = f"""[Unit]
Description=Timer for {service_name}

[Timer]
OnCalendar=*-*-* {project.run_time}:00
Persistent=true

[Install]
WantedBy=timers.target
"""
            timer_file_path = f"/etc/systemd/system/{service_name}.timer"
            
            with open(timer_file_path, 'w') as f:
                f.write(timer_content)
            
            # Reload systemd
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            
            # Enable and start timer if service is enabled
            if project.service_enabled:
                subprocess.run(["systemctl", "enable", f"{service_name}.timer"], check=True)
                subprocess.run(["systemctl", "start", f"{service_name}.timer"], check=True)
                logger.info(f"Service {service_name} created and enabled successfully")
            else:
                logger.info(f"Service {service_name} created but not enabled")
                
            return True
            
        except Exception as e:
            logger.error(f"Error creating service file: {e}")
            return False
    
    @staticmethod
    def update_service(project):
        """Update an existing service file"""
        # First delete the old service
        BackupService.delete_service(project)
        
        # Then create a new one
        return BackupService.create_service_file(project)
    
    @staticmethod
    def delete_service(project):
        """Delete a service file for a backup project"""
        service_name = f"{project.project_name}_Backup"
        
        try:
            # Stop and disable the timer
            subprocess.run(["systemctl", "stop", f"{service_name}.timer"], check=False)
            subprocess.run(["systemctl", "disable", f"{service_name}.timer"], check=False)
            
            # Remove service and timer files
            timer_file = f"/etc/systemd/system/{service_name}.timer"
            service_file = f"/etc/systemd/system/{service_name}.service"
            
            if os.path.exists(timer_file):
                os.remove(timer_file)
            
            if os.path.exists(service_file):
                os.remove(service_file)
            
            # Reload systemd
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            logger.info(f"Service {service_name} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting service: {e}")
            return False
    
    @staticmethod
    def execute_backup(project_id):
        """Execute the backup process for a specific project"""
        from app import app
        
        with app.app_context():
            try:
                project = BackupProject.query.get(project_id)
                if not project:
                    logger.error(f"Project with ID {project_id} not found")
                    return False
                
                logger.info(f"Starting backup process for project: {project.project_name}")
                
                # 1. Stop containers
                container_list = project.containers_list
                for container in container_list:
                    logger.info(f"Stopping container: {container}")
                    subprocess.run(["docker", "stop", container], check=True)
                
                # 2. Create temporary backup directory if it doesn't exist
                temp_dir = "/BkUp"
                os.makedirs(temp_dir, exist_ok=True)
                
                # 3. Generate backup file name with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                backup_filename = f"{project.project_name}_Backup_{timestamp}"
                zip_path = f"{temp_dir}/{backup_filename}.zip"
                
                # 4. Create zip backup
                logger.info(f"Creating zip backup at: {zip_path}")
                subprocess.run(["zip", "-r", zip_path, project.source_path], check=True)
                
                # 5. Start containers
                for container in container_list:
                    logger.info(f"Starting container: {container}")
                    subprocess.run(["docker", "start", container], check=True)
                
                # 6. Upload to Google Drive using rclone
                logger.info(f"Uploading backup to Google Drive: {project.destination_path}")
                dest_path = project.destination_path.rstrip('/')
                subprocess.run(["rclone", "copy", zip_path, f"gdrive:{dest_path}/"], check=True)
                
                # 7. Update the last backup time
                project.last_backup = datetime.utcnow()
                db.session.commit()
                
                # 8. Cleanup temporary zip file
                os.remove(zip_path)
                
                logger.info(f"Backup completed successfully for project: {project.project_name}")
                return True
                
            except Exception as e:
                logger.error(f"Error executing backup: {e}")
                # Try to start containers in case of failure
                try:
                    project = BackupProject.query.get(project_id)
                    container_list = project.containers_list
                    for container in container_list:
                        subprocess.run(["docker", "start", container], check=False)
                except:
                    pass
                return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python backup_service.py execute <project_id>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "execute" and len(sys.argv) == 3:
        project_id = int(sys.argv[2])
        success = BackupService.execute_backup(project_id)
        sys.exit(0 if success else 1)
    else:
        print("Invalid command. Available commands: execute <project_id>")
        sys.exit(1)
