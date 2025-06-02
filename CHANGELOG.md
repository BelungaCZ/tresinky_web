🏠 [Главная](README.md) | 🚀 [Environment Setup](docs/environment_setup.md) | 🌐 [Deployment Guide](docs/deployment_guide.md) | 💻 [Implementation Plan](IMPLEMENTATION_PLAN.md)

---

# Changelog

## [Unreleased] - 2025-05-30

### Added
- Environment configuration system with development and production settings
- New configuration files:
  - `config/config.py` for centralized configuration management
  - `.env.development` for development environment settings
  - `.env.production` for production environment settings
- Environment switching script `scripts/switch_env.sh`
- Docker Compose configuration with environment-specific settings
- SSL certificate generation script `scripts/generate_ssl.sh`
- Nginx configuration with HTTP/2.0 support
- CI/CD pipeline configuration in `.github/workflows/`
- Test configuration and setup
- Comprehensive documentation in README.md

### Changed
- Updated `app.py` to use the new configuration system
- Modified `docker-compose.yml` to support environment-specific settings
- Enhanced Nginx configuration for better security and performance
- Updated project structure for better organization
- Improved documentation with detailed setup and usage instructions

### Security
- Added SSL/TLS configuration
- Implemented secure headers in Nginx
- Added environment-specific security settings
- Improved file upload security

### Infrastructure
- Added Docker support with multi-environment configuration
- Implemented Nginx as reverse proxy
- Added SQLite database configuration
- Set up CI/CD pipeline with GitHub Actions

### Development
- Added test configuration with pytest
- Implemented code coverage reporting
- Added development tools and scripts
- Enhanced project documentation

### Documentation
- Updated README.md with comprehensive project information
- Added setup instructions for different environments
- Documented security measures and best practices
- Added contribution guidelines

## How to Use

### Development Environment
```bash
./scripts/switch_env.sh development
```

### Production Environment
```bash
./scripts/switch_env.sh production
```

### SSL Certificate Generation
```bash
./scripts/generate_ssl.sh
```

### Running Tests
```bash
./run_tests.sh
```

---

## 🔗 См. также

- **🏠 [Главная](README.md)** - Основная документация проекта
- **🚀 [Environment Setup](docs/environment_setup.md)** - Настройка окружения для разработки
- **🌐 [Deployment Guide](docs/deployment_guide.md)** - Руководство по деплою
- **💻 [Implementation Plan](IMPLEMENTATION_PLAN.md)** - Техническая документация исправлений
- **⬅️ [Назад: Главная](README.md)** | **➡️ [Далее: Environment Setup](docs/environment_setup.md)** 