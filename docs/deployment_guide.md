# Deployment Guide

🏠 [Main](../README.md) | 📋 [Changelog](../CHANGELOG.md) | 💻 [Implementation Plan](../IMPLEMENTATION_PLAN.md) | 🚀 [Environment Setup](environment_setup.md)

---

## Prerequisites

1. Docker and Docker Compose installed
2. Git installed
3. Access to the server
4. Domain name configured
5. SSL certificates (self signed for development; for production SSL certificates will be managed by Let's Encrypt)

## Initial Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/Tresinky_web.git
   cd Tresinky_web
   ```

## Development Deployment

1. Generate self signed SSL certificate for development:

   ```bash
   ./scripts/generate_ssl.sh 
   ```

2. Switch to development environment:

   ```bash
   ./scripts/switch_env.sh development
   ```

3. Start the services:

   ```bash
   docker compose up -d
   ```text
      or 
   ```bash
   flask run --host=0.0.0.0 --port=5000 
   ```

4. Access the application:
   - Web: <http://localhost:5000>
   - Admin: <http://localhost:5000/admin>

## Production Deployment

1. SSL certificates will be managed by Let's Encrypt.

2. Switch to production environment:

   ```bash
   ./scripts/switch_env.sh production
   ```

3. Setup production environment:

   ```bash
   ./scripts/setup_production.sh production
   ```

4. Start the services:

   ```bash
   docker compose up -d
   ```

5. Verify the deployment:
   - Check response: `curl -I http://sad-tresinky-cetechovice.cz`
   - Check response: `curl -I https://sad-tresinky-cetechovice.cz`
   - Check application logs: `docker compose logs web`
   - Check Nginx logs: `docker compose logs nginx`
   - Test HTTPS: <https://sad-tresinky-cetechovice.cz>

## Environment Configuration

### Overview

The application uses a sophisticated environment configuration system that separates settings between development and production environments while maintaining flexibility and security.

### Environment Files Structure

```text
.
├── .env                          # Symlink to current environment
├── .env.development             # Development settings
├── .env.production              # Production settings  
├── .env.nginx.development       # Nginx-specific dev settings
├── .env.nginx.production        # Nginx-specific prod settings
└── .env.example                 # Template file
```

### Environment Detection

The system automatically detects the current environment using the `.env` symlink:

```bash
# Check current environment
ls -la .env
# Output examples:
# lrwxr-xr-x .env -> .env.development  # Development
# lrwxr-xr-x .env -> .env.production   # Production
```

### Configuration Separation

#### Web Application (`web` service)

Uses complete environment files with all application settings:

- **Development**: `.env.development`
- **Production**: `.env.production`

**Key settings:**

- `VIRTUAL_HOST` - Domain configuration for nginx-proxy
- `LETSENCRYPT_HOST` - SSL certificate domains
- `MAIL_*` - Email configuration
- `SECRET_KEY` - Application security
- `DEBUG` - Debug mode

#### Nginx Services (`nginx-proxy`, `nginx-letsencrypt`)

Uses specialized environment files **without** `VIRTUAL_HOST` to prevent upstream conflicts:

- **Development**: `.env.nginx.development`
- **Production**: `.env.nginx.production`

**Key settings:**

- `DEFAULT_HOST` - Default domain
- `ALLOW_SELF_SIGNED` - SSL certificate validation
- `SSL_MODE` - SSL configuration mode
- `LETSENCRYPT_EMAIL` - Certificate registration email

### Development vs Production Differences

| Setting | Development | Production | Purpose |
|---------|-------------|------------|---------|
| `VIRTUAL_HOST` | `localhost, sad-tresinky-cetechovice.cz` | `sad-tresinky-cetechovice.cz` | Proxy domains |
| `DEFAULT_HOST` | `localhost` | `sad-tresinky-cetechovice.cz` | Default SSL domain |
| `ALLOW_SELF_SIGNED` | `true` | `false` | SSL certificate validation |
| `SSL_MODE` | `development` | `production` | SSL configuration |
| `DEBUG` | `true` | `false` | Debug mode |
| `ADMIN_EMAIL` | `stashok@speakasap.com` | `stashok@speakasap.com` | Admin notifications |

### Environment Switching

```bash
# Switch to development
./scripts/switch_env.sh development

# Switch to production  
./scripts/switch_env.sh production

# Verify current environment
readlink .env
```

### Critical Configuration Notes

1. **VIRTUAL_HOST Separation**: Only the `web` service should have `VIRTUAL_HOST` variable. nginx services must not have it to prevent upstream conflicts.

2. **Email Configuration**: Same SMTP settings work for both environments, but admin emails differ.

3. **SSL Configuration**: Development uses self-signed certificates, production uses Let's Encrypt.

4. **Domain Configuration**: Development supports both localhost and domain access, production only domain.

### Configuration Validation

```bash
# Check nginx upstream (should show only web container)
docker compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf | grep -A5 "upstream"

# Expected output:
# upstream sad-tresinky-cetechovice.cz {
#     server 172.18.0.2:5000;  # Only web container
#     keepalive 2;
# }
```

### Troubleshooting Configuration Issues

#### Contact Form Not Working

If POST requests don't reach Flask:

1. **Check nginx upstream**:

   ```bash
   docker compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf | grep -A10 "upstream"
   ```

2. **If multiple servers in upstream**:

   ```bash
   # Fix nginx configuration
   ./scripts/fix_nginx_upstream.sh
   ```

3. **Verify configuration files**:

   ```bash
   # Check that nginx services don't have VIRTUAL_HOST
   docker compose exec nginx-proxy env | grep VIRTUAL_HOST  # Should be empty
   docker compose exec web env | grep VIRTUAL_HOST          # Should show domain
   ```

## Database Management

### Backup

```bash
# Backup database
cp instance/tresinky.db instance/tresinky.db.backup

# Backup with timestamp
cp instance/tresinky.db instance/tresinky.db.$(date +%Y%m%d_%H%M%S)
```

### Restore

```bash
# Restore from backup
cp instance/tresinky.db.backup instance/tresinky.db
```

## Gallery Content Management

### Gallery Update Process (Dev → Prod)

**Step-by-step workflow for updating gallery content safely:**

#### Step 1: Upload Content on Development

```bash
# Access development upload interface
http://127.0.0.1:5000/admin/upload
```

1. Upload all new albums and images through the web interface
2. Verify all uploads are successful and properly processed
3. Check gallery display and functionality
4. Ensure all metadata is correctly set

#### Step 2: Synchronize Database

```bash
# Copy database from development to production
scp instance/tresinky.db root@104.248.102.172:/root/Tresinky_web/instance/tresinky.db
```

#### Step 3: Synchronize Gallery Files (if needed)

```bash
# Sync gallery images from dev to prod
rsync -avz --delete static/images/gallery/ root@104.248.102.172:/root/Tresinky_web/static/images/gallery/

# Alternative: Create and transfer archive
tar -czf gallery_backup_$(date +%Y%m%d_%H%M%S).tar.gz static/images/gallery/
scp gallery_backup_*.tar.gz root@104.248.102.172:/root/Tresinky_web/
```

#### Step 4: Restart Production Application

```bash
# On production server
cd /root/Tresinky_web
docker compose down
docker compose up -d
```

#### Step 5: Verify Production

1. Check gallery at production URL
2. Verify all albums and images display correctly
3. Test admin interface functionality
4. Check logs for any errors

### Benefits of This Approach

- **Reliability**: Dev environment ensures proper processing
- **Safety**: Database contains all metadata and relationships
- **Consistency**: Automatic synchronization via `sync_gallery_with_disk()`
- **Rollback**: Easy to restore from database backups
- **Quality Control**: Visual verification before production deployment

### Important Notes

- Always use development environment for initial uploads
- Database synchronization includes all image metadata and album structures
- File synchronization may be needed if processing differs between environments
- The application automatically syncs database with filesystem on startup
- Random album previews will be automatically generated from available images

## SSL Certificate Management

### Development

- Use self-signed certificates generated by `scripts/generate_ssl.sh`
- Certificates stored in `ssl/` directory

### Production

1. SSL certificates will be managed by Let's Encrypt.
2. Update Nginx configuration if needed

## Monitoring

### Logs

```bash
# Application logs
docker compose logs web

# Nginx logs
docker compose logs nginx

# Follow logs
docker compose logs -f web
```

### Health Checks

1. Application: <http://localhost:5000/health>
2. Nginx: <http://localhost/health>

## Updates and Maintenance

### Application Updates

1. Pull latest changes:

   ```bash
   git pull origin main
   ```

2. Rebuild and restart:

   ```bash
   docker compose down
   docker compose up -d --build
   ```

### Database Updates

1. Backup current database
2. Apply migrations if needed
3. Verify data integrity

### SSL Certificate Renewal

1. Reload Nginx:

   ```bash
   docker compose restart nginx
   ```

## Troubleshooting

### Common Issues

1. Application Not Starting

   ```bash
   # Check logs
   docker compose logs web
   
   # Check container status
   docker compose ps
   ```

2. Nginx Issues

   ```bash
   # Check Nginx configuration
   docker compose exec nginx nginx -t
   
   # Check Nginx logs
   docker compose logs nginx
   ```

3. Database Issues

   ```bash
   # Check database file
   ls -l instance/tresinky.db
   
   # Check database logs
   docker compose logs db
   ```

4. SSL Certificate Issues

   ```bash
   # Check certificate status
   docker compose exec nginx-proxy ls -la /etc/nginx/certs/
   
   # Renew certificates
   docker compose restart nginx-letsencrypt
   ```

5. Contact Form Issues

   ```bash
   # Check if POST requests reach Flask
   docker compose logs web | grep -i "POST\|contact" | tail -10
   
   # Check nginx upstream configuration  
   docker compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf | grep -A10 "upstream"
   
   # Fix nginx upstream if multiple servers present
   ./scripts/fix_nginx_upstream.sh
   ```

6. Email Issues

   ```bash
   # Test SMTP connection
   docker compose exec web python3 -c "
   import smtplib, os
   try:
       server = smtplib.SMTP(os.getenv('MAIL_SERVER'), int(os.getenv('MAIL_PORT')))
       server.starttls()
       server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
       print('✅ SMTP connection successful')
       server.quit()
   except Exception as e:
       print(f'❌ SMTP error: {e}')
   "
   ```

### Environment Configuration Issues

1. **Wrong Environment Detected**:

   ```bash
   # Check symlink
   ls -la .env
   
   # Fix symlink
   ./scripts/switch_env.sh production  # or development
   ```

2. **nginx-proxy Multiple Upstreams**:
   - **Symptom**: Contact form submissions don't work
   - **Cause**: nginx-proxy sees multiple containers with VIRTUAL_HOST
   - **Fix**: Run `./scripts/fix_nginx_upstream.sh`

3. **SSL Certificate Problems**:

   ```bash
   # Development - use self-signed
   ./scripts/generate_ssl.sh
   
   # Production - check Let's Encrypt
   docker compose logs nginx-letsencrypt
   ```

### Performance Issues

1. Check resource usage:

   ```bash
   docker stats
   ```

2. Monitor logs for errors:

   ```bash
   docker compose logs -f
   ```

3. Check Nginx access logs:

   ```bash
   docker compose exec nginx tail -f /var/log/nginx/access.log
   ```

## Security Checklist

1. Environment Variables
   - [ ] Strong secret keys
   - [ ] Production settings
   - [ ] Secure database credentials

2. SSL/TLS
   - [ ] Valid certificates
   - [ ] Proper configuration
   - [ ] Regular renewal

3. Nginx
   - [ ] Security headers
   - [ ] SSL configuration
   - [ ] Access restrictions
   - [ ] HTTP2 support

4. Application
   - [ ] Debug mode disabled
   - [ ] Secure session settings
   - [ ] Input validation

## Backup and Recovery

### Regular Backups

1. Database
2. SSL certificates
3. Configuration files
4. Uploaded gallery files

### Recovery Procedure

1. Stop services
2. Restore backups
3. Verify configuration
4. Start services

## Scaling

### Vertical Scaling

1. Increase container resources
2. Optimize Nginx configuration
3. Enable caching

### Horizontal Scaling

1. Load balancer setup
2. Database replication
3. Session management

## Maintenance Schedule

### Daily

- Monitor logs
- Check application status
- Verify backups

### Weekly

- Review security logs
- Check SSL certificates
- Monitor performance

### Monthly

- Update dependencies
- Review security settings
- Optimize configuration
- Check disk space

## Support

For issues and support:

1. Check documentation
2. Review logs
3. Contact development team

---

## 🔗 См. также

- **🏠 [Главная](../README.md)** - Основная документация проекта
- **🚀 [Environment Setup](environment_setup.md)** - Детальная настройка окружения
- **💻 [Implementation Plan](../IMPLEMENTATION_PLAN.md)** - Техническая документация
- **📋 [Changelog](../CHANGELOG.md)** - История изменений проекта
- **⬅️ [Назад: Environment Setup](environment_setup.md)** | **➡️ [Далее: Changelog](../CHANGELOG.md)**
