import os
import subprocess
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def check_rclone_config():
    """Check if rclone is configured with a Google Drive remote named 'gdrive'"""
    try:
        result = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True, check=True)
        remotes = result.stdout.strip().split('\n')
        
        # Check for gdrive: remote
        if 'gdrive:' in remotes:
            return True
        else:
            logger.warning("Google Drive remote 'gdrive:' not found in rclone configuration")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking rclone configuration: {e}")
        return False

def setup_rclone():
    """Instructions for setting up rclone with Google Drive"""
    instructions = """
    To set up rclone with Google Drive:
    
    1. Run 'rclone config' in the terminal
    2. Press 'n' for new remote
    3. Enter 'gdrive' as the name
    4. Select 'Google Drive' as the storage type
    5. Follow the prompts to authenticate with your Google account
    """
    return instructions

def validate_docker_container(container_name):
    """Check if a Docker container exists"""
    try:
        result = subprocess.run(["docker", "inspect", container_name], 
                                capture_output=True, text=True, check=False)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error validating Docker container: {e}")
        return False

def validate_directory(path):
    """Check if a directory exists and is readable"""
    try:
        return os.path.isdir(path) and os.access(path, os.R_OK)
    except Exception as e:
        logger.error(f"Error validating directory {path}: {e}")
        return False

def format_datetime(dt):
    """Format a datetime object for display"""
    if not dt:
        return "Never"
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_system_info():
    """Get system information for diagnostics"""
    info = {
        "python_version": subprocess.run(["python3", "--version"], capture_output=True, text=True).stdout.strip(),
        "rclone_version": subprocess.run(["rclone", "version"], capture_output=True, text=True).stdout.split('\n')[0],
        "docker_version": subprocess.run(["docker", "--version"], capture_output=True, text=True).stdout.strip(),
        "zip_version": subprocess.run(["zip", "--version"], capture_output=True, text=True).stdout.split('\n')[0]
    }
    return info
