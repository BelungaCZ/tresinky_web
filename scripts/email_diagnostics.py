#!/usr/bin/env python3
"""
Email Configuration Diagnostics Script
Проверяет настройки email на production сервере
"""

import os
import sys
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

def check_environment():
    """Проверка переменных окружения"""
    print("🔍 ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
    print("=" * 50)
    
    # Проверяем загрузку .env файла
    env_file = '.env'
    if os.path.exists(env_file):
        if os.path.islink(env_file):
            link_target = os.readlink(env_file)
            print(f"✅ .env файл найден (symlink -> {link_target})")
        else:
            print(f"✅ .env файл найден (обычный файл)")
        load_dotenv(env_file)
    else:
        print("❌ .env файл не найден")
        return False
    
    # Проверяем основные переменные
    required_vars = [
        'FLASK_ENV',
        'MAIL_SERVER', 
        'MAIL_PORT',
        'MAIL_USE_TLS',
        'MAIL_USERNAME',
        'MAIL_PASSWORD',
        'MAIL_DEFAULT_SENDER',
        'ADMIN_EMAIL'
    ]
    
    all_vars_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Скрываем пароль в выводе
            if var == 'MAIL_PASSWORD':
                print(f"✅ {var} = {'*' * len(value)}")
            else:
                print(f"✅ {var} = {value}")
        else:
            print(f"❌ {var} = НЕ УСТАНОВЛЕНО")
            all_vars_ok = False
    
    return all_vars_ok

def check_network_connectivity():
    """Проверка сетевого подключения к Gmail SMTP"""
    print("\n🌐 ПРОВЕРКА СЕТЕВОГО ПОДКЛЮЧЕНИЯ")
    print("=" * 50)
    
    mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = int(os.getenv('MAIL_PORT', 587))
    
    try:
        print(f"🔌 Проверка подключения к {mail_server}:{mail_port}...")
        socket.setdefaulttimeout(10)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((mail_server, mail_port))
        sock.close()
        
        if result == 0:
            print(f"✅ Подключение к {mail_server}:{mail_port} успешно")
            return True
        else:
            print(f"❌ Не удается подключиться к {mail_server}:{mail_port}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при проверке подключения: {e}")
        return False

def check_smtp_auth():
    """Проверка SMTP аутентификации"""
    print("\n🔐 ПРОВЕРКА SMTP АУТЕНТИФИКАЦИИ")
    print("=" * 50)
    
    mail_server = os.getenv('MAIL_SERVER')
    mail_port = int(os.getenv('MAIL_PORT', 587))
    mail_username = os.getenv('MAIL_USERNAME')
    mail_password = os.getenv('MAIL_PASSWORD')
    mail_use_tls = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    
    if not mail_server or not mail_username or not mail_password:
        print("❌ Отсутствуют необходимые параметры для SMTP")
        return False
    
    try:
        print(f"📧 Подключение к SMTP серверу {mail_server}:{mail_port}...")
        server = smtplib.SMTP(mail_server, mail_port)
        server.set_debuglevel(1)  # Включаем debug для подробного вывода
        
        if mail_use_tls:
            print("🔒 Включение TLS...")
            server.starttls()
        
        print("🔑 Попытка аутентификации...")
        server.login(mail_username, mail_password)
        
        print("✅ SMTP аутентификация прошла успешно")
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Ошибка аутентификации SMTP: {e}")
        print("💡 Проверьте правильность логина/пароля и настройки 2FA")
        return False
    except Exception as e:
        print(f"❌ Общая ошибка SMTP: {e}")
        return False

def send_test_email():
    """Отправка тестового email"""
    print("\n📮 ОТПРАВКА ТЕСТОВОГО EMAIL")
    print("=" * 50)
    
    mail_server = os.getenv('MAIL_SERVER')
    mail_port = int(os.getenv('MAIL_PORT', 587))
    mail_username = os.getenv('MAIL_USERNAME')
    mail_password = os.getenv('MAIL_PASSWORD')
    mail_default_sender = os.getenv('MAIL_DEFAULT_SENDER')
    admin_email = os.getenv('ADMIN_EMAIL')
    mail_use_tls = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    
    if not mail_server or not mail_username or not mail_password or not mail_default_sender or not admin_email:
        print("❌ Отсутствуют необходимые параметры для отправки email")
        return False
    
    try:
        # Создаем тестовое сообщение
        msg = MIMEMultipart()
        msg['From'] = mail_default_sender
        msg['To'] = admin_email
        msg['Subject'] = 'Тест email настроек - Třešinky Cetechovice'
        
        body = """
        Это тестовое сообщение для проверки настроек email.
        
        Если вы получили это сообщение, email настройки работают корректно.
        
        Отправлено из скрипта диагностики email.
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Отправляем
        server = smtplib.SMTP(mail_server, mail_port)
        if mail_use_tls:
            server.starttls()
        server.login(mail_username, mail_password)
        
        text = msg.as_string()
        server.sendmail(mail_default_sender, admin_email, text)
        server.quit()
        
        print(f"✅ Тестовый email отправлен на {admin_email}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при отправке тестового email: {e}")
        return False

def main():
    """Основная функция диагностики"""
    print("🔧 ДИАГНОСТИКА EMAIL НАСТРОЕК")
    print("=" * 50)
    print(f"Время запуска: {os.popen('date').read().strip()}")
    print(f"Рабочая директория: {os.getcwd()}")
    print()
    
    results = []
    
    # Проверяем переменные окружения
    results.append(("Переменные окружения", check_environment()))
    
    # Проверяем сетевое подключение
    results.append(("Сетевое подключение", check_network_connectivity()))
    
    # Проверяем SMTP аутентификацию
    results.append(("SMTP аутентификация", check_smtp_auth()))
    
    # Отправляем тестовый email
    results.append(("Отправка тестового email", send_test_email()))
    
    # Итоговый отчет
    print("\n📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 50)
    
    all_ok = True
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name}: {status}")
        if not result:
            all_ok = False
    
    print()
    if all_ok:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print("Email настройки работают корректно.")
    else:
        print("⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        print("Требуется исправление настроек email.")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main()) 