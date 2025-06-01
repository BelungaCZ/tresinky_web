#!/bin/bash

# Log rotation script for gunicorn logs
# Keeps log file under 1MB

LOG_FILE="/app/logs/gunicorn.log"
MAX_SIZE=1048576  # 1MB in bytes

# Check if log file exists and get its size
if [ -f "$LOG_FILE" ]; then
    FILE_SIZE=$(stat -c%s "$LOG_FILE")
    
    # If file size exceeds 1MB, rotate it
    if [ $FILE_SIZE -gt $MAX_SIZE ]; then
        echo "$(date): Log file size ($FILE_SIZE bytes) exceeds 1MB. Rotating..."
        
        # Keep last 100 lines and create new log file
        tail -n 100 "$LOG_FILE" > "${LOG_FILE}.tmp"
        mv "${LOG_FILE}.tmp" "$LOG_FILE"
        
        # Send SIGUSR1 to gunicorn to reopen log files
        if [ -f "/tmp/gunicorn.pid" ]; then
            kill -USR1 $(cat /tmp/gunicorn.pid) 2>/dev/null || true
        fi
        
        echo "$(date): Log rotation completed"
    fi
fi 