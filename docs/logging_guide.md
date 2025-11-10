# Tresinky Web Server - Logging Guide

This document provides comprehensive instructions for checking logs on the Tresinky web server running in production.

## Quick Start

Connect to the production server:

```bash
ssh tresinky@80.211.195.223
# or if you have SSH config set up:
ssh tresinky
```

## Container Status Check

Always start by checking the current status of all containers:

```bash
docker ps -a
```

## 1. Container Logs

### Flask App Logs (Main Application)

```bash
# Recent logs (last 50 lines)
docker logs --tail 50 tresinky_web-web-1

# Follow logs in real-time
docker logs -f tresinky_web-web-1

# Logs since specific time
docker logs --since 1h tresinky_web-web-1
docker logs --since "2025-08-26T07:00:00" tresinky_web-web-1

# All logs (use with caution - can be very long)
docker logs tresinky_web-web-1
```

### Nginx Proxy Logs

```bash
# Recent logs
docker logs --tail 50 nginx-proxy

# Follow logs in real-time
docker logs -f nginx-proxy

# Logs since specific time
docker logs --since 1h nginx-proxy
```

### Let's Encrypt SSL Logs

```bash
# Recent logs
docker logs --tail 50 nginx-letsencrypt

# Follow logs in real-time
docker logs -f nginx-letsencrypt

# Logs since specific time
docker logs --since 1h nginx-letsencrypt
```

## 2. Application-Specific Logs

### Flask App Internal Logs

```bash
# Gunicorn access logs (web server)
docker exec tresinky_web-web-1 tail -50 /app/logs/gunicorn.log

# Application logs (Flask app)
docker exec tresinky_web-web-1 tail -50 /app/logs/app.log

# Database logs
docker exec tresinky_web-web-1 tail -50 /app/logs/database.log

# Error logs
docker exec tresinky_web-web-1 tail -50 /app/logs/errors.log

# Validation logs
docker exec tresinky_web-web-1 tail -50 /app/logs/validation.log

# Processing logs
docker exec tresinky_web-web-1 tail -50 /app/logs/processing.log

# Upload logs
docker exec tresinky_web-web-1 tail -50 /app/logs/upload.log

# Performance logs
docker exec tresinky_web-web-1 tail -50 /app/logs/performance-history.log
```

### Nginx Internal Logs

```bash
# Access logs
docker exec nginx-proxy tail -50 /var/log/nginx/access.log

# Error logs
docker exec nginx-proxy tail -50 /var/log/nginx/error.log

# Check if logs exist
docker exec nginx-proxy ls -la /var/log/nginx/
```

## 3. Real-time Monitoring

### Follow Multiple Logs Simultaneously

```bash
# Watch all container logs in real-time (background processes)
docker logs -f tresinky_web-web-1 & 
docker logs -f nginx-proxy & 
docker logs -f nginx-letsencrypt

# Stop background processes
jobs
kill %1 %2 %3
```

### Follow Specific Log Files in Real-time

```bash
# Follow gunicorn logs
docker exec tresinky_web-web-1 tail -f /app/logs/gunicorn.log

# Follow application logs
docker exec tresinky_web-web-1 tail -f /app/logs/app.log

# Follow nginx access logs
docker exec nginx-proxy tail -f /var/log/nginx/access.log
```

## 4. Time-based Log Filtering

### Recent Activity

```bash
# Last hour
docker logs --since 1h tresinky_web-web-1

# Last 30 minutes
docker logs --since 30m tresinky_web-web-1

# Since specific date/time
docker logs --since "2025-08-26T07:00:00" tresinky_web-web-1
docker logs --since "2025-08-26" tresinky_web-web-1
```

### Specific Time Ranges

```bash
# Between two timestamps
docker logs --since "2025-08-26T07:00:00" --until "2025-08-26T08:00:00" tresinky_web-web-1
```

## 5. Log Analysis Commands

### Search for Specific Content

```bash
# Search for errors
docker logs tresinky_web-web-1 | grep -i "error"

# Search for warnings
docker logs tresinky_web-web-1 | grep -i "warning"

# Search for specific IP addresses
docker logs tresinky_web-web-1 | grep "85.163.140.109"

# Search for specific routes
docker logs tresinky_web-web-1 | grep "/gallery"
```

### Count and Statistics

```bash
# Count total log lines
docker logs tresinky_web-web-1 | wc -l

# Count errors
docker logs tresinky_web-web-1 | grep -c -i "error"

# Count successful requests
docker logs tresinky_web-web-1 | grep -c "200"
```

## 6. Quick Status Commands

### One-liner Status Check

```bash
docker ps && echo "--- Recent App Logs ---" && docker logs --tail 10 tresinky_web-web-1
```

### Container Health Check

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" && echo "--- Memory Usage ---" && docker stats --no-stream
```

### Log File Sizes

```bash
docker exec tresinky_web-web-1 du -h /app/logs/* && echo "--- Nginx Logs ---" && docker exec nginx-proxy du -h /var/log/nginx/*
```

## 7. Troubleshooting Commands

### Check for Common Issues

```bash
# Check for failed container starts
docker ps -a | grep -v "Up"

# Check for high memory usage
docker stats --no-stream

# Check disk space
df -h

# Check for port conflicts
netstat -tulpn | grep :80
netstat -tulpn | grep :443
netstat -tulpn | grep :5000
```

### Verify SSL Certificates

```bash
# Check SSL certificate status
docker exec nginx-proxy ls -la /etc/nginx/certs/

# Test SSL connection locally
curl -v -k https://localhost/
```

## 8. Log Rotation and Maintenance

### Check Log File Sizes

```bash
# Check all log file sizes
docker exec tresinky_web-web-1 find /app/logs -name "*.log" -exec ls -lh {} \;

# Check nginx log sizes
docker exec nginx-proxy find /var/log/nginx -name "*.log" -exec ls -lh {} \;
```

### Clean Old Logs (if needed)

```bash
# Clear specific log files (use with caution)
docker exec tresinky_web-web-1 truncate -s 0 /app/logs/app.log
docker exec tresinky_web-web-1 truncate -s 0 /app/logs/gunicorn.log
```

## 9. Advanced Monitoring

### Set up Continuous Monitoring

```bash
# Create a monitoring script
cat > monitor_logs.sh << 'EOF'
#!/bin/bash
while true; do
    echo "=== $(date) ==="
    docker logs --tail 5 tresinky_web-web-1
    echo "---"
    sleep 30
done
EOF

chmod +x monitor_logs.sh
./monitor_logs.sh
```

### Export Logs for Analysis

```bash
# Export logs to local machine
docker logs tresinky_web-web-1 > app_logs.txt
docker logs nginx-proxy > nginx_logs.txt

# Or copy specific log files
docker cp tresinky_web-web-1:/app/logs/app.log ./app.log
docker cp nginx-proxy:/var/log/nginx/access.log ./nginx_access.log
```

## 10. Common Log Patterns

### Successful Request Pattern

```text
2025-08-26 05:54:42 - app - INFO - Calling contact(method=GET)
2025-08-26 05:54:42 - app - INFO - Request URL: https://sad-tresinky-cetechovice.cz/kontakt
```

### Error Pattern

```text
2025-08-26 05:18:09 - app - WARNING - Dependency check failed: convert not found
```

### Database Operation Pattern

```text
2025-08-26 05:51:05 - database - INFO - Created new album: 2020 - Celkový přehled (2020)
```

## Notes

- **Container Names**: The main containers are `tresinky_web-web-1`, `nginx-proxy`, and `nginx-letsencrypt`
- **Log Locations**: Application logs are in `/app/logs/` inside the Flask container
- **Real-time Monitoring**: Use `Ctrl+C` to stop following logs
- **File Permissions**: Some log files may require root access to view
- **Log Rotation**: Logs are automatically managed by the application

## Emergency Commands

If the website is down or experiencing issues:

```bash
# Check container status
docker ps -a

# Restart containers
docker restart tresinky_web-web-1
docker restart nginx-proxy

# Check recent errors
docker logs --tail 100 tresinky_web-web-1 | grep -i "error\|exception\|fail"

# Verify website accessibility
curl -v https://sad-tresinky-cetechovice.cz/
```text
