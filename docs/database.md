🏠 [Главная](../README.md) | 📋 [Changelog](../CHANGELOG.md) | 🚀 [Environment Setup](environment_setup.md) | 🌐 [Deployment Guide](deployment_guide.md)

---

# Database Documentation - Třešinky Cetechovice

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

## Database Tables

### 1. Table: `contact_message`
**Purpose**: Stores contact form submissions from website visitors

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-incrementing unique identifier |
| `name` | VARCHAR(100) | NOT NULL | Sender's name |
| `email` | VARCHAR(120) | NOT NULL | Sender's email address |
| `message` | TEXT | NOT NULL | Message content |
| `date` | DATETIME | DEFAULT now() | Submission timestamp |

**Example Record**:
```sql
(1, 'Test User', 'test@example.com', 'Test message', '2025-06-03 13:01:03.703589')
```

### 2. Table: `gallery_image`
**Purpose**: Stores metadata for gallery images and albums organization

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-incrementing unique identifier |
| `filename` | VARCHAR(255) | NOT NULL | Relative path to image file |
| `title` | VARCHAR(100) | | Image title/name |
| `description` | TEXT | | Image description |
| `date` | DATETIME | NOT NULL | Upload/processing date |
| `original_date` | DATETIME | | Original photo date (from EXIF) |
| `category` | VARCHAR(100) | | Album/category name |
| `display_order` | INTEGER | DEFAULT 0 | Sorting order within album |

**Example Record**:
```sql
(102, 'images/gallery/2019_spring/photo_001.webp', '2019 Spring Photo', 'Beautiful spring scene', '2025-06-02 14:32:17', '2019-04-06 14:27:42', '2019_spring', 0)
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
```
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

## 🔗 Related Documentation

- **[README.md](../README.md)** - Main project overview
- **[Environment Setup](environment_setup.md)** - Development environment configuration
- **[Implementation Plan](../IMPLEMENTATION_PLAN.md)** - Current development status
- **[Changelog](../CHANGELOG.md)** - Version history and updates 