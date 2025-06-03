# Třešinky Cetechovice Web Application

## Overview
Web application for Třešinky Cetechovice, featuring a gallery, contact form, and donation system.
It should run faster than 90% other webpages on mobile devices. Speed is the key.

## Features
- Responsive design for all devices
- Maximum possible speed
- Image gallery with album support
- Contact form
- Donation system
- Admin interface for gallery management
- Support for multiple image formats (JPG, JPEG, PNG, WebP, HEIC)
- Support for video files (MP4)
- Automatic image optimization and WebP conversion
- Album management with automatic cleanup of empty directories

## 📚 Документация

### 🚀 Setup & Configuration
- **[Environment Setup](docs/environment_setup.md)** - Настройка окружения разработки и продакшена
- **[Deployment Guide](docs/deployment_guide.md)** - Полное руководство по деплою приложения

### 💻 Development  
- **[Implementation Plan](IMPLEMENTATION_PLAN.md)** - Детальный план реализации исправлений и улучшений
- **[Changelog](CHANGELOG.md)** - История изменений и обновлений проекта
- **[Database Documentation](docs/database.md)** - Подробная документация по базе данных

### 📋 Maintenance
- **[Changelog](CHANGELOG.md)** - Отслеживание версий и изменений
- **[Implementation Plan](IMPLEMENTATION_PLAN.md)** - Техническая документация по исправлениям

## Technical Details

### Site speed
- Using fast CSS
- HTTP/2
- Casching
- Small size

### Database
- **Type**: SQLite database
- **Location**: `instance/tresinky.db` (automatically created by Flask)
- **ORM**: Flask-SQLAlchemy
- **Size**: ~32KB with current data
- **Tables**:
  - `contact_message` - Contact form submissions (name, email, message, date)
  - `gallery_image` - Image metadata (filename, title, description, dates, category, display_order)
- **Features**:
  - Automatic database initialization
  - Image metadata management
  - Contact form message storage
  - Database-filesystem synchronization
  - Comprehensive logging of all database operations
- **Development & Production**: Same SQLite configuration for both environments

### Image Processing
- Images are automatically resized and converted to WebP format
- Maintains 4:3 aspect ratio for gallery previews
- Supports multiple image formats:
  - JPG/JPEG
  - PNG
  - WebP
  - HEIC
- Video support for MP4 files
- Automatic cleanup of empty album directories

### Gallery Features
- Album-based organization
- Automatic album creation from directory uploads
- Image metadata support (title, description, date)
- Drag-and-drop upload support
- Progress indication during upload
- Real-time WebSocket updates during processing
- Responsive 4:3 aspect ratio previews
- Album management (create, edit, delete)
- Image management (edit, delete, move between albums)

### Admin Interface
- Gallery management at `/admin/gallery`
- Image upload at `/admin/upload`
- Image editing with metadata support
- Album selection and creation
- Bulk operations support
- Real-time upload progress

## Setup

### Prerequisites
- Python 3.8+
- ImageMagick
- heif-convert (for HEIC support)

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make the image processing script executable:
   ```bash
   chmod +x scripts/process_image.sh
   ```

### Configuration
- **Database**: SQLite automatically initialized in `instance/tresinky.db`
- **Environment**: Set via `.env` files (development/production)
- **Static files**: Configured for gallery, uploads, and cache directories
- **Upload limits**: 400MB max file size configured
- **Logging**: Comprehensive logging system in `logs/` directory

## Usage

### Gallery Management
1. Access admin interface at `/admin/gallery`
2. Upload images through `/admin/upload`
3. Edit images and metadata
4. Move images between albums
5. Delete images or entire albums

### Image Upload
1. Select or create an album
2. Upload images or entire directories
3. Add metadata (optional)
4. Monitor upload progress
5. Images are automatically processed and optimized

### Album Management
- Albums are created automatically from directory uploads
- Empty albums are automatically removed
- Images can be moved between albums
- Album names are preserved from directory names

## File Structure
```
static/
  ├── images/
  │   ├── gallery/     # Processed gallery images
  │   ├── hero/        # Hero images
  │   └── thumbnails/  # Thumbnail images
  ├── css/
  ├── js/
  └── uploads/        # Temporary upload directory
instance/
  └── tresinky.db     # SQLite database file
logs/
  ├── database.log    # Database operations log
  ├── upload.log      # File upload operations log
  ├── processing.log  # Image processing log
  └── errors.log      # Error log
```

## Development
- Follow PEP 8 guidelines
- Use type hints
- Document all functions and classes
- Test all new features

## Security
- Secure file upload handling
- Input validation
- CSRF protection
- File type verification

## Performance
- Automatic image optimization
- WebP conversion for better compression
- Responsive image loading
- Efficient database queries

## Maintenance
- Regular cleanup of temporary files
- Automatic removal of empty albums
- Database optimization
- Log monitoring

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[Your License Here] 

---

## 🔗 См. также

- **[Environment Setup](docs/environment_setup.md)** - Детальная настройка окружения для разработки и продакшена
- **[Deployment Guide](docs/deployment_guide.md)** - Пошаговое руководство по деплою
- **[Database Documentation](docs/database.md)** - Подробная документация по базе данных и структуре таблиц
- **[Implementation Plan](IMPLEMENTATION_PLAN.md)** - Техническая документация и план исправлений
- **[Changelog](CHANGELOG.md)** - История версий и обновлений проекта


