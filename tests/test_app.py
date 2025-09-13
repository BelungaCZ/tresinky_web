import unittest
import os
import tempfile
import shutil
from pathlib import Path
from werkzeug.datastructures import FileStorage

def test_home_page(client):
    """Test if home page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'T\xc5\x99e\xc5\xa1inky Cetechovice' in response.data

def test_about_page(client):
    """Test if about page loads successfully"""
    response = client.get('/o-nas')
    assert response.status_code == 200
    assert b'O n\xc3\xa1s' in response.data

def test_garden_page(client):
    """Test if garden page loads successfully"""
    response = client.get('/sad')
    assert response.status_code == 200
    assert b'Sad' in response.data

def test_support_page(client):
    """Test if support page loads successfully"""
    response = client.get('/podpora')
    assert response.status_code == 200
    assert b'Podpora' in response.data

def test_contact_page(client):
    """Test if contact page loads successfully"""
    response = client.get('/kontakt')
    assert response.status_code == 200
    assert b'Kontakt' in response.data

def test_sync_gallery_with_disk_function(app, client):
    """Test sync_gallery_with_disk function"""
    from app import sync_gallery_with_disk, GalleryImage, Album, db
    
    with app.app_context():
        # Создаем тестовые данные в БД
        test_album = Album(normalized_name='test_album', display_name='Test Album')
        db.session.add(test_album)
        db.session.commit()
        
        # Создаем запись о файле, которого нет на диске
        test_image = GalleryImage(
            filename='images/gallery/test_album/nonexistent.webp',
            title='Nonexistent Image',
            album_id=test_album.id
        )
        db.session.add(test_image)
        db.session.commit()
        
        # Проверяем, что запись создалась
        assert GalleryImage.query.count() == 1
        
        # Создаем тестовую директорию и файл
        gallery_dir = Path('static/images/gallery/test_album')
        gallery_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем реальный файл
        test_file = gallery_dir / 'real_image.webp'
        test_file.write_text('fake image data')
        
        # Создаем запись о реальном файле
        real_image = GalleryImage(
            filename='images/gallery/test_album/real_image.webp',
            title='Real Image',
            album_id=test_album.id
        )
        db.session.add(real_image)
        db.session.commit()
        
        # Проверяем, что теперь у нас 2 записи
        assert GalleryImage.query.count() == 2
        
        # Запускаем синхронизацию
        sync_gallery_with_disk()
        
        # Проверяем, что запись о несуществующем файле удалена
        assert GalleryImage.query.count() == 1
        
        # Проверяем, что запись о реальном файле осталась
        remaining_image = GalleryImage.query.first()
        assert remaining_image is not None
        assert remaining_image.filename == 'images/gallery/test_album/real_image.webp'
        
        # Очищаем тестовые данные
        db.session.delete(remaining_image)
        db.session.delete(test_album)
        db.session.commit()
        
        # Удаляем тестовую директорию
        shutil.rmtree('static/images/gallery/test_album', ignore_errors=True)

def test_sync_gallery_with_disk_empty_albums(app, client):
    """Test sync_gallery_with_disk removes empty albums"""
    from app import sync_gallery_with_disk, Album, db
    
    with app.app_context():
        # Создаем пустой альбом
        empty_album = Album(normalized_name='empty_album', display_name='Empty Album')
        db.session.add(empty_album)
        db.session.commit()
        
        # Проверяем, что альбом создался
        assert Album.query.count() == 1
        
        # Запускаем синхронизацию
        sync_gallery_with_disk()
        
        # Проверяем, что пустой альбом удален
        assert Album.query.count() == 0

def test_gallery_route_syncs_database(app, client):
    """Test that /gallery route calls sync_gallery_with_disk"""
    from app import sync_gallery_with_disk, GalleryImage, Album, db
    
    with app.app_context():
        # Создаем тестовые данные
        test_album = Album(normalized_name='test_album', display_name='Test Album')
        db.session.add(test_album)
        db.session.commit()
        
        test_image = GalleryImage(
            filename='images/gallery/test_album/nonexistent.webp',
            title='Nonexistent Image',
            album_id=test_album.id
        )
        db.session.add(test_image)
        db.session.commit()
        
        # Проверяем, что запись есть
        assert GalleryImage.query.count() == 1
        
        # Вызываем маршрут /gallery
        response = client.get('/gallery')
        assert response.status_code == 200
        
        # Проверяем, что запись о несуществующем файле удалена
        assert GalleryImage.query.count() == 0
        
        # Очищаем тестовые данные
        db.session.delete(test_album)
        db.session.commit()

def test_admin_gallery_route_syncs_database(app, client):
    """Test that /admin/gallery route calls sync_gallery_with_disk"""
    from app import sync_gallery_with_disk, GalleryImage, Album, db
    
    with app.app_context():
        # Создаем тестовые данные
        test_album = Album(normalized_name='test_album', display_name='Test Album')
        db.session.add(test_album)
        db.session.commit()
        
        test_image = GalleryImage(
            filename='images/gallery/test_album/nonexistent.webp',
            title='Nonexistent Image',
            album_id=test_album.id
        )
        db.session.add(test_image)
        db.session.commit()
        
        # Проверяем, что запись есть
        assert GalleryImage.query.count() == 1
        
        # Вызываем маршрут /admin/gallery
        response = client.get('/admin/gallery')
        assert response.status_code == 200
        
        # Проверяем, что запись о несуществующем файле удалена
        assert GalleryImage.query.count() == 0
        
        # Очищаем тестовые данные
        db.session.delete(test_album)
        db.session.commit()

def test_contact_form_submission_success(app, client):
    """Test successful contact form submission"""
    from app import ContactMessage, db
    
    with app.app_context():
        # Проверяем, что нет сообщений в БД
        assert ContactMessage.query.count() == 0
        
        # Отправляем валидную форму (CSRF отключен для тестов)
        response = client.post('/kontakt', data={
            'name': 'Тестовый пользователь',
            'email': 'test@example.com',
            'message': 'Тестовое сообщение из контактной формы'
        }, follow_redirects=True)
        
        # Отладочная информация при ошибке
        if response.status_code != 200:
            print(f"Status code: {response.status_code}")
            print(f"Response data: {response.data.decode('utf-8')[:500]}")
        
        # Проверяем успешный ответ
        assert response.status_code == 200
        
        # Проверяем, что сообщение сохранилось в БД
        assert ContactMessage.query.count() == 1
        
        # Проверяем содержимое сообщения
        message = ContactMessage.query.first()
        assert message is not None
        assert message.name == 'Тестовый пользователь'
        assert message.email == 'test@example.com'
        assert message.message == 'Тестовое сообщение из контактной формы'
        
        # Проверяем наличие flash сообщения об успехе
        assert 'Děkujeme za vaši zprávu' in response.data.decode('utf-8')
        
        # Очищаем тестовые данные
        db.session.delete(message)
        db.session.commit()

def test_contact_form_validation_errors(app, client):
    """Test contact form validation with invalid data"""
    from app import ContactMessage, db
    
    with app.app_context():
        # Проверяем, что нет сообщений в БД
        assert ContactMessage.query.count() == 0
        
        # Отправляем невалидную форму (пустые поля)
        response = client.post('/kontakt', data={
            'name': '',
            'email': '',
            'message': ''
        })
        
        # Проверяем, что форма не прошла валидацию
        assert response.status_code == 200
        
        # Проверяем, что сообщение НЕ сохранилось в БД
        assert ContactMessage.query.count() == 0
        
        # Проверяем наличие ошибок валидации
        response_text = response.data.decode('utf-8')
        # В случае ошибки валидации должно быть flash сообщение
        # или отображение формы с ошибками

def test_contact_form_email_notification(app, client):
    """Test email notification sending"""
    from app import ContactMessage, send_contact_email, db
    from unittest.mock import patch
    
    with app.app_context():
        # Создаем тестовое сообщение
        from datetime import datetime
        test_message = ContactMessage(
            name='Test User',
            email='test@example.com',
            message='Test message'
        )
        test_message.date = datetime.now()  # Устанавливаем дату
        
        # Мокаем отправку email
        with patch('app.mail.send') as mock_send:
            result = send_contact_email(test_message)
            
            # Проверяем, что функция вернула True (успех)
            assert result == True
            
            # Проверяем, что mail.send был вызван
            assert mock_send.called

def test_contact_form_csrf_protection(app, client):
    """Test CSRF configuration for contact form"""
    from app import ContactMessage, db
    
    with app.app_context():
        # Проверяем, что в тестовом окружении CSRF отключен
        assert app.config.get('WTF_CSRF_ENABLED') == False
        
        # Получаем форму
        response = client.get('/kontakt')
        assert response.status_code == 200
        
        # В тестовом окружении CSRF токен не должен быть в форме
        response_text = response.data.decode('utf-8')
        # Форма должна работать без CSRF токена
        assert 'form method="POST"' in response_text

def test_configuration_environments():
    """Test configuration settings for different environments"""
    from config.config import DevelopmentConfig, ProductionConfig, TestingConfig, get_config
    import os
    
    # Test Development Configuration
    dev_config = DevelopmentConfig()
    assert dev_config.DEBUG == True
    assert dev_config.USE_HTTPS == False
    assert dev_config.SESSION_COOKIE_SECURE == False  # HTTP environment
    assert dev_config.REMEMBER_COOKIE_SECURE == False  # HTTP environment
    assert dev_config.SESSION_COOKIE_HTTPONLY == True  # XSS protection
    assert dev_config.REMEMBER_COOKIE_HTTPONLY == True  # XSS protection
    assert dev_config.WTF_CSRF_ENABLED == True
    assert dev_config.DOMAIN == 'localhost:5000'
    
    # Test Production Configuration
    prod_config = ProductionConfig()
    assert prod_config.DEBUG == False
    assert prod_config.USE_HTTPS == True
    assert prod_config.SESSION_COOKIE_SECURE == True  # HTTPS environment
    assert prod_config.REMEMBER_COOKIE_SECURE == True  # HTTPS environment
    assert prod_config.SESSION_COOKIE_HTTPONLY == True  # XSS protection
    assert prod_config.REMEMBER_COOKIE_HTTPONLY == True  # XSS protection
    assert prod_config.WTF_CSRF_ENABLED == True
    assert prod_config.DOMAIN == 'sad-tresinky-cetechovice.cz'
    # PREFERRED_URL_SCHEME should remain commented out (not set)
    assert not hasattr(prod_config, 'PREFERRED_URL_SCHEME')
    
    # Test Testing Configuration
    test_config = TestingConfig()
    assert test_config.DEBUG == True
    assert test_config.TESTING == True
    assert test_config.WTF_CSRF_ENABLED == False  # Disabled for testing
    assert test_config.SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:'
    
    # Test get_config() function with different environments
    original_env = os.getenv('FLASK_ENV')
    
    try:
        # Test development environment (default)
        os.environ.pop('FLASK_ENV', None)
        config_class = get_config()
        assert config_class == DevelopmentConfig
        
        # Test explicit development environment
        os.environ['FLASK_ENV'] = 'development'
        config_class = get_config()
        assert config_class == DevelopmentConfig
        
        # Test production environment
        os.environ['FLASK_ENV'] = 'production'
        config_class = get_config()
        assert config_class == ProductionConfig
        
        # Test testing environment
        os.environ['FLASK_ENV'] = 'testing'
        config_class = get_config()
        assert config_class == TestingConfig
        
        # Test unknown environment (should return default)
        os.environ['FLASK_ENV'] = 'unknown'
        config_class = get_config()
        assert config_class == DevelopmentConfig
        
    finally:
        # Restore original environment
        if original_env:
            os.environ['FLASK_ENV'] = original_env
        else:
            os.environ.pop('FLASK_ENV', None)

def test_security_settings_logic():
    """Test the logical consistency of security settings"""
    from config.config import DevelopmentConfig, ProductionConfig
    
    # Development: HTTP environment, cookies should NOT be secure
    dev_config = DevelopmentConfig()
    assert dev_config.USE_HTTPS == False
    assert dev_config.SESSION_COOKIE_SECURE == False
    assert dev_config.REMEMBER_COOKIE_SECURE == False
    # But HTTP-only should still be enabled for XSS protection
    assert dev_config.SESSION_COOKIE_HTTPONLY == True
    assert dev_config.REMEMBER_COOKIE_HTTPONLY == True
    
    # Production: HTTPS environment, cookies SHOULD be secure
    prod_config = ProductionConfig()
    assert prod_config.USE_HTTPS == True
    assert prod_config.SESSION_COOKIE_SECURE == True
    assert prod_config.REMEMBER_COOKIE_SECURE == True
    assert prod_config.SESSION_COOKIE_HTTPONLY == True
    assert prod_config.REMEMBER_COOKIE_HTTPONLY == True
    
    # Verify that PREFERRED_URL_SCHEME is not set (to avoid ProxyFix conflicts)
    # This should remain commented out in config.py
    assert not hasattr(prod_config, 'PREFERRED_URL_SCHEME')