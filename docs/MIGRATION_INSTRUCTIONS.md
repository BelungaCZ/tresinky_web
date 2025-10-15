# Migration Instructions

## Overview
This document provides detailed instructions for migrating the Třešinky Cetechovice web application database and configuration between different environments and versions.

## 🚨 Important Notes

### Before Starting Migration
- **Always backup your data** before starting any migration
- **Test migrations in development** before applying to production
- **Verify all dependencies** are installed and up to date
- **Check disk space** to ensure sufficient space for backups

### Migration Prerequisites
- Python 3.8+ installed
- Database access permissions
- Backup storage available
- Migration scripts executable

## 📋 Database Migrations

### Production Database Issues
If you encounter database errors like `no such table: album` on production, use the automated migration script:

```bash
# On production server
./scripts/migrate_database.sh
```

The script will:
- Create a backup of the existing database
- Check for missing tables
- Create missing tables safely
- Test all database operations
- Provide detailed migration report

### Manual Database Migration

#### Step 1: Backup Existing Database
```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d_%H%M%S)

# Backup database
cp instance/tresinky.db backups/$(date +%Y%m%d_%H%M%S)/tresinky_backup.db

# Verify backup
sqlite3 backups/$(date +%Y%m%d_%H%M%S)/tresinky_backup.db ".tables"
```

#### Step 2: Connect to Web Container
```bash
# Connect to web container
docker compose exec web bash

# Start Python shell
python3
```

#### Step 3: Run Migration
```python
# In Python shell
from app import app, db
with app.app_context():
    # Create all tables
    db.create_all()
    print("Tables created successfully")
    
    # Verify tables exist
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("Available tables:", tables)
```

#### Step 4: Verify Migration
```python
# Test database operations
from app import app, db, GalleryImage, ContactMessage
with app.app_context():
    # Test GalleryImage table
    try:
        count = GalleryImage.query.count()
        print(f"GalleryImage records: {count}")
    except Exception as e:
        print(f"GalleryImage error: {e}")
    
    # Test ContactMessage table
    try:
        count = ContactMessage.query.count()
        print(f"ContactMessage records: {count}")
    except Exception as e:
        print(f"ContactMessage error: {e}")
```

### Database Schema Migration

#### Current Schema
```sql
-- Contact messages table
CREATE TABLE contact_message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Gallery images table
CREATE TABLE gallery_image (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    description TEXT,
    album VARCHAR(255),
    category VARCHAR(100),
    display_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Migration Script
```python
# migration_script.py
from app import app, db
from sqlalchemy import text

def migrate_database():
    with app.app_context():
        try:
            # Check if tables exist
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            # Create contact_message table if not exists
            if 'contact_message' not in existing_tables:
                db.engine.execute(text('''
                    CREATE TABLE contact_message (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(120) NOT NULL,
                        message TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                '''))
                print("Created contact_message table")
            
            # Create gallery_image table if not exists
            if 'gallery_image' not in existing_tables:
                db.engine.execute(text('''
                    CREATE TABLE gallery_image (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename VARCHAR(255) NOT NULL,
                        title VARCHAR(255),
                        description TEXT,
                        album VARCHAR(255),
                        category VARCHAR(100),
                        display_order INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                '''))
                print("Created gallery_image table")
            
            print("Migration completed successfully")
            
        except Exception as e:
            print(f"Migration failed: {e}")
            raise

if __name__ == "__main__":
    migrate_database()
```

## 🔄 Environment Migrations

### Development to Production

#### Step 1: Prepare Development Environment
```bash
# Ensure all changes are committed
git add .
git commit -m "Prepare for production migration"

# Push to repository
git push origin main
```

#### Step 2: Update Production Code
```bash
# On production server
cd /root/Tresinky_web
git pull origin main
```

#### Step 3: Migrate Database
```bash
# Run migration script
./scripts/migrate_database.sh
```

#### Step 4: Restart Application
```bash
# Restart application
./rebuild.sh
```

#### Step 5: Verify Migration
```bash
# Check application status
curl -I http://localhost:5000

# Check database
sqlite3 instance/tresinky.db ".tables"
```

### Production to Development

#### Step 1: Export Production Database
```bash
# On production server
scp instance/tresinky.db user@dev-server:/path/to/dev/instance/
```

#### Step 2: Import to Development
```bash
# On development server
cp /path/to/prod/tresinky.db instance/tresinky.db
```

#### Step 3: Update Development Code
```bash
# Pull latest changes
git pull origin main
```

#### Step 4: Test Development Environment
```bash
# Start development server
python3 app.py

# Test functionality
curl http://localhost:5000/gallery
```

## 🔧 Configuration Migrations

### Environment Variables

#### Development Configuration
```bash
# .env.development
FLASK_ENV=development
SECRET_KEY=your-dev-secret-key
DATABASE_URL=sqlite:///instance/tresinky.db
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=400000000
```

#### Production Configuration
```bash
# .env.production
FLASK_ENV=production
SECRET_KEY=your-prod-secret-key
DATABASE_URL=sqlite:///instance/tresinky.db
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=400000000
```

### Nginx Configuration

#### Development Nginx
```nginx
# nginx.development.conf
server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://web:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Production Nginx
```nginx
# nginx.production.conf
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://web:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🚨 Troubleshooting

### Common Migration Issues

#### Database Connection Errors
```bash
# Check database file permissions
ls -la instance/tresinky.db

# Fix permissions if needed
chmod 664 instance/tresinky.db
chown www-data:www-data instance/tresinky.db
```

#### Table Creation Errors
```python
# Check if tables exist
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("Existing tables:", tables)
```

#### Import/Export Errors
```bash
# Check file integrity
sqlite3 instance/tresinky.db "PRAGMA integrity_check;"

# Repair if needed
sqlite3 instance/tresinky.db ".recover" | sqlite3 instance/tresinky_recovered.db
```

### Rollback Procedures

#### Database Rollback
```bash
# Stop application
docker compose down

# Restore backup
cp backups/YYYYMMDD_HHMMSS/tresinky_backup.db instance/tresinky.db

# Restart application
docker compose up -d
```

#### Configuration Rollback
```bash
# Restore previous configuration
git checkout HEAD~1 -- config/

# Restart application
./rebuild.sh
```

## 📊 Migration Verification

### Database Verification
```python
# verify_database.py
from app import app, db, GalleryImage, ContactMessage

def verify_database():
    with app.app_context():
        try:
            # Test GalleryImage operations
            gallery_count = GalleryImage.query.count()
            print(f"Gallery images: {gallery_count}")
            
            # Test ContactMessage operations
            contact_count = ContactMessage.query.count()
            print(f"Contact messages: {contact_count}")
            
            # Test database connection
            db.session.execute("SELECT 1")
            print("Database connection: OK")
            
            return True
        except Exception as e:
            print(f"Database verification failed: {e}")
            return False

if __name__ == "__main__":
    verify_database()
```

### Application Verification
```bash
# Test application endpoints
curl -I http://localhost:5000/
curl -I http://localhost:5000/gallery
curl -I http://localhost:5000/contact

# Check logs
tail -f logs/app.log
tail -f logs/database.log
```

## 📚 Additional Resources

### Documentation
- [Database Documentation](database.md) - Detailed database structure
- [Deployment Guide](deployment_guide.md) - Production deployment
- [Environment Setup](environment_setup.md) - Development setup

### Scripts
- `scripts/migrate_database.sh` - Automated database migration
- `scripts/backup_database.sh` - Database backup script
- `scripts/restore_database.sh` - Database restore script

### Support
- Check application logs for error details
- Review database logs for operation issues
- Contact development team for complex migrations

---

*Last updated: [Current Date]*
*Next review: [Next Review Date]*
