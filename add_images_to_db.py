from app import app, db, GalleryImage
import os
from datetime import datetime

def get_image_date(image_path):
    try:
        return datetime.fromtimestamp(os.path.getmtime(image_path))
    except:
        return datetime.now()

def add_images_to_db():
    upload_folder = os.path.join('static', 'uploads')
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Get all image files
        for filename in os.listdir(upload_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
                # Check if image already exists in database
                existing = GalleryImage.query.filter_by(filename=filename).first()
                if not existing:
                    # Create new database entry
                    image = GalleryImage(
                        filename=filename,
                        date=get_image_date(os.path.join(upload_folder, filename)),
                        original_date=get_image_date(os.path.join(upload_folder, filename))
                    )
                    db.session.add(image)
        
        # Commit changes
        db.session.commit()
        print("Images added to database successfully!")

if __name__ == '__main__':
    add_images_to_db() 