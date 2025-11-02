
# Database Documentation - Třešinky Cetechovice

🏠 [Main](../README.md) | 📋 [Changelog](../CHANGELOG.md) | 🚀 [Environment Setup](environment_setup.md) | 🌐 [Deployment Guide](deployment_guide.md)

---

## Overview

Třešinky Cetechovice web application uses **SQLite** database for storing image metadata and contact form submissions. The database provides persistent storage for gallery organization and user interactions.

## Database Configuration

### Location & Access

- **File**: `instance/tresinky.db` (automatically created by Flask)
- **Type**: SQLite 3
- **ORM**: Flask-SQLAlchemy
- **Size**: ~32KB with current data (85 images + contact messages)

### Environment Configuration

```python
# Development & Production
DATABASE_URL=sqlite:///tresinky.db

# Test Environment  
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
```

### Connection Settings

```python
# config/config.py
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///tresinky.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

## Database Schema

### GalleryImage Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique identifier |
| `filename` | VARCHAR(255) | NOT NULL | File path relative to static directory |
| `title` | VARCHAR(100) | | Image title/name |
| `description` | TEXT | | Image description |
| `date` | DATETIME | NOT NULL | Upload/processing date |
| `original_date` | DATETIME | | Original photo date (from EXIF) |
| `album_id` | INTEGER | FOREIGN KEY | Reference to album table |
| `category` | VARCHAR(100) | | Legacy field for migration (temporary) |
| `display_order` | INTEGER | DEFAULT 0 | Sorting order within album |

### Album Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique identifier |
| `normalized_name` | VARCHAR(100) | UNIQUE, NOT NULL | Name for filesystem (without diacritics) |
| `display_name` | VARCHAR(100) | NOT NULL | Name for user display (with diacritics) |
| `created_at` | DATETIME | DEFAULT NOW | Creation timestamp |
| `updated_at` | DATETIME | DEFAULT NOW | Last update timestamp |

**Example Records**:

```sql
-- Album table
(1, 'jarni_fotografie', 'Jarní fotografie', '2025-01-03 10:00:00', '2025-01-03 10:00:00')

-- GalleryImage table
(102, 'images/gallery/jarni_fotografie/photo_001.webp', 'Jarní fotografie', 'Beautiful spring scene', '2025-06-02 14:32:17', '2019-04-06 14:27:42', 1, NULL, 0)
```

## Database Operations

### Reading from Database

#### Get All Gallery Images

```python
# Get all images ordered by date
images = GalleryImage.query.order_by(desc(GalleryImage.date)).all()

# Get specific image by ID
image = GalleryImage.query.get_or_404(id)

# Count images in specific album
remaining_images = db.session.query(GalleryImage).filter(
    text("filename LIKE :pattern")
).params(pattern=f'%{album_name}%').count()
```

#### Synchronize Database with Filesystem

```python
def sync_gallery_with_disk():
    """Remove database entries for missing files"""
    db_images = GalleryImage.query.all()
    
    # Check if files exist on disk
    for db_image in db_images:
        if db_image.filename not in existing_files:
            db.session.delete(db_image)
    
    db.session.commit()
```

### Writing to Database

#### Save Contact Form Submission

```python
@app.route('/kontakt', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        db.session.add(message)
        db.session.commit()
        flash('Děkujeme za vaši zprávu!', 'success')
```

#### Add Gallery Image

```python
# Create new gallery image record
gallery_image = GalleryImage(
    filename=os.path.join('images', 'gallery', album_name, processed_filename),
    title=form.title.data or os.path.splitext(secure_name)[0],
    description=form.description.data,
    date=image_date,
    original_date=image_date,
    category=album_name
)

db.session.add(gallery_image)
db.session.commit()
```

#### Update Image Metadata

```python
@app.route('/admin/gallery/<int:id>/edit', methods=['GET', 'POST'])
def edit_image(id):
    image = GalleryImage.query.get_or_404(id)
    
    # Update properties
    image.title = form.title.data
    image.description = form.description.data
    image.display_order = form.display_order.data
    
    db.session.commit()
```

#### Delete Image

```python
@app.route('/admin/gallery/<int:id>/delete', methods=['POST'])
def delete_image(id):
    image = GalleryImage.query.get_or_404(id)
    
    # Delete file from filesystem
    file_path = os.path.join('static', image.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete from database
    db.session.delete(image)
    db.session.commit()
```

## Database Initialization

### Automatic Table Creation

```python
# In app.py - creates tables on startup
with app.app_context():
    try:
        db.create_all()
        app_logger.info("Database tables created/verified successfully")
    except Exception as db_error:
        log_exception(app_logger, db_error, 'creating database tables')
        exit(1)
```

### Manual Initialization Script

```python
# add_images_to_db.py
def add_images_to_db():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Process existing images in upload folder
        for filename in os.listdir(upload_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                # Create database entry for existing files
                existing = GalleryImage.query.filter_by(filename=filename).first()
                if not existing:
                    image = GalleryImage(...)
                    db.session.add(image)
        
        db.session.commit()
```

## Database Maintenance

### Logging System

All database operations are logged to `logs/database.log`:

```text
2025-06-03 11:50:16 - database - INFO - Added gallery image to session: photo.webp
2025-06-03 11:50:16 - database - INFO - Successfully committed single file to database: photo.jpg
```

### Database-Filesystem Synchronization

The system automatically:

- **Removes database records** for deleted image files
- **Cleans up empty albums** when last image is deleted
- **Maintains consistency** between database and filesystem

### Transaction Management

```python
try:
    db.session.add(gallery_image)
    db.session.commit()
    database_logger.info(f"Successfully committed: {filename}")
except Exception as commit_error:
    db.session.rollback()
    database_logger.error(f"Database error: {str(commit_error)}")
```

## Performance Considerations

### Query Optimization

- **Ordered queries**: `order_by(desc(GalleryImage.date))` for chronological display
- **Efficient filters**: Using SQLAlchemy `text()` for pattern matching
- **Lazy loading**: Database queries only when data is needed

### Database Size Management

- **Automatic cleanup**: Removes orphaned records during sync operations  
- **Efficient storage**: Only metadata stored in DB, not image files
- **Regular maintenance**: Database sync runs on gallery management access

## Testing Configuration

### Test Database

```python
# tests/conftest.py
@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()
```

### Test Data Management

- **In-memory database**: Tests use `sqlite:///:memory:`
- **Automatic cleanup**: Database recreated for each test
- **Isolated testing**: No interference with development data

---

## Database Migrations

### Production Migration Script

For production deployments where database tables are missing, use the automated migration script:

```bash
# On production server
./scripts/migrate_database.sh
```

#### What the migration script does

1. **Safety Checks**:
   - Verifies production environment
   - Checks if containers are running
   - Creates database backup before changes

2. **Table Creation**:
   - Checks existing tables (`contact_message`, `album`, `gallery_image`)
   - Creates missing tables using `db.create_all()`
   - Verifies all tables were created successfully

3. **Testing**:
   - Tests basic CRUD operations for all models
   - Verifies foreign key relationships
   - Cleans up test data after verification

4. **Backup Management**:
   - Creates timestamped backup in `backups/` directory
   - Preserves existing data before migration
   - Provides rollback capability if needed

#### Migration Output Example

```text
🗄️  Database Migration Script for Třešinky Cetechovice
==================================================
✅ Production environment detected
✅ Web container is running
📦 Creating database backup...
✅ Database file found, creating backup...
✅ Database backup created: backups/20250619_211500/tresinky.db.backup.20250619_211500

🔧 Starting database migration...
🔍 Checking existing tables...
❌ Table 'contact_message' missing
❌ Table 'album' missing
❌ Table 'gallery_image' missing

📊 Found 0 existing tables: 

🔧 Creating missing tables...
✅ All tables created successfully!
✅ Verified: Table 'contact_message' created
✅ Verified: Table 'album' created
✅ Verified: Table 'gallery_image' created

🧪 Testing database operations...
✅ ContactMessage operations: OK
✅ Album operations: OK
✅ GalleryImage operations: OK
✅ Test data cleaned up

✅ Database migration completed successfully!

📋 Migration Summary:
   - Database backup created in: backups/20250619_211500
   - All tables created/verified
   - Database operations tested

🎉 Application should now work correctly!
```

### Manual Migration (Alternative)

If the automated script fails, you can perform manual migration:

```bash
# Connect to web container
docker compose exec web bash

# Start Python shell
python3

# In Python shell:
from app import app, db
with app.app_context():
    db.create_all()
    print("Tables created successfully")
```

### Troubleshooting Migration Issues

#### Common Problems

1. **Permission Errors**:

   ```bash
   # Check file permissions
   docker compose exec web ls -la /app/instance/
   
   # Fix permissions if needed
   docker compose exec web chown -R 1000:1000 /app/instance/
   ```

2. **Container Not Running**:

   ```bash
   # Start containers
   docker compose up -d
   
   # Check status
   docker compose ps
   ```

3. **Database Locked**:

   ```bash
   # Restart web container
   docker compose restart web
   
   # Check for other processes
   docker compose exec web fuser /app/instance/tresinky.db
   ```

4. **Migration Script Errors**:

   ```bash
   # Check container logs
   docker compose logs web
   
   # Run with verbose output
   docker compose exec web python3 -v /tmp/migrate_db.py
   ```

#### Rollback Procedure

If migration fails and you need to restore from backup:

```bash
# Stop containers
docker compose down

# Restore database from backup
cp backups/YYYYMMDD_HHMMSS/tresinky.db.backup.YYYYMMDD_HHMMSS instance/tresinky.db

# Start containers
docker compose up -d

# Verify restoration
docker compose exec web python3 -c "
from app import app, db
with app.app_context():
    from sqlalchemy import text
    result = db.session.execute(text('SELECT name FROM sqlite_master WHERE type=\"table\"'))
    tables = [row[0] for row in result.fetchall()]
    print(f'Found tables: {tables}')
"
```

### Migration Best Practices

1. **Always Backup First**: The migration script automatically creates backups
2. **Test in Development**: Verify migration works in development environment first
3. **Monitor Logs**: Check application logs after migration for any errors
4. **Verify Functionality**: Test key features like gallery and contact form
5. **Keep Backups**: Don't delete backup files until you're confident everything works

### Migration History

| Date | Version | Changes | Status |
|------|---------|---------|--------|
| 2025-06-19 | 1.0 | Initial migration script | ✅ Complete |
| 2025-06-19 | 1.1 | Added Album table support | ✅ Complete |

---

## 🔗 Related Documentation

- **[README.md](../README.md)** - Main project overview
- **[Environment Setup](environment_setup.md)** - Development environment configuration
- **[Implementation Plan](../IMPLEMENTATION_PLAN.md)** - Current development status
- **[Changelog](../CHANGELOG.md)** - Version history and updates
