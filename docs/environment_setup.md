🏠 [Главная](../README.md) | 📋 [Changelog](../CHANGELOG.md) | 💻 [Implementation Plan](../IMPLEMENTATION_PLAN.md) | 🌐 [Deployment Guide](deployment_guide.md)

---

# Environment Setup and Configuration

## Overview

The application supports two environments: development and production. Each environment has its own configuration settings, security measures, and deployment requirements.

## Environment Configuration

### Development Environment

The development environment is configured for local development and testing. It includes:

- Debug mode enabled
- Local database
- Development-specific settings

Configuration file: `.env.development`
```ini
FLASK_ENV=development
FLASK_APP=app.py
FLASK_DEBUG=1
SECRET_KEY=your-development-secret-key
DATABASE_URL=sqlite:///tresinky.db
DOMAIN=localhost:5000
USE_HTTPS=true
```

### Production Environment

The production environment is configured for deployment to the live server. It includes:

- Debug mode disabled
- Production database
- HTTPS enabled
- Production-specific security settings

Configuration file: `.env.production`
```ini
FLASK_ENV=production
FLASK_APP=app.py
FLASK_DEBUG=0
SECRET_KEY=your-production-secret-key
DATABASE_URL=sqlite:///tresinky.db
DOMAIN=sad-tresinky-cetechovice.cz
USE_HTTPS=true
```

## Docker Configuration

The application uses Docker for containerization and deployment. The `docker-compose.yml` file defines three services:

1. Web Service (Flask Application)
   - Builds from the Dockerfile
   - Mounts the application code
   - Uses environment-specific configuration
   - Connects to the database

2. Nginx Service
   - Serves as reverse proxy
   - Handles SSL/TLS
   - Serves static files
   - Configurable ports

3. Database Service
   - SQLite database
   - Persistent storage

## SSL Configuration

SSL certificates will be managed by Let's Encrypt for the production environment. 
The `scripts/generate_ssl.sh` script can generate self-signed certificates for development:

```bash
./scripts/generate_ssl.sh
```

## Environment Switching

Use the `scripts/switch_env.sh` script to switch between environments:

```bash
# Switch to development
./scripts/switch_env.sh development

# Switch to production
./scripts/switch_env.sh production
```

The script will:
1. Stop existing containers
2. Load the appropriate environment configuration
3. Start containers with new settings

## Nginx Configuration

The Nginx configuration (`config/nginx.conf`) includes:

- HTTP/2.0 support
- SSL/TLS configuration
- Security headers
- Static file serving
- Proxy settings

## Security Measures

### Development
- Debug mode enabled for easier development
- Local database
- HTTP for local access
- HTTPS for local testing
- Development-specific security settings

### Production
- Debug mode disabled
- HTTPS required
- Secure headers enabled
- Production-specific security settings
- SSL/TLS configuration

## Production Deployment Process

1. Prepare the environment:

   # Switch to production environment
   ```bash
   ./scripts/switch_env.sh production
   ```

2. Start the services:
   ```bash
   docker compose up -d
   ```

3. Verify the deployment:
   - Check application logs
   - Verify SSL configuration
   - Test all functionality

## Monitoring and Maintenance

### Logs
- Application logs: `docker compose logs web`
- Nginx logs: `docker compose logs nginx`

### Updates
1. Pull latest changes
2. Rebuild containers:
   ```bash
   ./prod_rebuild.sh
   ```

### Backup
- Database: `./instance/tresinky.db`
- SSL certificates: `./ssl/`
- Configuration files: `.env.*`

## Troubleshooting

### Common Issues

1. SSL Certificate Issues
   - Verify certificate paths
   - Check certificate permissions
   - Ensure proper certificate format

2. Database Issues
   - Check database file permissions
   - Verify database path
   - Ensure proper database initialization

3. Nginx Issues
   - Check Nginx configuration
   - Verify port availability
   - Check SSL configuration

### Debugging

1. Development Environment
   - Enable debug mode
   - Check application logs
   - Use development tools

2. Production Environment
   - Check Nginx logs
   - Monitor application logs
   - Verify SSL configuration

## Best Practices

1. Security
   - Use strong secret keys
   - Enable HTTPS in production
   - Implement security headers
   - Regular security updates

2. Performance
   - Enable HTTP/2.0
   - Configure caching
   - Optimize static files
   - Monitor resource usage

3. Maintenance
   - Regular backups
   - Log monitoring
   - Security updates
   - Performance optimization

---

## 🔗 См. также

- **🏠 [Главная](../README.md)** - Основная документация проекта
- **🌐 [Deployment Guide](deployment_guide.md)** - Полное руководство по деплою
- **💻 [Implementation Plan](../IMPLEMENTATION_PLAN.md)** - Техническая документация
- **📋 [Changelog](../CHANGELOG.md)** - История изменений проекта
- **⬅️ [Назад: Changelog](../CHANGELOG.md)** | **➡️ [Далее: Deployment Guide](deployment_guide.md)** 