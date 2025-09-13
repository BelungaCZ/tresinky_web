#!/usr/bin/env python3
"""
Тестовый скрипт для проверки отправки email через Flask приложение
"""

import sys
import os

# Добавляем корневую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, ContactMessage, send_contact_email
from datetime import datetime

def test_email_sending():
    """Тестирует отправку email через приложение"""
    print("🧪 ТЕСТИРОВАНИЕ ОТПРАВКИ EMAIL")
    print("=" * 40)
    
    with app.app_context():
        # Проверяем конфигурацию
        print("📋 Конфигурация приложения:")
        print(f"FLASK_ENV: {app.config.get('FLASK_ENV', 'не установлено')}")
        print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
        print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
        print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
        print(f"ADMIN_EMAIL: {app.config.get('ADMIN_EMAIL')}")
        print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        print()
        
        # Создаем тестовое сообщение
        test_message = ContactMessage(
            name="Test User",
            email="test@example.com", 
            message="Тестовое сообщение для проверки отправки email на production сервере."
        )
        test_message.date = datetime.now()
        
        print("📧 Попытка отправки тестового email...")
        
        try:
            # Тестируем отправку
            result = send_contact_email(test_message)
            
            if result:
                print("✅ Тестовый email отправлен успешно!")
                print(f"📬 Отправлено на: {app.config.get('ADMIN_EMAIL')}")
                print(f"📤 От: {app.config.get('MAIL_DEFAULT_SENDER')}")
                return True
            else:
                print("❌ Ошибка при отправке тестового email")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при отправке email: {e}")
            return False

def test_database_connection():
    """Тестирует подключение к базе данных"""
    print("\n💾 ТЕСТИРОВАНИЕ БАЗЫ ДАННЫХ")
    print("=" * 30)
    
    with app.app_context():
        try:
            # Проверяем количество сообщений
            message_count = ContactMessage.query.count()
            print(f"✅ Подключение к БД работает")
            print(f"📊 Количество сообщений в БД: {message_count}")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            return False

def main():
    """Основная функция тестирования"""
    print("🔧 ТЕСТИРОВАНИЕ EMAIL ФУНКЦИОНАЛЬНОСТИ")
    print("=" * 50)
    
    # Тестируем БД
    db_ok = test_database_connection()
    
    # Тестируем email
    email_ok = test_email_sending()
    
    print("\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 30)
    print(f"База данных: {'✅ Работает' if db_ok else '❌ Проблемы'}")
    print(f"Отправка email: {'✅ Работает' if email_ok else '❌ Проблемы'}")
    
    if db_ok and email_ok:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("Email функциональность работает корректно.")
        return 0
    else:
        print("\n⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        print("Требуется дальнейшая диагностика.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 