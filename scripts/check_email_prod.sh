#!/bin/bash

# Email Diagnostics Script for Production Server
# Проверяет настройки email на production сервере Třešinky Cetechovice

echo "🔧 ДИАГНОСТИКА EMAIL НАСТРОЕК НА PRODUCTION"
echo "=" * 50

# Проверяем текущую директорию
echo "📁 Рабочая директория: $(pwd)"

# Проверяем .env файл
if [ -L ".env" ]; then
    link_target=$(readlink .env)
    echo "✅ .env файл найден (symlink -> $link_target)"
else
    echo "❌ .env симлинк не найден"
fi

# Проверяем содержимое .env файла
echo ""
echo "🔍 ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ:"
echo "=" * 30

# Проверяем основные переменные (без показа паролей)
if [ -f ".env" ]; then
    echo "FLASK_ENV=$(grep FLASK_ENV .env | cut -d'=' -f2)"
    echo "MAIL_SERVER=$(grep MAIL_SERVER .env | cut -d'=' -f2)"
    echo "MAIL_PORT=$(grep MAIL_PORT .env | cut -d'=' -f2)"
    echo "MAIL_USE_TLS=$(grep MAIL_USE_TLS .env | cut -d'=' -f2)"
    echo "MAIL_USERNAME=$(grep MAIL_USERNAME .env | cut -d'=' -f2)"
    echo "MAIL_PASSWORD=***скрыто***"
    echo "MAIL_DEFAULT_SENDER=$(grep MAIL_DEFAULT_SENDER .env | cut -d'=' -f2)"
    echo "ADMIN_EMAIL=$(grep ADMIN_EMAIL .env | cut -d'=' -f2)"
else
    echo "❌ Файл .env не найден"
fi

# Проверяем доступность SMTP сервера
echo ""
echo "🌐 ПРОВЕРКА ПОДКЛЮЧЕНИЯ К SMTP:"
echo "=" * 30

MAIL_SERVER=$(grep MAIL_SERVER .env | cut -d'=' -f2)
MAIL_PORT=$(grep MAIL_PORT .env | cut -d'=' -f2)

echo "Проверка подключения к $MAIL_SERVER:$MAIL_PORT..."

if command -v nc > /dev/null 2>&1; then
    if nc -z -w5 $MAIL_SERVER $MAIL_PORT 2>/dev/null; then
        echo "✅ Подключение к $MAIL_SERVER:$MAIL_PORT успешно"
    else
        echo "❌ Не удается подключиться к $MAIL_SERVER:$MAIL_PORT"
        echo "💡 Возможно, порт $MAIL_PORT заблокирован файрволом"
    fi
else
    echo "⚠️  Утилита nc не найдена, проверка подключения пропущена"
fi

# Проверяем логи приложения на наличие ошибок email
echo ""
echo "📝 ПРОВЕРКА ЛОГОВ НА ОШИБКИ EMAIL:"
echo "=" * 40

if [ -d "logs" ]; then
    echo "Поиск ошибок email в логах..."
    
    # Ищем ошибки SMTP
    smtp_errors=$(grep -i "smtp" logs/*.log 2>/dev/null | tail -5)
    if [ ! -z "$smtp_errors" ]; then
        echo "🔍 Найдены SMTP ошибки:"
        echo "$smtp_errors"
    else
        echo "✅ SMTP ошибок не найдено"
    fi
    
    # Ищем ошибки email
    email_errors=$(grep -i "email\|mail" logs/*.log 2>/dev/null | tail -5)
    if [ ! -z "$email_errors" ]; then
        echo "🔍 Найдены Email ошибки:"
        echo "$email_errors"
    else
        echo "✅ Email ошибок не найдено"
    fi
    
    # Ищем ошибки contact
    contact_errors=$(grep -i "contact" logs/*.log 2>/dev/null | tail -5)
    if [ ! -z "$contact_errors" ]; then
        echo "🔍 Найдены Contact ошибки:"
        echo "$contact_errors"
    else
        echo "✅ Contact ошибок не найдено"
    fi
else
    echo "⚠️  Директория logs не найдена"
fi

# Проверяем конфигурацию Flask
echo ""
echo "⚙️  ПРОВЕРКА КОНФИГУРАЦИИ FLASK:"
echo "=" * 35

echo "Проверка загрузки конфигурации Flask..."
if [ -f "config/config.py" ]; then
    echo "✅ Файл config/config.py найден"
    
    # Проверяем fallback значения
    fallback_admin=$(grep "ADMIN_EMAIL.*=" config/config.py | grep -o "'.*@.*'")
    if [ ! -z "$fallback_admin" ]; then
        echo "⚠️  Найдено fallback значение ADMIN_EMAIL: $fallback_admin"
        echo "💡 Если переменная ADMIN_EMAIL не загружается, будет использовано это значение"
    fi
else
    echo "❌ Файл config/config.py не найден"
fi

# Проверяем состояние Docker контейнера (если используется)
echo ""
echo "🐳 ПРОВЕРКА DOCKER КОНТЕЙНЕРА:"
echo "=" * 30

if command -v docker > /dev/null 2>&1; then
    if docker compose ps | grep -q "web.*Up"; then
        echo "✅ Docker контейнер web запущен"
        
        # Проверяем переменные окружения в контейнере
        echo "🔍 Переменные окружения в контейнере:"
        docker compose exec web printenv | grep -E "FLASK_ENV|MAIL_|ADMIN_EMAIL" | head -10
    else
        echo "⚠️  Docker контейнер web не запущен или не найден"
    fi
else
    echo "⚠️  Docker не найден, проверка контейнера пропущена"
fi

echo ""
echo "✅ ДИАГНОСТИКА ЗАВЕРШЕНА"
echo "=" * 25
echo "Используйте результаты для диагностики проблем с email на production сервере." 