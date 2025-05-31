# Třešinky Cetechovice Website

Modern website for the Třešinky Cetechovice association, featuring information about the orchard, gallery, donation form, and contact information.

## Features

- Responsive design
- Modern UI with animations
- Image gallery with lightbox
- Contact form
- Donation form
- Interactive elements
- User authentication
- Personal cabinet
- Admin panel

## Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Docker (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tresinky-web.git
cd tresinky-web
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root with the following variables:
```
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

2. Create necessary directories:
```bash
mkdir -p static/uploads
mkdir -p static/images
```

## Running the Application

### Using Docker

1. Build and run using Docker Compose:
```bash
docker-compose up --build
```

### Local Development

1. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

2. Run the development server:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## Project Structure

```
tresinky_web/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── static/            # Static files
│   ├── css/          # CSS files
│   ├── js/           # JavaScript files
│   ├── images/       # Website images (webp format)
│   └── uploads/      # User uploaded files
├── templates/         # HTML templates
├── auth_service/      # Authentication service
├── personal_cabinet/  # User cabinet functionality
├── tests/            # Test files
└── README.md         # This file
```

## Image Guidelines

### Website Images
- Place all website images in `static/images/`
- Use .webp format for better performance
- Recommended image dimensions:
  - Gallery thumbnails: 400x300px
  - Full gallery images: 1200x800px
  - Hero images: 1920x1080px
- Optimize images before uploading

### Gallery Images
- Upload gallery images through the admin interface
- Images will be automatically processed and stored in `static/uploads/`
- Supported formats: JPG, PNG, WEBP
- Maximum file size: 5MB

## Testing

Run tests using:
```bash
./run_tests.sh
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 