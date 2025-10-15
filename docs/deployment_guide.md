# Deployment Guide

## Overview
This document provides comprehensive instructions for deploying the Třešinky Cetechovice web application to production environments.

## 🚀 Production Deployment

### Prerequisites
- **Ubuntu 20.04+** server with root access
- **Domain name** pointing to server IP
- **SSL certificate** (Let's Encrypt recommended)
- **Docker & Docker Compose** installed
- **Nginx** for reverse proxy

### Server Requirements
- **CPU:** 2+ cores
- **RAM:** 4GB+ (8GB recommended)
- **Storage:** 20GB+ SSD
- **Network:** 100Mbps+ connection

## 📋 Deployment Steps

### Step 1: Server Preparation

#### Update System
```bash
# Update package lists
sudo apt-get update && sudo apt-get upgrade -y

# Install essential packages
sudo apt-get install -y curl wget git unzip software-properties-common
```

#### Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.0.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker compose version
```

#### Install Nginx
```bash
# Install Nginx
sudo apt-get install -y nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

### Step 2: Application Deployment

#### Clone Repository
```bash
# Navigate to web directory
cd /var/www

# Clone repository
sudo git clone https://github.com/your-username/tresinky-web.git
sudo chown -R $USER:$USER tresinky-web
cd tresinky-web
```

#### Configure Environment
```bash
# Copy production configuration
cp .env.production .env

# Edit configuration
nano .env
```

#### Production Environment Variables
```bash
# .env.production
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key
DATABASE_URL=sqlite:///instance/tresinky.db
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=400000000
DEBUG=False
```

#### Initialize Database
```bash
# Create necessary directories
mkdir -p instance logs static/uploads

# Initialize database
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Step 3: Docker Configuration

#### Build Application
```bash
# Build Docker image
docker compose build

# Start application
docker compose up -d

# Check status
docker compose ps
```

#### Verify Application
```bash
# Check application logs
docker compose logs web

# Test application
curl -I http://localhost:5000
```

### Step 4: Nginx Configuration

#### Create Nginx Configuration
```bash
# Create site configuration
sudo nano /etc/nginx/sites-available/tresinky
```

#### Nginx Configuration
```nginx
# /etc/nginx/sites-available/tresinky
upstream web {
    server localhost:5000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Main application
    location / {
        proxy_pass http://web;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    # Static files
    location /static/ {
        alias /var/www/tresinky-web/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
        
        # Enable gzip compression
        gzip on;
        gzip_types text/css application/javascript image/svg+xml;
    }
    
    # Upload files
    location /uploads/ {
        alias /var/www/tresinky-web/static/uploads/;
        expires 30d;
        add_header Cache-Control "public";
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ \.(env|log|db)$ {
        deny all;
    }
}
```

#### Enable Site
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/tresinky /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 5: SSL Certificate

#### Install Certbot
```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx
```

#### Obtain SSL Certificate
```bash
# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

#### Setup Auto-Renewal
```bash
# Add to crontab
sudo crontab -e

# Add this line
0 12 * * * /usr/bin/certbot renew --quiet
```

### Step 6: Application Optimization

#### Configure Logging
```bash
# Create log rotation
sudo nano /etc/logrotate.d/tresinky
```

#### Log Rotation Configuration
```
/var/www/tresinky-web/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        docker compose restart web
    endscript
}
```

#### Setup Monitoring
```bash
# Install monitoring tools
sudo apt-get install -y htop iotop nethogs

# Create monitoring script
nano /var/www/tresinky-web/scripts/monitor.sh
```

#### Monitoring Script
```bash
#!/bin/bash
# monitor.sh

echo "=== System Status ==="
echo "Date: $(date)"
echo "Uptime: $(uptime)"
echo ""

echo "=== Docker Status ==="
docker compose ps
echo ""

echo "=== Application Status ==="
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://your-domain.com
echo ""

echo "=== Disk Usage ==="
df -h
echo ""

echo "=== Memory Usage ==="
free -h
echo ""

echo "=== Application Logs (Last 10 lines) ==="
tail -10 /var/www/tresinky-web/logs/app.log
```

#### Make Script Executable
```bash
chmod +x /var/www/tresinky-web/scripts/monitor.sh
```

## 🔄 Deployment Updates

### Update Process
```bash
# Navigate to application directory
cd /var/www/tresinky-web

# Pull latest changes
git pull origin main

# Backup database
cp instance/tresinky.db instance/tresinky_backup_$(date +%Y%m%d_%H%M%S).db

# Rebuild application
docker compose down
docker compose build
docker compose up -d

# Verify deployment
curl -I https://your-domain.com
```

### Rollback Process
```bash
# Stop application
docker compose down

# Restore previous version
git checkout HEAD~1

# Restore database backup
cp instance/tresinky_backup_YYYYMMDD_HHMMSS.db instance/tresinky.db

# Restart application
docker compose up -d
```

## 📊 Performance Optimization

### Nginx Optimization
```nginx
# Add to nginx configuration
worker_processes auto;
worker_connections 1024;

# Enable gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

# Enable caching
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|webp)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Docker Optimization
```yaml
# docker-compose.yml optimization
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

## 🚨 Security Configuration

### Firewall Setup
```bash
# Install UFW
sudo apt-get install -y ufw

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Application Security
```bash
# Set proper permissions
sudo chown -R www-data:www-data /var/www/tresinky-web
sudo chmod -R 755 /var/www/tresinky-web
sudo chmod 600 /var/www/tresinky-web/.env
sudo chmod 600 /var/www/tresinky-web/instance/tresinky.db
```

### Database Security
```bash
# Backup database regularly
sudo crontab -e

# Add backup job
0 2 * * * /var/www/tresinky-web/scripts/backup_database.sh
```

## 📈 Monitoring & Maintenance

### Health Checks
```bash
# Create health check script
nano /var/www/tresinky-web/scripts/health_check.sh
```

#### Health Check Script
```bash
#!/bin/bash
# health_check.sh

# Check application status
if curl -s -f https://your-domain.com > /dev/null; then
    echo "Application: OK"
else
    echo "Application: FAILED"
    # Send alert email
    echo "Application down at $(date)" | mail -s "Alert: Application Down" admin@your-domain.com
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage: WARNING ($DISK_USAGE%)"
else
    echo "Disk usage: OK ($DISK_USAGE%)"
fi

# Check memory usage
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEMORY_USAGE -gt 80 ]; then
    echo "Memory usage: WARNING ($MEMORY_USAGE%)"
else
    echo "Memory usage: OK ($MEMORY_USAGE%)"
fi
```

### Log Monitoring
```bash
# Monitor error logs
tail -f /var/www/tresinky-web/logs/errors.log

# Monitor application logs
tail -f /var/www/tresinky-web/logs/app.log

# Monitor Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🚨 Troubleshooting

### Common Issues

#### Application Not Starting
```bash
# Check Docker logs
docker compose logs web

# Check application status
docker compose ps

# Restart application
docker compose restart web
```

#### Database Issues
```bash
# Check database file
ls -la /var/www/tresinky-web/instance/tresinky.db

# Fix permissions
sudo chown www-data:www-data /var/www/tresinky-web/instance/tresinky.db
sudo chmod 664 /var/www/tresinky-web/instance/tresinky.db
```

#### Nginx Issues
```bash
# Check Nginx status
sudo systemctl status nginx

# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

#### SSL Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Test SSL
openssl s_client -connect your-domain.com:443
```

### Performance Issues

#### High Memory Usage
```bash
# Check memory usage
free -h
docker stats

# Restart application
docker compose restart web
```

#### High CPU Usage
```bash
# Check CPU usage
top
htop

# Check Docker resource usage
docker stats
```

#### Slow Response Times
```bash
# Check Nginx logs
sudo tail -f /var/log/nginx/access.log

# Test response time
curl -w "@curl-format.txt" -o /dev/null -s https://your-domain.com
```

## 📚 Additional Resources

### Documentation
- [Environment Setup](environment_setup.md) - Development environment
- [Database Documentation](database.md) - Database configuration
- [Performance Metrics](PERFORMANCE_METRICS.md) - Performance monitoring

### Scripts
- `scripts/setup_production.sh` - Production setup script
- `scripts/backup_database.sh` - Database backup script
- `scripts/monitor.sh` - System monitoring script

### Support
- Check application logs for error details
- Review system logs for infrastructure issues
- Contact development team for deployment support

---

*Last updated: [Current Date]*
*Next review: [Next Review Date]*