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
## Step-by-Step Guide: Deploying Your Backup System on Ubuntu 24.04
Here's a complete guide to download, set up, and access your backup system with two containers (db and sys) on Ubuntu 24.04.
### Part 1: Download the Project
1. **Install Git (if not already installed)**
   ```bash
   sudo apt update
   sudo apt install -y git
Create a directory for your project

mkdir -p ~/backup-system
cd ~/backup-system
Download the project files

git clone https://github.com/Ent-BSeg/BkUp.git .
Part 2: Prepare the Server
Install Docker and Docker Compose

# Update package index
sudo apt update
# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
# Add Docker's GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
# Update apt and install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# Verify Docker is working
sudo docker run hello-world
# Add current user to docker group (optional)
sudo usermod -aG docker $USER
Create the backup directory

sudo mkdir -p /BkUp
sudo chmod 777 /BkUp
Part 3: Set Up the Docker Configuration
Create docker-compose.yml

cat > docker-compose.yml << 'EOL'
version: '3'
services:
  db:
    image: postgres:15
    container_name: backup-db
    restart: unless-stopped
    environment:
      - POSTGRES_PASSWORD=StrongPassword123  # Change this!
      - POSTGRES_USER=postgres
      - POSTGRES_DB=backup_system
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - backup-network
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: backup-sys
    depends_on:
      - db
    ports:
      - "5000:5000"
    volumes:
      - .:/app
      - /var/run/docker.sock:/var/run/docker.sock
      - /etc/systemd/system:/etc/systemd/system
      - /BkUp:/BkUp
    environment:
      - TZ=UTC
      - DATABASE_URL=postgresql://postgres:StrongPassword123@db:5432/backup_system  # Use same password
      - SESSION_SECRET=YourSecretKey123456789  # Change this!
    restart: unless-stopped
    privileged: true
    networks:
      - backup-network
networks:
  backup-network:
    driver: bridge
volumes:
  postgres_data:
EOL
Create Dockerfile

cat > Dockerfile << 'EOL'
FROM ubuntu:24.04
# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    rclone \
    zip \
    systemd \
    curl \
    docker.io \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# Set up working directory
WORKDIR /app
# Copy requirements
COPY requirements.txt ./
# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt
# Copy application files
COPY . .
# Create backup directory
RUN mkdir -p /BkUp
# Expose port
EXPOSE 5000
# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--reuse-port", "--reload", "main:app"]
EOL
Create requirements.txt

cat > requirements.txt << 'EOL'
flask
flask-login
flask-sqlalchemy
flask-wtf
gunicorn
psycopg2-binary
sqlalchemy
werkzeug
wtforms
email-validator
EOL
Part 4: Build and Start the Containers
Build the containers

sudo docker-compose build
Start the containers

sudo docker-compose up -d
Verify the containers are running

sudo docker-compose ps
Part 5: Configure rclone for Google Drive Access
Access the app container

sudo docker exec -it backup-sys bash
Configure rclone

rclone config
Follow the interactive prompts to set up Google Drive

Select "n" for new remote
Enter a name (e.g., "gdrive")
Select Google Drive from the list (usually number 15)
Select "1" for full access to all files
Enter a client ID (or leave blank)
Enter a client secret (or leave blank)
Select "1" for global scope
Select "y" to auto config
Follow browser authentication steps
Select "y" to confirm the configuration
Exit the container

exit
Part 6: Access Your Backup System
Through the web browser

http://YOUR_SERVER_IP:5000
Replace YOUR_SERVER_IP with your actual server IP address.

Register an admin account

When you first access the system, you'll be prompted to create an admin account
Use a valid email address and a strong password
Part 7: Making the System Accessible via Domain Name (Optional)
Install Nginx

sudo apt update
sudo apt install -y nginx
Create Nginx configuration

sudo nano /etc/nginx/sites-available/backup-system
Add the following configuration

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
Replace your-domain.com with your actual domain name.

Enable the site

sudo ln -s /etc/nginx/sites-available/backup-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
Set up SSL with Let's Encrypt (recommended)

sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
Follow the prompts to complete the SSL certificate setup.

Part 8: System Maintenance
View container logs

sudo docker-compose logs -f
Restart the containers

sudo docker-compose restart
Update the application

# Pull latest changes from git
git pull
# Rebuild and restart containers
sudo docker-compose down
sudo docker-compose build
sudo docker-compose up -d
Backup the database

sudo docker exec -t backup-db pg_dumpall -c -U postgres > backup.sql
Restore the database

cat backup.sql | sudo docker exec -i backup-db psql -U postgres
Project Structure
Flask web application for the front-end
PostgreSQL database for data storage
Docker containers for system isolation
Systemd services for scheduled backups
License
This project is licensed under the MIT License

## Steps to Create Your GitHub Repository
1. Log in to your GitHub account
2. Click the "+" icon in the top-right corner and select "New repository"
3. Name your repository (e.g., "docker-backup-manager")
4. Add a description (optional)
5. Choose public or private visibility
6. Check "Add a README file"
7. Click "Create repository"
8. After creation, click on the README.md file
9. Click the pencil icon to edit
10. Replace all content with the markdown text I provided above
11. Click "Commit changes"
## Uploading Your Project Files
To upload the rest of your project files to GitHub:
1. Use the web interface:
   - Click "Add file" > "Upload files"
   - Drag and drop or select files from your computer
   - Commit the changes
2. Or use Git commands (from your local machine):
   ```bash
   # Clone the repository (after creating it on GitHub)
   git clone https://github.com/YOUR_USERNAME/docker-backup-manager.git
   cd docker-backup-manager
   
   # Copy your files into this directory
   # ...
   
   # Add all files
   git add .
   
   # Commit
   git commit -m "Add project files"
   
   # Push to GitHub
   git push
For the Docker Compose setup, make sure to include the docker-compose.yml and Dockerfile files in your repository. These are the most critical files for setting up the two containers (db and sys) as you requested.

