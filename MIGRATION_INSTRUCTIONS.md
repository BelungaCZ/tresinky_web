# Database Migration Instructions

## Проблема
На продакшене отсутствует таблица `album` в базе данных, что вызывает ошибку:
```
sqlite3.OperationalError: no such table: album
```

## Решение

### 1. Подключитесь к продакшен серверу
```bash
ssh user@your-production-server
cd /path/to/tresinky_web
```

### 2. Выполните миграцию
```bash
# Сделайте скрипт исполняемым (если нужно)
chmod +x scripts/migrate_database.sh

# Запустите миграцию
./scripts/migrate_database.sh
```

### 3. Проверьте результат
```bash
# Проверьте логи
docker compose logs web

# Протестируйте приложение
curl https://sad-tresinky-cetechovice.cz/gallery
```

## Что делает скрипт миграции

1. **Создает backup** базы данных в `backups/YYYYMMDD_HHMMSS/`
2. **Проверяет существующие таблицы** (`contact_message`, `album`, `gallery_image`)
3. **Создает недостающие таблицы** через `db.create_all()`
4. **Тестирует CRUD операции** для всех моделей
5. **Очищает тестовые данные** после проверки

## Альтернативное решение (если скрипт не работает)

```bash
# Подключитесь к контейнеру
docker compose exec web bash

# Запустите Python
python3

# В Python выполните:
from app import app, db
with app.app_context():
    db.create_all()
    print("Tables created successfully")
```

## Проверка после миграции

1. Откройте https://sad-tresinky-cetechovice.cz/gallery
2. Убедитесь, что галерея загружается без ошибок
3. Проверьте логи на наличие ошибок: `docker compose logs web`

## Troubleshooting

### Если миграция не работает:
1. Проверьте права доступа к файлам
2. Убедитесь, что контейнеры запущены
3. Проверьте логи контейнера

### Если нужно откатиться:
```bash
# Остановите контейнеры
docker compose down

# Восстановите из backup
cp backups/YYYYMMDD_HHMMSS/tresinky.db.backup.YYYYMMDD_HHMMSS instance/tresinky.db

# Запустите контейнеры
docker compose up -d
```

## Контакты
Если возникнут проблемы, проверьте логи и обратитесь к документации в `docs/database.md` 