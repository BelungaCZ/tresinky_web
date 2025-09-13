#!/bin/bash

# Database Migration Script for Třešinky Cetechovice
# Safely migrates database schema on production server

set -e  # Exit on any error

echo "🗄️  Database Migration Script for Třešinky Cetechovice"
echo "=================================================="

# Check if running in production environment
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production file not found!"
    echo "This script should be run on the production server."
    exit 1
fi

# Check if containers are running
if ! docker compose ps | grep -q "web.*Up"; then
    echo "❌ Error: Web container is not running!"
    echo "Please start the application first: docker compose up -d"
    exit 1
fi

echo "✅ Production environment detected"
echo "✅ Web container is running"

# Create backup directory
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 Creating database backup..."

# Check if database file exists
if docker compose exec web test -f /app/instance/tresinky.db; then
    echo "✅ Database file found, creating backup..."
    
    # Create backup
    docker compose exec web cp /app/instance/tresinky.db /app/instance/tresinky.db.backup.$(date +%Y%m%d_%H%M%S)
    
    # Copy backup to host
    docker compose cp web:/app/instance/tresinky.db.backup.$(date +%Y%m%d_%H%M%S) "$BACKUP_DIR/"
    
    echo "✅ Database backup created: $BACKUP_DIR/tresinky.db.backup.$(date +%Y%m%d_%H%M%S)"
else
    echo "ℹ️  No existing database found, will create new one"
fi

echo ""
echo "🔧 Starting database migration..."

# Create Python script for migration
cat > /tmp/migrate_db.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/app')

from app import app, db, Album, GalleryImage, ContactMessage
from datetime import datetime

def check_table_exists(table_name):
    """Check if table exists in database"""
    try:
        with app.app_context():
            result = db.session.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            return result.fetchone() is not None
    except Exception as e:
        print(f"Error checking table {table_name}: {e}")
        return False

def migrate_database():
    """Perform database migration"""
    print("🔍 Checking existing tables...")
    
    tables_to_check = ['contact_message', 'album', 'gallery_image']
    existing_tables = []
    
    for table in tables_to_check:
        if check_table_exists(table):
            existing_tables.append(table)
            print(f"✅ Table '{table}' exists")
        else:
            print(f"❌ Table '{table}' missing")
    
    print(f"\n📊 Found {len(existing_tables)} existing tables: {', '.join(existing_tables)}")
    
    if len(existing_tables) == len(tables_to_check):
        print("✅ All tables already exist! No migration needed.")
        return True
    
    print("\n🔧 Creating missing tables...")
    
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ All tables created successfully!")
            
            # Verify tables were created
            for table in tables_to_check:
                if check_table_exists(table):
                    print(f"✅ Verified: Table '{table}' created")
                else:
                    print(f"❌ Error: Table '{table}' still missing")
                    return False
            
            # Test basic operations
            print("\n🧪 Testing database operations...")
            
            # Test ContactMessage
            test_message = ContactMessage(
                name="Migration Test",
                email="test@example.com", 
                message="Database migration test"
            )
            db.session.add(test_message)
            db.session.commit()
            print("✅ ContactMessage operations: OK")
            
            # Test Album
            test_album = Album(
                normalized_name="test_album",
                display_name="Test Album"
            )
            db.session.add(test_album)
            db.session.commit()
            print("✅ Album operations: OK")
            
            # Test GalleryImage
            test_image = GalleryImage(
                filename="test_image.webp",
                title="Test Image",
                album_id=test_album.id
            )
            db.session.add(test_image)
            db.session.commit()
            print("✅ GalleryImage operations: OK")
            
            # Clean up test data
            db.session.delete(test_image)
            db.session.delete(test_album)
            db.session.delete(test_message)
            db.session.commit()
            print("✅ Test data cleaned up")
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
EOF

# Execute migration script in container
echo "🚀 Executing migration script..."
if docker compose exec web python3 /tmp/migrate_db.py; then
    echo ""
    echo "✅ Database migration completed successfully!"
    echo ""
    echo "📋 Migration Summary:"
    echo "   - Database backup created in: $BACKUP_DIR"
    echo "   - All tables created/verified"
    echo "   - Database operations tested"
    echo ""
    echo "🎉 Application should now work correctly!"
else
    echo ""
    echo "❌ Database migration failed!"
    echo ""
    echo "🔧 Troubleshooting steps:"
    echo "   1. Check container logs: docker compose logs web"
    echo "   2. Restore from backup if needed"
    echo "   3. Check database file permissions"
    echo "   4. Restart containers: docker compose restart web"
    exit 1
fi

# Clean up temporary file
docker compose exec web rm -f /tmp/migrate_db.py

echo ""
echo "📝 Next steps:"
echo "   1. Test the application: https://sad-tresinky-cetechovice.cz/gallery"
echo "   2. Check logs for any errors: docker compose logs web"
echo "   3. Monitor application performance"
echo ""
echo "💾 Backup location: $BACKUP_DIR" 