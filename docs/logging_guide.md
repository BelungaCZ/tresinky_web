# Logging Guide

## Overview
This document provides comprehensive guidance for the logging system in the Třešinky Cetechovice web application, including configuration, usage, and monitoring.

## 📋 Logging Architecture

### Log Files Structure
```
logs/
├── app.log          # Main application logs
├── database.log     # Database operation logs
├── errors.log       # Error and exception logs
├── processing.log   # Image processing logs
└── upload.log       # File upload logs
```

### Log Levels
- **DEBUG** - Detailed information for debugging
- **INFO** - General information about program execution
- **WARNING** - Something unexpected happened
- **ERROR** - Serious problem occurred
- **CRITICAL** - Very serious error occurred

## 🔧 Logging Configuration

### Centralized Logger Setup
```python
# utils/logger.py
import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, name, log_file, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Create file handler
        file_handler = logging.FileHandler(f'logs/{log_file}')
        file_handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def critical(self, message):
        self.logger.critical(message)

# Create logger instances
app_logger = Logger('app', 'app.log')
db_logger = Logger('database', 'database.log')
error_logger = Logger('errors', 'errors.log')
processing_logger = Logger('processing', 'processing.log')
upload_logger = Logger('upload', 'upload.log')
```

### Application Logging
```python
# app.py
from utils.logger import app_logger, db_logger, error_logger

@app.route('/')
def home():
    app_logger.info("Home page accessed")
    try:
        # Application logic
        return render_template('home.html')
    except Exception as e:
        error_logger.error(f"Error in home route: {str(e)}")
        return "Error occurred", 500
```

### Database Logging
```python
# Database operations
def log_database_operation(operation, table, details=None):
    db_logger.info(f"Database {operation} on {table}")
    if details:
        db_logger.debug(f"Details: {details}")

# Example usage
def create_contact_message(name, email, message):
    log_database_operation("INSERT", "contact_message", {
        "name": name,
        "email": email
    })
    
    message = ContactMessage(
        name=name,
        email=email,
        message=message
    )
    
    try:
        db.session.add(message)
        db.session.commit()
        db_logger.info("Contact message created successfully")
    except Exception as e:
        db_logger.error(f"Failed to create contact message: {str(e)}")
        raise
```

## 📊 Log Categories

### Application Logs (app.log)
**Purpose:** General application flow and user actions
**Level:** INFO, WARNING, ERROR

**Examples:**
```
2024-01-15 10:30:15 - app - INFO - Home page accessed
2024-01-15 10:30:20 - app - INFO - Gallery page accessed
2024-01-15 10:30:25 - app - WARNING - Slow response time: 2.5s
2024-01-15 10:30:30 - app - ERROR - Failed to load gallery images
```

### Database Logs (database.log)
**Purpose:** Database operations and queries
**Level:** DEBUG, INFO, ERROR

**Examples:**
```
2024-01-15 10:30:15 - database - INFO - Database INSERT on contact_message
2024-01-15 10:30:15 - database - DEBUG - Details: {'name': 'John Doe', 'email': 'john@example.com'}
2024-01-15 10:30:20 - database - INFO - Database SELECT on gallery_image
2024-01-15 10:30:20 - database - ERROR - Database connection failed: timeout
```

### Error Logs (errors.log)
**Purpose:** Exceptions and critical errors
**Level:** ERROR, CRITICAL

**Examples:**
```
2024-01-15 10:30:15 - errors - ERROR - Error in home route: division by zero
2024-01-15 10:30:20 - errors - CRITICAL - Database connection lost
2024-01-15 10:30:25 - errors - ERROR - File upload failed: disk full
```

### Processing Logs (processing.log)
**Purpose:** Image processing operations
**Level:** INFO, WARNING, ERROR

**Examples:**
```
2024-01-15 10:30:15 - processing - INFO - Processing image: photo.jpg
2024-01-15 10:30:16 - processing - INFO - Converted to WebP: photo.webp
2024-01-15 10:30:17 - processing - WARNING - Large image processed: 5MB
2024-01-15 10:30:18 - processing - ERROR - Image processing failed: invalid format
```

### Upload Logs (upload.log)
**Purpose:** File upload operations
**Level:** INFO, WARNING, ERROR

**Examples:**
```
2024-01-15 10:30:15 - upload - INFO - File upload started: photo.jpg
2024-01-15 10:30:16 - upload - INFO - File validation passed: photo.jpg
2024-01-15 10:30:17 - upload - WARNING - Large file uploaded: 10MB
2024-01-15 10:30:18 - upload - ERROR - Upload failed: file too large
```

## 🔍 Log Analysis

### Real-time Monitoring
```bash
# Monitor all logs
tail -f logs/*.log

# Monitor specific log
tail -f logs/app.log

# Monitor errors only
tail -f logs/errors.log

# Monitor with timestamps
tail -f logs/app.log | while read line; do echo "$(date): $line"; done
```

### Log Search and Filtering
```bash
# Search for specific errors
grep "ERROR" logs/*.log

# Search for specific user
grep "john@example.com" logs/*.log

# Search for specific time range
grep "2024-01-15 10:30" logs/*.log

# Count error occurrences
grep -c "ERROR" logs/*.log

# Search with context
grep -A 5 -B 5 "database connection" logs/*.log
```

### Log Statistics
```bash
# Count log entries by level
grep -c "INFO" logs/app.log
grep -c "WARNING" logs/app.log
grep -c "ERROR" logs/app.log

# Count database operations
grep -c "Database" logs/database.log

# Count uploads
grep -c "upload" logs/upload.log

# Count processing operations
grep -c "processing" logs/processing.log
```

## 📈 Performance Monitoring

### Response Time Logging
```python
# Add to app.py
import time
from functools import wraps

def log_response_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        response_time = end_time - start_time
        app_logger.info(f"Response time for {func.__name__}: {response_time:.4f}s")
        
        if response_time > 2.0:
            app_logger.warning(f"Slow response time: {response_time:.4f}s")
        
        return result
    return wrapper

# Use decorator
@log_response_time
@app.route('/gallery')
def gallery():
    # Gallery logic
    pass
```

### Memory Usage Logging
```python
# Add to app.py
import psutil
import os

def log_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / 1024 / 1024
    
    app_logger.info(f"Memory usage: {memory_mb:.2f} MB")
    
    if memory_mb > 500:  # 500MB threshold
        app_logger.warning(f"High memory usage: {memory_mb:.2f} MB")

# Call periodically
@app.before_request
def before_request():
    log_memory_usage()
```

## 🔄 Log Rotation

### Manual Log Rotation
```bash
# Create log rotation script
nano scripts/rotate_logs.sh
```

#### Log Rotation Script
```bash
#!/bin/bash
# rotate_logs.sh

LOG_DIR="logs"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$LOG_DIR/backups"

# Rotate logs
for log_file in "$LOG_DIR"/*.log; do
    if [ -f "$log_file" ]; then
        # Compress and move to backup
        gzip -c "$log_file" > "$LOG_DIR/backups/$(basename "$log_file")_$DATE.gz"
        
        # Clear current log
        > "$log_file"
        
        echo "Rotated: $log_file"
    fi
done

# Remove old backups (keep last 30 days)
find "$LOG_DIR/backups" -name "*.gz" -mtime +30 -delete

echo "Log rotation completed"
```

#### Make Script Executable
```bash
chmod +x scripts/rotate_logs.sh
```

### Automated Log Rotation
```bash
# Add to crontab
crontab -e

# Add log rotation job (daily at 2 AM)
0 2 * * * /path/to/tresinky-web/scripts/rotate_logs.sh
```

### System Log Rotation
```bash
# Create system logrotate configuration
sudo nano /etc/logrotate.d/tresinky
```

#### Logrotate Configuration
```
/path/to/tresinky-web/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        # Restart application to reopen log files
        docker compose restart web
    endscript
}
```

## 🚨 Error Monitoring

### Error Detection
```bash
# Monitor for critical errors
tail -f logs/errors.log | grep "CRITICAL"

# Monitor for database errors
tail -f logs/database.log | grep "ERROR"

# Monitor for upload errors
tail -f logs/upload.log | grep "ERROR"
```

### Error Alerting
```bash
# Create error alert script
nano scripts/error_alert.sh
```

#### Error Alert Script
```bash
#!/bin/bash
# error_alert.sh

ERROR_COUNT=$(grep -c "ERROR\|CRITICAL" logs/*.log | awk -F: '{sum+=$2} END {print sum}')

if [ "$ERROR_COUNT" -gt 10 ]; then
    echo "High error count detected: $ERROR_COUNT"
    # Send email alert
    echo "High error count: $ERROR_COUNT" | mail -s "Alert: High Error Count" admin@your-domain.com
fi
```

### Error Analysis
```bash
# Analyze error patterns
grep "ERROR" logs/*.log | cut -d' ' -f4- | sort | uniq -c | sort -nr

# Analyze error frequency by hour
grep "ERROR" logs/*.log | cut -d' ' -f2 | cut -d':' -f1 | sort | uniq -c

# Analyze error frequency by day
grep "ERROR" logs/*.log | cut -d' ' -f1 | sort | uniq -c
```

## 📊 Log Analytics

### Log Parsing Script
```python
# scripts/log_analyzer.py
import re
from collections import defaultdict
from datetime import datetime

def analyze_logs():
    log_files = [
        'logs/app.log',
        'logs/database.log',
        'logs/errors.log',
        'logs/processing.log',
        'logs/upload.log'
    ]
    
    stats = {
        'total_entries': 0,
        'error_count': 0,
        'warning_count': 0,
        'info_count': 0,
        'errors_by_type': defaultdict(int),
        'errors_by_hour': defaultdict(int)
    }
    
    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    stats['total_entries'] += 1
                    
                    if 'ERROR' in line:
                        stats['error_count'] += 1
                        # Extract error type
                        error_match = re.search(r'ERROR - (.+?):', line)
                        if error_match:
                            stats['errors_by_type'][error_match.group(1)] += 1
                        
                        # Extract hour
                        time_match = re.search(r'(\d{2}):\d{2}:\d{2}', line)
                        if time_match:
                            stats['errors_by_hour'][time_match.group(1)] += 1
                    
                    elif 'WARNING' in line:
                        stats['warning_count'] += 1
                    elif 'INFO' in line:
                        stats['info_count'] += 1
        
        except FileNotFoundError:
            print(f"Log file not found: {log_file}")
    
    return stats

if __name__ == "__main__":
    stats = analyze_logs()
    print("Log Analysis Results:")
    print(f"Total entries: {stats['total_entries']}")
    print(f"Errors: {stats['error_count']}")
    print(f"Warnings: {stats['warning_count']}")
    print(f"Info: {stats['info_count']}")
    print("\nTop error types:")
    for error_type, count in sorted(stats['errors_by_type'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {error_type}: {count}")
```

### Performance Metrics
```python
# scripts/performance_analyzer.py
import re
from collections import defaultdict

def analyze_performance():
    performance_data = []
    
    with open('logs/app.log', 'r') as f:
        for line in f:
            # Extract response times
            time_match = re.search(r'Response time for (\w+): ([\d.]+)s', line)
            if time_match:
                endpoint = time_match.group(1)
                response_time = float(time_match.group(2))
                performance_data.append((endpoint, response_time))
    
    # Calculate statistics
    endpoints = defaultdict(list)
    for endpoint, time in performance_data:
        endpoints[endpoint].append(time)
    
    print("Performance Analysis:")
    for endpoint, times in endpoints.items():
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        print(f"{endpoint}: avg={avg_time:.4f}s, max={max_time:.4f}s, min={min_time:.4f}s")

if __name__ == "__main__":
    analyze_performance()
```

## 🚨 Troubleshooting

### Common Log Issues

#### Log Files Not Created
```bash
# Check directory permissions
ls -la logs/

# Fix permissions
chmod 755 logs/
chown www-data:www-data logs/
```

#### Log Files Too Large
```bash
# Check file sizes
du -h logs/*.log

# Rotate large files
./scripts/rotate_logs.sh
```

#### Missing Log Entries
```python
# Check logger configuration
from utils.logger import app_logger
app_logger.info("Test log entry")
```

### Log Performance Issues

#### Slow Log Writing
```python
# Use async logging
import asyncio
import aiofiles

async def async_log(logger, level, message):
    async with aiofiles.open(f'logs/{logger}.log', 'a') as f:
        await f.write(f"{datetime.now()} - {level} - {message}\n")
```

#### High Disk Usage
```bash
# Monitor disk usage
df -h

# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete
```

## 📚 Additional Resources

### Documentation
- [Environment Setup](environment_setup.md) - Logging setup
- [Deployment Guide](deployment_guide.md) - Production logging
- [Database Documentation](database.md) - Database logging

### Tools
- **ELK Stack** - Elasticsearch, Logstash, Kibana
- **Fluentd** - Log collection and processing
- **Grafana** - Log visualization and monitoring

### Support
- Check log files for error details
- Review system logs for infrastructure issues
- Contact development team for logging support

---

*Last updated: [Current Date]*
*Next review: [Next Review Date]*