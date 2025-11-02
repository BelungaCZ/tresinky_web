# Environment Setup and Configuration

🏠 [Main](../README.md) | 📋 [Changelog](../CHANGELOG.md) | 💻 [Implementation Plan](../IMPLEMENTATION_PLAN.md) | 🌐 [Deployment Guide](deployment_guide.md)

---

## Overview

The application supports two environments: development and production. Each environment has its own configuration settings, security measures, and deployment requirements.

## Environment Configuration

### Environment File Management

Для упрощения разработки и тестирования environment разделен на development и production. Для определения, на каком environment что работает, используется файл `.env`, который является символической ссылкой на `.env.development` или на `.env.production`.

**Структура конфигурационных файлов:**

```text
.env                    # Символическая ссылка на активное окружение
.env.development        # Настройки для разработки
.env.production         # Настройки для продакшена
```

**Механизм работы:**

- `.env` - это символическая ссылка, которая указывает на актуальный файл конфигурации
- В development: `.env` → `.env.development`
- В production: `.env` → `.env.production`

**Переменные окружения, которые должны различаться:**

Все переменные, которые могут отличаться на development и production должны быть отражены в соответствующих файлах. Например:

- **Конфигурация SSL и дебагинга**: `FLASK_DEBUG`, `USE_HTTPS`
- **Пути к базам данных**: `DATABASE_URL`
- **Пароли и секретные ключи**: `SECRET_KEY`
- **Домены и хосты**: `DOMAIN`, `VIRTUAL_HOST`
- **SSL сертификаты**: `LETSENCRYPT_HOST`, `LETSENCRYPT_EMAIL`
- **Настройки безопасности**: различные уровни безопасности для разных окружений

### Nginx Configuration Separation

Начиная с версии 2025-01-03, конфигурация nginx была выделена в отдельные файлы для предотвращения конфликтов upstream в nginx-proxy.

**Структура nginx конфигурационных файлов:**

```text
.env.nginx.development     # nginx-specific настройки для разработки
.env.nginx.production      # nginx-specific настройки для продакшена
```

**Критические отличия nginx конфигурации:**

| Сервис | Файл конфигурации | VIRTUAL_HOST |
|--------|------------------|--------------|
| `web` | `.env.development` / `.env.production` | ✅ Присутствует |
| `nginx-proxy` | `.env.nginx.development` / `.env.nginx.production` | ❌ Отсутствует |
| `nginx-letsencrypt` | `.env.nginx.development` / `.env.nginx.production` | ❌ Отсутствует |

**Почему это важно:**

- nginx-proxy автоматически обнаруживает контейнеры с переменной `VIRTUAL_HOST`
- Если несколько контейнеров имеют одинаковый `VIRTUAL_HOST`, nginx-proxy добавляет их всех в upstream
- POST запросы могут попадать на неправильные контейнеры (nginx-letsencrypt, nginx-proxy)
- Контактная форма перестает работать

**Содержимое файлов nginx конфигурации:**

`.env.nginx.development`:

```ini
# Nginx configuration for development (БЕЗ VIRTUAL_HOST!)
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
DEFAULT_HOST=localhost
ALLOW_SELF_SIGNED=true
SSL_MODE=development
LETSENCRYPT_EMAIL=admin@sad-tresinky-cetechovice.cz
DEBUG=true
```

`.env.nginx.production`:

```ini
# Nginx configuration (БЕЗ VIRTUAL_HOST!)
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
DEFAULT_HOST=sad-tresinky-cetechovice.cz
ALLOW_SELF_SIGNED=false
SSL_MODE=production
LETSENCRYPT_EMAIL=admin@sad-tresinky-cetechovice.cz
DEBUG=false
```

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
2. **Обновить символическую ссылку `.env`** для указания на соответствующий файл конфигурации:
   - Для development: создать ссылку `.env` → `.env.development`
   - Для production: создать ссылку `.env` → `.env.production`
3. Load the appropriate environment configuration
4. Start containers with new settings

**Проверка текущего окружения:**

```bash
# Проверить, на какой файл указывает .env
ls -la .env

# Результат для development:
# .env -> .env.development

# Результат для production:
# .env -> .env.production
```

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

1. Prepare the environment. Switch to production environment:

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

## Common Configuration Issues and Solutions

### Problem: Contact Form Not Working (POST requests don't reach Flask)

**Симптомы:**

- Контактная форма загружается, но не отправляется
- В логах Flask видны только GET запросы к `/kontakt`, но нет POST
- curl тест показывает перенаправления: `curl -s vs curl -sL`

**Причина:**
nginx-proxy создает upstream с несколькими контейнерами, если они имеют одинаковый `VIRTUAL_HOST`

**Диагностика:**

```bash
# Проверить nginx upstream
docker compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf | grep -A10 "upstream"

# НЕПРАВИЛЬНО (несколько серверов):
# upstream sad-tresinky-cetechovice.cz {
#     server 172.18.0.2:5000;  # web
#     server 172.18.0.4:80;    # nginx-letsencrypt
#     server 172.18.0.3:80;    # nginx-proxy
# }

# ПРАВИЛЬНО (только web):
# upstream sad-tresinky-cetechovice.cz {
#     server 172.18.0.2:5000;  # ТОЛЬКО web
#     keepalive 2;
# }
```

**Решение:**

```bash
# Автоматическое исправление
./scripts/fix_nginx_upstream.sh

# Или ручное исправление:
# 1. Создать .env.nginx.production без VIRTUAL_HOST
# 2. Обновить docker-compose.yml для использования раздельных env файлов
# 3. Перезапустить контейнеры
```

### Problem: Wrong Environment Detection

**Симптомы:**

- Приложение запускается с неправильными настройками
- SSL сертификаты не соответствуют окружению

**Диагностика:**

```bash
# Проверить текущий environment
ls -la .env
readlink .env

# Проверить какие переменные загружены
docker compose exec web env | grep FLASK_ENV
```

**Решение:**

```bash
# Переключиться на правильное окружение
./scripts/switch_env.sh production  # или development
```

### Problem: SSL Certificate Issues

**Development:**

```bash
# Сгенерировать self-signed сертификаты
./scripts/generate_ssl.sh

# Проверить сертификаты
ls -la ssl/
```

**Production:**

```bash
# Проверить статус Let's Encrypt
docker compose logs nginx-letsencrypt

# Перезапустить получение сертификатов
docker compose restart nginx-letsencrypt
```

### Problem: Email Configuration Issues

**Диагностика:**

```bash
# Тест SMTP подключения
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

### Configuration Validation

**Проверка правильности конфигурации:**

```bash
# 1. Проверить environment
echo "Current environment: $(readlink .env)"

# 2. Проверить VIRTUAL_HOST в контейнерах
echo "=== web container VIRTUAL_HOST ==="
docker compose exec web env | grep VIRTUAL_HOST

echo "=== nginx-proxy container VIRTUAL_HOST ==="
docker compose exec nginx-proxy env | grep VIRTUAL_HOST || echo "VIRTUAL_HOST not set (correct)"

echo "=== nginx-letsencrypt container VIRTUAL_HOST ==="
docker compose exec nginx-letsencrypt env | grep VIRTUAL_HOST || echo "VIRTUAL_HOST not set (correct)"

# 3. Проверить nginx upstream
echo "=== nginx upstream configuration ==="
docker compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf | grep -A10 "upstream"
```

**Ожидаемые результаты:**

- `web` контейнер: VIRTUAL_HOST установлен
- `nginx-proxy` контейнер: VIRTUAL_HOST НЕ установлен
- `nginx-letsencrypt` контейнер: VIRTUAL_HOST НЕ установлен
- nginx upstream: только один сервер (web контейнер)
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

## Configuration Testing

### Automated Testing

Приложение включает автоматизированные тесты для проверки корректности настроек безопасности в разных окружениях:

```bash
# Запуск тестов конфигурации
python -m pytest tests/test_app.py::test_configuration_environments -v
python -m pytest tests/test_app.py::test_security_settings_logic -v

# Запуск всех тестов
python -m pytest tests/test_app.py -v
```

### Manual Configuration Verification

#### Проверка настроек Development окружения

```bash
python -c "
from config.config import DevelopmentConfig
config = DevelopmentConfig()
print('=== DEVELOPMENT CONFIGURATION ===')
print(f'DEBUG: {config.DEBUG}')
print(f'USE_HTTPS: {config.USE_HTTPS}')
print(f'SESSION_COOKIE_SECURE: {config.SESSION_COOKIE_SECURE}')
print(f'REMEMBER_COOKIE_SECURE: {config.REMEMBER_COOKIE_SECURE}')
print(f'DOMAIN: {config.DOMAIN}')
print('✅ Для HTTP окружения secure cookies должны быть FALSE')
"
```

#### Проверка настроек Production окружения

```bash
python -c "
from config.config import ProductionConfig
config = ProductionConfig()
print('=== PRODUCTION CONFIGURATION ===')
print(f'DEBUG: {config.DEBUG}')
print(f'USE_HTTPS: {config.USE_HTTPS}')
print(f'SESSION_COOKIE_SECURE: {config.SESSION_COOKIE_SECURE}')
print(f'REMEMBER_COOKIE_SECURE: {config.REMEMBER_COOKIE_SECURE}')
print(f'DOMAIN: {config.DOMAIN}')
print(f'Has PREFERRED_URL_SCHEME: {hasattr(config, \"PREFERRED_URL_SCHEME\")}')
print('✅ Для HTTPS окружения secure cookies должны быть TRUE')
print('✅ PREFERRED_URL_SCHEME не должно быть установлено (ProxyFix)')
"
```

#### Проверка активной конфигурации

```bash
python -c "
from config.config import get_config
import os
print(f'Current FLASK_ENV: {os.getenv(\"FLASK_ENV\", \"development\")}')
config_class = get_config()
config = config_class()
print(f'Active config class: {config_class.__name__}')
print(f'SESSION_COOKIE_SECURE: {config.SESSION_COOKIE_SECURE}')
print(f'USE_HTTPS: {config.USE_HTTPS}')
"
```

### Expected Configuration Results

| Окружение | DEBUG | USE_HTTPS | SESSION_COOKIE_SECURE | REMEMBER_COOKIE_SECURE |
|-----------|-------|-----------|---------------------|----------------------|
| Development | `True` | `False` | `False` | `False` |
| Production | `False` | `True` | `True` | `True` |
| Testing | `True` | `False` | (наследует) | (наследует) |

### Security Configuration Validation

#### Проверка ProxyFix совместимости

```bash
# PREFERRED_URL_SCHEME не должно быть установлено
python -c "
from config.config import ProductionConfig
config = ProductionConfig()
if hasattr(config, 'PREFERRED_URL_SCHEME'):
    print('❌ PREFERRED_URL_SCHEME установлено - конфликт с ProxyFix!')
else:
    print('✅ PREFERRED_URL_SCHEME не установлено - ProxyFix совместимость OK')
"
```

#### Проверка настроек в разных окружениях

```bash
# Test development
export FLASK_ENV=development
python -c "from config.config import get_config; print('Config:', get_config().__name__)"

# Test production
export FLASK_ENV=production
python -c "from config.config import get_config; print('Config:', get_config().__name__)"

# Reset environment
unset FLASK_ENV
```

Подробные инструкции по тестированию см. в [README.md - Configuration Testing](../README.md#configuration-testing).

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
