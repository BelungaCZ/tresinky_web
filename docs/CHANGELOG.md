# Changelog

All notable changes to the Třešinky Cetechovice web application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive performance monitoring system
- Mobile-specific optimization testing
- Detailed performance metrics tracking
- English documentation translation

### Changed
- Moved all documentation to `docs/` directory
- Translated all Markdown files to English
- Updated performance optimization strategies

### Fixed
- Gallery loading issue - removed early return preventing gallery display
- Template variable name mismatch - changed 'albums' to 'folders'
- Syntax errors in elif blocks - corrected indentation
- Cache-busting parameter issues causing 404 errors

## [1.2.0] - 2024-01-XX

### Added
- Gallery system with album support
- Image upload and management interface
- Contact form functionality
- Donation system integration
- Admin interface for content management
- Support for multiple image formats (JPG, JPEG, PNG, WebP, HEIC)
- Video file support (MP4)
- Automatic image optimization and WebP conversion
- Album management with automatic cleanup
- Responsive design for all devices
- Performance optimization features

### Changed
- Updated image processing pipeline
- Improved gallery navigation
- Enhanced mobile responsiveness
- Optimized database queries

### Fixed
- Image loading performance issues
- Mobile touch interaction problems
- Database synchronization issues
- File upload validation

## [1.1.0] - 2024-01-XX

### Added
- Basic web application structure
- SQLite database integration
- Flask application framework
- Static file serving
- Basic routing system
- Environment configuration
- Logging system

### Changed
- Initial project setup
- Basic functionality implementation

### Fixed
- Initial development issues
- Basic configuration problems

## [1.0.0] - 2024-01-XX

### Added
- Initial project release
- Basic web application
- Project documentation
- Development environment setup

---

## Performance Metrics History

### Version 1.2.0 Performance
- **Performance Score:** 75-80 (mobile)
- **LCP:** 3-4 seconds
- **FID:** 150-200ms
- **CLS:** 0.2-0.3
- **TTI:** 4-5 seconds

### Target Performance (Next Release)
- **Performance Score:** > 90 (mobile)
- **LCP:** < 2.5 seconds
- **FID:** < 100ms
- **CLS:** < 0.1
- **TTI:** < 3 seconds

## Breaking Changes

### Version 1.2.0
- Changed gallery template variable from 'albums' to 'folders'
- Updated image processing pipeline
- Modified database schema for gallery images

### Version 1.1.0
- Initial database schema implementation
- Basic application structure

## Migration Notes

### From Version 1.1.0 to 1.2.0
1. **Database Migration:**
   ```bash
   # Run database migration script
   ./scripts/migrate_database.sh
   ```

2. **Template Updates:**
   - Update gallery templates to use 'folders' variable
   - Verify image loading functionality

3. **Configuration Updates:**
   - Update environment variables
   - Verify file upload settings

### From Version 1.0.0 to 1.1.0
1. **Database Setup:**
   ```bash
   # Initialize database
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

2. **Environment Configuration:**
   - Set up development environment
   - Configure production settings

## Known Issues

### Version 1.2.0
- Performance optimization needed for mobile devices
- Some images may load slowly on slow connections
- Gallery navigation could be improved

### Version 1.1.0
- Basic functionality only
- Limited performance optimization
- No mobile-specific features

## Future Releases

### Version 1.3.0 (Planned)
- Performance optimizations
- Mobile-specific improvements
- Enhanced caching strategy
- Better error handling

### Version 1.4.0 (Planned)
- Advanced gallery features
- Search functionality
- User authentication
- API endpoints

## Contributing

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 guidelines for Python code
- Use type hints for function parameters and return values
- Write comprehensive tests for new features
- Update documentation for any changes
- Follow the existing code style

### Testing Requirements
- All new features must be tested
- Performance tests must be run for optimization changes
- Mobile testing is required for UI changes
- Database migrations must be tested

## Support

### Getting Help
- Check the documentation in the `docs/` directory
- Review the changelog for known issues
- Check the issue tracker for reported problems
- Contact the development team for support

### Reporting Issues
- Use the issue tracker to report bugs
- Include detailed steps to reproduce issues
- Provide system information and browser details
- Include performance metrics if applicable

---

*For more information about the project, see the [README](README.md) and [Implementation Plan](IMPLEMENTATION_PLAN.md).*
