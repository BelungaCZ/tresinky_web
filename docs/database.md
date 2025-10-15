# Database Documentation

## Overview
This document provides comprehensive documentation for the Třešinky Cetechovice web application database, including schema, operations, and maintenance procedures.

## 🗄️ Database Architecture

### Database Type
- **Type:** SQLite
- **Location:** `instance/tresinky.db`
- **ORM:** Flask-SQLAlchemy
- **Size:** ~32KB (current data)
- **Encoding:** UTF-8

### Connection Configuration
```python
# Database URL
DATABASE_URL = "sqlite:///instance/tresinky.db"

# SQLAlchemy configuration
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

## 📊 Database Schema

### Tables Overview
| Table Name | Purpose | Records | Size |
|------------|---------|---------|------|
| `contact_message` | Contact form submissions | ~50 | ~8KB |
| `gallery_image` | Image metadata | ~200 | ~24KB |

### Table Details

#### contact_message
Stores contact form submissions from website visitors.

```sql
CREATE TABLE contact_message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
- `id` - Primary key (INTEGER, AUTOINCREMENT)
- `name` - Contact person name (VARCHAR(100), NOT NULL)
- `email` - Contact email address (VARCHAR(120), NOT NULL)
- `message` - Contact message content (TEXT, NOT NULL)
- `timestamp` - Submission timestamp (DATETIME, DEFAULT CURRENT_TIMESTAMP)

**Indexes:**
- Primary key on `id`
- No additional indexes (small table)

#### gallery_image
Stores metadata for gallery images and albums.

```sql
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

**Columns:**
- `id` - Primary key (INTEGER, AUTOINCREMENT)
- `filename` - Image filename (VARCHAR(255), NOT NULL)
- `title` - Image title (VARCHAR(255), NULLABLE)
- `description` - Image description (TEXT, NULLABLE)
- `album` - Album name (VARCHAR(255), NULLABLE)
- `category` - Image category (VARCHAR(100), NULLABLE)
- `display_order` - Display order in album (INTEGER, DEFAULT 0)
- `created_at` - Creation timestamp (DATETIME, DEFAULT CURRENT_TIMESTAMP)
- `updated_at` - Last update timestamp (DATETIME, DEFAULT CURRENT_TIMESTAMP)

**Indexes:**
- Primary key on `id`
- Index on `album` for album queries
- Index on `category` for category filtering
- Index on `display_order` for sorting

## 🔧 Database Operations

### Model Definitions

#### ContactMessage Model
```python
class ContactMessage(db.Model):
    __tablename__ = 'contact_message'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContactMessage {self.name}>'
```

#### GalleryImage Model
```python
class GalleryImage(db.Model):
    __tablename__ = 'gallery_image'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    album = db.Column(db.String(255))
    category = db.Column(db.String(100))
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<GalleryImage {self.filename}>'
```

### Common Queries

#### Contact Messages
```python
# Get all contact messages
messages = ContactMessage.query.all()

# Get recent messages (last 30 days)
from datetime import datetime, timedelta
recent_messages = ContactMessage.query.filter(
    ContactMessage.timestamp >= datetime.utcnow() - timedelta(days=30)
).all()

# Get messages by email
user_messages = ContactMessage.query.filter_by(email='user@example.com').all()
```

#### Gallery Images
```python
# Get all images
images = GalleryImage.query.all()

# Get images by album
album_images = GalleryImage.query.filter_by(album='2023').all()

# Get images by category
category_images = GalleryImage.query.filter_by(category='nature').all()

# Get images ordered by display order
ordered_images = GalleryImage.query.order_by(GalleryImage.display_order).all()

# Get images by album, ordered by display order
album_ordered_images = GalleryImage.query.filter_by(album='2023').order_by(GalleryImage.display_order).all()
```

### Database Initialization

#### Create Tables
```python
# Initialize database
from app import app, db

with app.app_context():
    db.create_all()
    print("Database tables created successfully")
```

#### Verify Tables
```python
# Check if tables exist
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("Available tables:", tables)
```

## 🔄 Database Maintenance

### Backup Procedures

#### Manual Backup
```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d_%H%M%S)

# Backup database
cp instance/tresinky.db backups/$(date +%Y%m%d_%H%M%S)/tresinky_backup.db

# Verify backup
sqlite3 backups/$(date +%Y%m%d_%H%M%S)/tresinky_backup.db ".tables"
```

#### Automated Backup Script
```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
DB_FILE="instance/tresinky.db"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
cp "$DB_FILE" "$BACKUP_DIR/tresinky_backup.db"

# Compress backup
gzip "$BACKUP_DIR/tresinky_backup.db"

# Remove old backups (keep last 30 days)
find backups/ -name "*.db.gz" -mtime +30 -delete

echo "Database backup completed: $BACKUP_DIR/tresinky_backup.db.gz"
```

### Restore Procedures

#### Restore from Backup
```bash
# Stop application
docker compose down

# Restore database
cp backups/YYYYMMDD_HHMMSS/tresinky_backup.db instance/tresinky.db

# Fix permissions
chmod 664 instance/tresinky.db
chown www-data:www-data instance/tresinky.db

# Start application
docker compose up -d
```

#### Restore from Compressed Backup
```bash
# Decompress backup
gunzip backups/YYYYMMDD_HHMMSS/tresinky_backup.db.gz

# Restore database
cp backups/YYYYMMDD_HHMMSS/tresinky_backup.db instance/tresinky.db

# Fix permissions
chmod 664 instance/tresinky.db
chown www-data:www-data instance/tresinky.db
```

### Database Optimization

#### Vacuum Database
```sql
-- Optimize database
VACUUM;

-- Analyze tables for query optimization
ANALYZE;
```

#### Reindex Database
```sql
-- Rebuild all indexes
REINDEX;
```

#### Check Database Integrity
```sql
-- Check database integrity
PRAGMA integrity_check;

-- Check foreign key constraints
PRAGMA foreign_key_check;
```

## 📊 Performance Monitoring

### Query Performance

#### Enable Query Logging
```python
# Add to app configuration
SQLALCHEMY_ECHO = True  # Log all SQL queries
```

#### Monitor Slow Queries
```python
# Add query timing
import time
from functools import wraps

def time_query(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Query took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

# Use decorator on database functions
@time_query
def get_gallery_images():
    return GalleryImage.query.all()
```

### Database Statistics

#### Table Statistics
```sql
-- Get table sizes
SELECT name, 
       (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=t.name) as row_count
FROM sqlite_master t 
WHERE type='table';

-- Get database size
SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();
```

#### Index Usage
```sql
-- Check index usage
EXPLAIN QUERY PLAN SELECT * FROM gallery_image WHERE album = '2023';

-- List all indexes
SELECT name, sql FROM sqlite_master WHERE type='index';
```

## 🚨 Troubleshooting

### Common Issues

#### Database Locked
```bash
# Check for locked database
lsof instance/tresinky.db

# Kill processes using database
sudo fuser -k instance/tresinky.db

# Restart application
docker compose restart web
```

#### Corrupted Database
```bash
# Check database integrity
sqlite3 instance/tresinky.db "PRAGMA integrity_check;"

# Repair database
sqlite3 instance/tresinky.db ".recover" | sqlite3 instance/tresinky_recovered.db
mv instance/tresinky_recovered.db instance/tresinky.db
```

#### Permission Issues
```bash
# Fix database permissions
chmod 664 instance/tresinky.db
chown www-data:www-data instance/tresinky.db

# Fix directory permissions
chmod 755 instance/
chown www-data:www-data instance/
```

### Performance Issues

#### Slow Queries
```python
# Add indexes for common queries
db.Index('idx_gallery_album', GalleryImage.album)
db.Index('idx_gallery_category', GalleryImage.category)
db.Index('idx_gallery_display_order', GalleryImage.display_order)
```

#### Memory Usage
```python
# Configure connection pooling
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 120,
    'pool_pre_ping': True
}
```

## 📚 Migration Procedures

### Schema Migrations

#### Add New Column
```python
# Add new column to existing table
from sqlalchemy import text

def add_column():
    with app.app_context():
        db.engine.execute(text('''
            ALTER TABLE gallery_image 
            ADD COLUMN new_field VARCHAR(255)
        '''))
        print("Column added successfully")
```

#### Create New Table
```python
# Create new table
def create_new_table():
    with app.app_context():
        db.engine.execute(text('''
            CREATE TABLE new_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        '''))
        print("Table created successfully")
```

### Data Migrations

#### Migrate Data
```python
# Migrate data between tables
def migrate_data():
    with app.app_context():
        # Get old data
        old_data = db.session.execute(text('SELECT * FROM old_table')).fetchall()
        
        # Insert into new table
        for row in old_data:
            db.session.execute(text('''
                INSERT INTO new_table (name, created_at) 
                VALUES (:name, :created_at)
            '''), {
                'name': row.name,
                'created_at': row.created_at
            })
        
        db.session.commit()
        print("Data migration completed")
```

## 📈 Monitoring & Alerts

### Database Health Checks
```python
# Health check function
def check_database_health():
    try:
        with app.app_context():
            # Test connection
            db.session.execute(text('SELECT 1'))
            
            # Check table counts
            contact_count = ContactMessage.query.count()
            gallery_count = GalleryImage.query.count()
            
            return {
                'status': 'healthy',
                'contact_messages': contact_count,
                'gallery_images': gallery_count
            }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }
```

### Automated Monitoring
```bash
#!/bin/bash
# monitor_database.sh

# Check database health
python3 -c "
from app import app, db
with app.app_context():
    try:
        db.session.execute('SELECT 1')
        print('Database: OK')
    except Exception as e:
        print('Database: ERROR -', e)
"

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage: WARNING ($DISK_USAGE%)"
else
    echo "Disk usage: OK ($DISK_USAGE%)"
fi
```

## 📚 Additional Resources

### Documentation
- [Environment Setup](environment_setup.md) - Database setup
- [Deployment Guide](deployment_guide.md) - Production database
- [Migration Instructions](MIGRATION_INSTRUCTIONS.md) - Database migrations

### Tools
- **SQLite Browser** - GUI for database management
- **DB Browser for SQLite** - Cross-platform database browser
- **sqlite3 CLI** - Command-line interface

### Support
- Check database logs for error details
- Review application logs for database issues
- Contact development team for complex database problems

---

*Last updated: [Current Date]*
*Next review: [Next Review Date]*