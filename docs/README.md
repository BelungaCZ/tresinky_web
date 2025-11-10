# Třešinky Cetechovice Web Application

## Overview
Web application for Třešinky Cetechovice, featuring a gallery, contact form, and donation system.
It should run faster than 90% of other webpages on mobile devices. Speed is the key.

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

## 📚 Documentation

### 🚀 Setup & Configuration
- **[Environment Setup](environment_setup.md)** - Development and production environment setup
- **[Deployment Guide](deployment_guide.md)** - Complete application deployment guide

### 💻 Development  
- **[Implementation Plan](IMPLEMENTATION_PLAN.md)** - Detailed implementation plan for fixes and improvements
- **[Optimization Plan](OPTIMIZATION_PLAN.md)** - Comprehensive performance optimization plan
- **[Changelog](CHANGELOG.md)** - Project change history and updates
- **[Database Documentation](database.md)** - Detailed database documentation

### 📊 Performance & Testing
- **[Performance Metrics](PERFORMANCE_METRICS.md)** - Performance metrics monitoring system
- **[Mobile Testing Guide](MOBILE_TESTING_GUIDE.md)** - Mobile device optimization testing guide
- **[Configuration Testing](#configuration-testing)** - Security settings testing for different environments

### 📋 Maintenance
- **[Changelog](CHANGELOG.md)** - Version and change tracking
- **[Implementation Plan](IMPLEMENTATION_PLAN.md)** - Technical documentation for fixes

### 📁 Documentation Structure
```
docs/
├── README.md (main documentation + Performance Testing)
├── CHANGELOG.md (change history + new documentation)
├── IMPLEMENTATION_PLAN.md (implementation plan + Performance Requirements)
├── PERFORMANCE_METRICS.md (metrics system + measurement instructions)
├── MOBILE_TESTING_GUIDE.md (testing + requirements)
├── OPTIMIZATION_PLAN.md (optimization plan)
├── database.md
├── deployment_guide.md  
└── environment_setup.md
```

## Technical Details

### Site Speed
- Using fast CSS
- HTTP/2
- Caching
- Small size

### Environment Configuration
- **Dual Environment Support**: Separate development and production configurations
- **Smart Environment Detection**: Automatic detection via `.env` symlink
- **Segregated nginx Configuration**: Prevents upstream conflicts in nginx-proxy
- **Environment-Specific Settings**: Different SSL, domains, emails per environment

**Configuration Files:**
- `.env.development` / `.env.production` - Main application settings
- `.env.nginx.development` / `.env.nginx.production` - nginx-specific settings (no VIRTUAL_HOST)
- Automatic environment switching with `./scripts/switch_env.sh`

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

### Gallery Update Process (Dev → Prod)

**Recommended workflow for updating gallery content:**

1. **Upload on Development Environment**
   - Access development upload interface: `http://127.0.0.1:5000/admin/upload`
   - Upload all new albums and images through the web interface
   - Verify all uploads are successful and properly processed
   - Check gallery display at `http://127.0.0.1:5000/gallery`
   - Push changes to the repository

2. **Synchronize Database to Production**
   ```bash
   # Copy database from dev to prod
   scp instance/tresinky.db root@104.248.102.172:/root/Tresinky_web/instance/tresinky.db
   ```

3. **Restart Production Application**
   ```bash
   # On production server
   ./rebuild.sh
   ```

4. **Verify Production Gallery**
   - Check gallery at production URL
   - Verify all albums and images display correctly
   - Test admin interface functionality

**Notes:**
- Always upload through dev environment first to ensure proper processing
- Database contains image metadata, album structures, and file paths
- The `sync_gallery_with_disk()` function will automatically clean up any inconsistencies

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

## Database Migrations

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

For detailed migration instructions, see [MIGRATION_INSTRUCTIONS.md](MIGRATION_INSTRUCTIONS.md).

### Manual Migration (Alternative)
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

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[Your License Here] 

---

## 🔗 See Also

- **[Environment Setup](environment_setup.md)** - Detailed environment setup for development and production
- **[Deployment Guide](deployment_guide.md)** - Step-by-step deployment guide
- **[Database Documentation](database.md)** - Detailed database documentation and table structure
- **[Migration Instructions](MIGRATION_INSTRUCTIONS.md)** - Database migration instructions for production
- **[Implementation Plan](IMPLEMENTATION_PLAN.md)** - Technical documentation and implementation plan
- **[Changelog](CHANGELOG.md)** - Project version history and updates

## Performance Testing & Monitoring

### Website Performance Measurement

**MANDATORY REQUIREMENT:** After each code change affecting performance, performance metrics must be measured and documented.

#### Measurement Tools:

1. **Chrome DevTools Lighthouse**
   ```bash
   # In Chrome DevTools:
   # F12 → Lighthouse → Performance → Mobile → Generate Report
   ```

2. **PageSpeed Insights API**
   ```bash
   # Command for quick check
   curl "https://www.googleapis.com/pagespeed/v5/runPagespeed?url=https://your-site.com&category=performance&strategy=mobile"
   ```

3. **Web Vitals Monitoring (built-in)**
   ```javascript
   // In browser console
   WebVitals.getMetrics();
   ```

#### Key Metrics to Track:

- **Performance Score:** > 90 (mobile), > 95 (desktop)
- **LCP (Largest Contentful Paint):** < 2.5s
- **FID (First Input Delay):** < 100ms  
- **CLS (Cumulative Layout Shift):** < 0.1

#### Workflow After Changes:

1. **Make code changes**
2. **Run local testing:**
   - Chrome DevTools → Performance
   - Network tab for resource loading analysis
3. **Measure Lighthouse scores** (before and after)
4. **Check Web Vitals** in browser console
5. **Document results** in [Performance Metrics](PERFORMANCE_METRICS.md)
6. **When deploying to production** - repeat measurements via PageSpeed Insights

Detailed instructions see in [Mobile Testing Guide](MOBILE_TESTING_GUIDE.md).

## Configuration Testing

### Security Settings Testing for Different Environments

The application uses different security settings for development (HTTP) and production (HTTPS) environments. It's critical to verify the correctness of these settings.

#### Quick Tests

```bash
# Run automated tests
python -m pytest tests/test_app.py::test_configuration_environments -v
python -m pytest tests/test_app.py::test_security_settings_logic -v

# Check all tests
python -m pytest tests/test_app.py -v
```

#### Manual Configuration Check
```bash
# Development environment (HTTP)
python -c "
from config.config import DevelopmentConfig
config = DevelopmentConfig()
print('Development - USE_HTTPS:', config.USE_HTTPS)
print('Development - SESSION_COOKIE_SECURE:', config.SESSION_COOKIE_SECURE)
print('Development - REMEMBER_COOKIE_SECURE:', config.REMEMBER_COOKIE_SECURE)
print('✅ For development secure cookies should be DISABLED')
"

# Production environment (HTTPS)  
python -c "
from config.config import ProductionConfig
config = ProductionConfig()
print('Production - USE_HTTPS:', config.USE_HTTPS)
print('Production - SESSION_COOKIE_SECURE:', config.SESSION_COOKIE_SECURE)
print('Production - REMEMBER_COOKIE_SECURE:', config.REMEMBER_COOKIE_SECURE)
print('✅ For production secure cookies should be ENABLED')
"

# Check ProxyFix compatibility
python -c "
from config.config import ProductionConfig
config = ProductionConfig()
print('Has PREFERRED_URL_SCHEME:', hasattr(config, 'PREFERRED_URL_SCHEME'))
print('✅ PREFERRED_URL_SCHEME should be False (not set)')
"
```

#### Check in Different Environments

```bash
# Test development
export FLASK_ENV=development
python -c "from config.config import get_config; print('Active config:', get_config().__name__)"

# Test production
export FLASK_ENV=production  
python -c "from config.config import get_config; print('Active config:', get_config().__name__)"

# Test testing
export FLASK_ENV=testing
python -c "from config.config import get_config; print('Active config:', get_config().__name__)"
```

#### Browser Check (production)

1. **Open Developer Tools** (F12)
2. **Go to Application → Cookies tab**
3. **Check cookie flags:**
   - ✅ `Secure` - should be enabled only for HTTPS production
   - ✅ `HttpOnly` - should be enabled always (XSS protection)

#### Expected Results:

| Environment | USE_HTTPS | SESSION_COOKIE_SECURE | REMEMBER_COOKIE_SECURE |
|-------------|-----------|---------------------|----------------------|
| Development | `False` | `False` | `False` |
| Production | `True` | `True` | `True` |
| Testing | `False` | (inherits from Config) | (inherits from Config) |

#### Troubleshooting:

**If secure cookies are enabled in development:**
```bash
# Check that correct configuration is used
python -c "
import os
print('FLASK_ENV:', os.getenv('FLASK_ENV', 'development'))
from config.config import get_config
print('Config class:', get_config().__name__)
"
```

**If secure cookies are disabled in production:**
```bash
# Check production settings
python -c "
from config.config import ProductionConfig
config = ProductionConfig()
print('Production config loaded correctly')
print('SESSION_COOKIE_SECURE:', config.SESSION_COOKIE_SECURE)
"
```

See also detailed instructions in the Implementation Plan.
