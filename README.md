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
- **[Optimization Plan](OPTIMIZATION_PLAN.md)** - Комплексный план оптимизации производительности
- **[Changelog](CHANGELOG.md)** - История изменений и обновлений проекта
- **[Database Documentation](docs/database.md)** - Подробная документация по базе данных

### 📊 Performance & Testing
- **[Performance Metrics](PERFORMANCE_METRICS.md)** - Система мониторинга метрик производительности
- **[Mobile Testing Guide](MOBILE_TESTING_GUIDE.md)** - Руководство по тестированию оптимизаций на мобильных устройствах

### 📋 Maintenance
- **[Changelog](CHANGELOG.md)** - Отслеживание версий и изменений
- **[Implementation Plan](IMPLEMENTATION_PLAN.md)** - Техническая документация по исправлениям

### 📁 Documentation Structure
```
docs/
├── README.md (основная документация + Performance Testing)
├── CHANGELOG.md (история изменений + новая документация)
├── IMPLEMENTATION_PLAN.md (план реализации + Performance Requirements)
├── PERFORMANCE_METRICS.md (система метрик + инструкции по измерению)
├── MOBILE_TESTING_GUIDE.md (тестирование + требования)
├── OPTIMIZATION_PLAN.md (план оптимизации)
├── docs/
│   ├── database.md
│   ├── deployment_guide.md  
│   └── environment_setup.md
└── scripts/
    └── performance-check.sh (автоматизация тестирования)
```

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

## Performance Testing & Monitoring

### Измерение производительности сайта

**ОБЯЗАТЕЛЬНОЕ ТРЕБОВАНИЕ:** После каждого изменения кода, влияющего на производительность, необходимо измерить метрики производительности и документировать результаты.

#### Инструменты для измерения:

1. **Chrome DevTools Lighthouse**
   ```bash
   # В Chrome DevTools:
   # F12 → Lighthouse → Performance → Mobile → Generate Report
   ```

2. **PageSpeed Insights API**
   ```bash
   # Команда для быстрой проверки
   curl "https://www.googleapis.com/pagespeed/v5/runPagespeed?url=https://your-site.com&category=performance&strategy=mobile"
   ```

3. **Web Vitals Monitoring (встроенный)**
   ```javascript
   // В консоли браузера
   WebVitals.getMetrics();
   ```

#### Ключевые метрики для отслеживания:

- **Performance Score:** > 90 (mobile), > 95 (desktop)
- **LCP (Largest Contentful Paint):** < 2.5s
- **FID (First Input Delay):** < 100ms  
- **CLS (Cumulative Layout Shift):** < 0.1

#### Workflow после изменений:

1. **Сделать изменения в коде**
2. **Запустить локальное тестирование:**
   - Chrome DevTools → Performance
   - Network tab для анализа загрузки ресурсов
3. **Измерить Lighthouse scores** (до и после)
4. **Проверить Web Vitals** в консоли браузера
5. **Документировать результаты** в [Performance Metrics](PERFORMANCE_METRICS.md)
6. **При деплое на production** - повторить измерения через PageSpeed Insights

Подробные инструкции см. в [Mobile Testing Guide](MOBILE_TESTING_GUIDE.md).


