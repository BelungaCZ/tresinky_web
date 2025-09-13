#!/bin/bash

# Database Reset Script for Třešinky Cetechovice
# Completely removes and recreates the database

set -e  # Exit on any error

echo "🗄️  Database Reset Script for Třešinky Cetechovice"
echo "=================================================="

# Check if running in production environment
if [ -L ".env" ]; then
    # Check what the symlink points to
    ENV_FILE=$(readlink .env)
    if [[ "$ENV_FILE" == ".env.production" ]]; then
        echo "🌐 Production environment detected (.env -> .env.production)"
        ENV="production"
        
        # Check if Docker is available and containers are running
        if command -v docker &> /dev/null && docker compose ps | grep -q "web.*Up" 2>/dev/null; then
            echo "✅ Web container is running"
        else
            echo "⚠️  Warning: Docker not available or containers not running"
            echo "   This might be a production environment without running containers"
        fi
    else
        echo "💻 Development environment detected (.env -> $ENV_FILE)"
        ENV="development"
    fi
else
    echo "💻 Development environment detected (no .env symlink)"
    ENV="development"
fi

# Create backup directory and timestamp
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$BACKUP_TIMESTAMP"
mkdir -p "$BACKUP_DIR"

echo "📦 Creating database backup..."

# Check if database file exists and create backup
if [ "$ENV" = "production" ]; then
    if docker compose exec web test -f /app/instance/tresinky.db; then
        echo "✅ Database file found, creating backup..."
        docker compose exec web cp /app/instance/tresinky.db /app/instance/tresinky.db.backup.$BACKUP_TIMESTAMP
        docker compose cp web:/app/instance/tresinky.db.backup.$BACKUP_TIMESTAMP "$BACKUP_DIR/"
        echo "✅ Database backup created: $BACKUP_DIR/tresinky.db.backup.$BACKUP_TIMESTAMP"
    else
        echo "ℹ️  No existing database found"
    fi
else
    if [ -f "instance/tresinky.db" ]; then
        echo "✅ Database file found, creating backup..."
        cp instance/tresinky.db "$BACKUP_DIR/tresinky.db.backup.$BACKUP_TIMESTAMP"
        echo "✅ Database backup created: $BACKUP_DIR/tresinky.db.backup.$BACKUP_TIMESTAMP"
    else
        echo "ℹ️  No existing database found"
    fi
fi

echo ""
echo "🗑️  Removing existing database..."

# Remove database file
if [ "$ENV" = "production" ]; then
    docker compose exec web rm -f /app/instance/tresinky.db
    echo "✅ Database file removed from container"
else
    rm -f instance/tresinky.db
    echo "✅ Database file removed locally"
fi

echo ""
echo "🔧 Creating new database..."

# Execute reset script
echo "🚀 Executing database reset script..."
if [ "$ENV" = "production" ]; then
    # Create Python script inside the container
    docker compose exec web bash -c 'cat > /tmp/reset_db.py << "EOF"
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, "/app")

from app import app, db, Album, GalleryImage, ContactMessage
from datetime import datetime
from sqlalchemy import text

def reset_database():
    """Reset database by creating all tables"""
    print("🔧 Creating new database...")
    
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ All tables created successfully!")
            
            # Verify tables were created
            tables_to_check = ["contact_message", "album", "gallery_image"]
            for table in tables_to_check:
                result = db.session.execute(text(f"SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"{table}\""))
                if result.fetchone():
                    print(f"✅ Verified: Table \"{table}\" created")
                else:
                    print(f"❌ Error: Table \"{table}\" missing")
                    return False
            
            # Test basic operations
            print("\n🧪 Testing database operations...")
            
            # Test ContactMessage
            test_message = ContactMessage(
                name="Reset Test",
                email="test@example.com", 
                message="Database reset test"
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
            
            # Verify database is empty
            album_count = Album.query.count()
            image_count = GalleryImage.query.count()
            message_count = ContactMessage.query.count()
            
            print(f"\n📊 Database status after reset:")
            print(f"   - Albums: {album_count}")
            print(f"   - Images: {image_count}")
            print(f"   - Messages: {message_count}")
            
            if album_count == 0 and image_count == 0 and message_count == 0:
                print("✅ Database is clean and ready for use")
                return True
            else:
                print("❌ Database still contains data")
                return False
            
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = reset_database()
    sys.exit(0 if success else 1)
EOF'
    
    if docker compose exec web python3 /tmp/reset_db.py; then
        echo ""
        echo "✅ Database reset completed successfully!"
        docker compose exec web rm -f /tmp/reset_db.py
    else
        echo ""
        echo "❌ Database reset failed!"
        docker compose exec web rm -f /tmp/reset_db.py
        exit 1
    fi
else
    if python3 /tmp/reset_db.py; then
        echo ""
        echo "✅ Database reset completed successfully!"
        rm -f /tmp/reset_db.py
    else
        echo ""
        echo "❌ Database reset failed!"
        rm -f /tmp/reset_db.py
        exit 1
    fi
fi

echo ""
echo "📋 Reset Summary:"
echo "   - Database backup created in: $BACKUP_DIR"
echo "   - Old database removed"
echo "   - New database created with all tables"
echo "   - Database operations tested"
echo "   - Database is clean and ready for use"
echo ""
echo "🎉 Database reset completed!"
echo ""
echo "📝 Next steps:"
if [ "$ENV" = "production" ]; then
    echo "   1. Test the application: https://sad-tresinky-cetechovice.cz/gallery"
    echo "   2. Check logs for any errors: docker compose logs web"
    echo "   3. Start uploading new images"
else
    echo "   1. Test the application locally: http://localhost:5000/gallery"
    echo "   2. Start uploading new images"
fi
echo ""
echo "💾 Backup location: $BACKUP_DIR" 