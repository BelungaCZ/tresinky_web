# Environment Setup

## Overview
This document provides detailed instructions for setting up the development and production environments for the Třešinky Cetechovice web application.

## 🚀 Development Environment

### Prerequisites
- **Python 3.8+** - Required for Flask application
- **Git** - For version control
- **Docker & Docker Compose** - For containerized development
- **ImageMagick** - For image processing
- **heif-convert** - For HEIC image support

### Installation Steps

#### 1. Clone Repository
```bash
git clone https://github.com/your-username/tresinky-web.git
cd tresinky-web
```

#### 2. Install Python Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Install System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install imagemagick heif-convert

# macOS
brew install imagemagick heif-convert

# CentOS/RHEL
sudo yum install ImageMagick heif-convert
```

#### 4. Configure Environment
```bash
# Copy environment template
cp .env.development .env

# Edit configuration
nano .env
```

#### 5. Initialize Database
```bash
# Create database directory
mkdir -p instance

# Initialize database
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

#### 6. Start Development Server
```bash
# Start application
python3 app.py

# Or use Docker
docker compose up -d
```

### Development Configuration

#### Environment Variables
```bash
# .env.development
FLASK_ENV=development
SECRET_KEY=your-development-secret-key
DATABASE_URL=sqlite:///instance/tresinky.db
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=400000000
DEBUG=True
```

#### Docker Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
      - ./instance:/app/instance
    environment:
      - FLASK_ENV=development
    depends_on:
      - db
  
  db:
    image: sqlite:latest
    volumes:
      - ./instance:/data
```

## 🏭 Production Environment

### Prerequisites
- **Ubuntu 20.04+** - Recommended server OS
- **Docker & Docker Compose** - For containerized deployment
- **Nginx** - For reverse proxy and SSL termination
- **SSL Certificate** - For HTTPS support
- **Domain Name** - For production access

### Installation Steps

#### 1. Server Setup
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.0.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Install Nginx
```bash
# Install Nginx
sudo apt-get install nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### 3. Deploy Application
```bash
# Clone repository
git clone https://github.com/your-username/tresinky-web.git
cd tresinky-web

# Copy production configuration
cp .env.production .env

# Start application
docker compose up -d
```

#### 4. Configure Nginx
```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/tresinky

# Enable site
sudo ln -s /etc/nginx/sites-available/tresinky /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. Setup SSL Certificate
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### Production Configuration

#### Environment Variables
```bash
# .env.production
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
DATABASE_URL=sqlite:///instance/tresinky.db
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=400000000
DEBUG=False
```

#### Nginx Configuration
```nginx
# /etc/nginx/sites-available/tresinky
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/your/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 🔧 Environment Management

### Switching Environments

#### Using Environment Scripts
```bash
# Switch to development
./scripts/switch_env.sh development

# Switch to production
./scripts/switch_env.sh production

# Check current environment
./scripts/switch_env.sh status
```

#### Manual Environment Switch
```bash
# Development
ln -sf .env.development .env
export FLASK_ENV=development

# Production
ln -sf .env.production .env
export FLASK_ENV=production
```

### Environment Validation

#### Check Environment Status
```bash
# Check Python version
python3 --version

# Check dependencies
pip list

# Check database
sqlite3 instance/tresinky.db ".tables"

# Check application
python3 -c "from app import app; print('App loaded successfully')"
```

#### Validate Configuration
```bash
# Check environment variables
python3 -c "
import os
from config.config import get_config
config = get_config()
print('Environment:', os.getenv('FLASK_ENV', 'development'))
print('Debug mode:', config.DEBUG)
print('Database URL:', config.DATABASE_URL)
"
```

## 🐳 Docker Development

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    imagemagick \
    heif-convert \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p instance logs static/uploads

# Set permissions
RUN chmod +x scripts/*.sh

# Expose port
EXPOSE 5000

# Start application
CMD ["python3", "app.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
      - ./instance:/app/instance
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=development
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf
      - ./static:/var/www/static
    depends_on:
      - web
    restart: unless-stopped
```

## 📊 Monitoring & Logging

### Application Logs
```bash
# View application logs
tail -f logs/app.log

# View database logs
tail -f logs/database.log

# View error logs
tail -f logs/errors.log
```

### System Monitoring
```bash
# Check Docker containers
docker ps

# Check application status
curl -I http://localhost:5000

# Check disk usage
df -h

# Check memory usage
free -h
```

## 🚨 Troubleshooting

### Common Issues

#### Python Version Issues
```bash
# Check Python version
python3 --version

# Install correct version
sudo apt-get install python3.9 python3.9-venv
```

#### Database Issues
```bash
# Check database file
ls -la instance/tresinky.db

# Fix permissions
chmod 664 instance/tresinky.db
chown $USER:$USER instance/tresinky.db
```

#### Docker Issues
```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Clean up containers
docker system prune -a
```

#### Nginx Issues
```bash
# Check Nginx status
sudo systemctl status nginx

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Performance Issues

#### Memory Usage
```bash
# Check memory usage
free -h

# Check Docker memory
docker stats

# Optimize memory usage
# Add swap file if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### Disk Space
```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a

# Clean up logs
sudo journalctl --vacuum-time=7d
```

## 📚 Additional Resources

### Documentation
- [Deployment Guide](deployment_guide.md) - Production deployment
- [Database Documentation](database.md) - Database setup
- [Performance Metrics](PERFORMANCE_METRICS.md) - Performance monitoring

### Scripts
- `scripts/setup_env.sh` - Environment setup script
- `scripts/switch_env.sh` - Environment switching script
- `scripts/backup_database.sh` - Database backup script

### Support
- Check application logs for error details
- Review system logs for infrastructure issues
- Contact development team for complex setup issues

---

*Last updated: [Current Date]*
*Next review: [Next Review Date]*