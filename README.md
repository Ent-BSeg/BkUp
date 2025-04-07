# Docker Backup Manager

A comprehensive Docker-based backup management system for Ubuntu 24.04 that uses rclone and zip to automate containerized application backups to Google Drive.

## Features

- Web-based dashboard for managing backup projects
- User authentication system
- Schedule automated backups
- Support for backing up Docker containers
- Google Drive integration using rclone
- Systemd service integration
- PostgreSQL database for data storage

## System Requirements

- Ubuntu 24.04 (also works on Ubuntu 22.04)
- Docker and Docker Compose
- Internet connection for Google Drive backups

## Installation

Follow these steps to install the system:

1. Install Docker and Docker Compose
2. Clone this repository
3. Configure the environment variables
4. Build and start the containers
5. Configure rclone for Google Drive access
6. Access the web interface and create an admin account

## Usage

1. Register an admin account
2. Create backup projects with specific parameters:
   - Project Name
   - Folder Name
   - Container Names
   - Source Path
   - Destination Path (in Google Drive)
   - Backup Time Schedule
3. Enable/disable backup services
4. Manage existing backup projects

## Project Structure

- Flask web application for the front-end
- PostgreSQL database for data storage
- Docker containers for system isolation
- Systemd services for scheduled backups

## Docker Configuration

The system uses two containers:
1. Database container (PostgreSQL)
2. Application container (Python Flask)

## License

This project is licensed under the MIT License
