# Třešinky Cetechovice Website

Modern website for the Třešinky Cetechovice association, featuring information about the orchard, gallery, donation form, and contact information.

## Features

- Responsive design
- Modern UI with animations
- Image gallery with lightbox
- Contact form
- Donation form
- Interactive elements

## Requirements

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tresinky-web.git
cd tresinky-web
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
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
```

## Running the Application

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
│   ├── img/          # Images
│   └── uploads/      # Uploaded files
├── templates/         # HTML templates
│   ├── base.html     # Base template
│   ├── home.html     # Home page
│   ├── about.html    # About page
│   ├── orchard.html  # Orchard page
│   ├── gallery.html  # Gallery page
│   ├── donate.html   # Donation page
│   └── contact.html  # Contact page
└── README.md         # This file
```

## Adding Content

### Images

1. Place images in the `static/img/` directory
2. Update image paths in templates accordingly

### Gallery

1. Place gallery images in `static/uploads/`
2. Use the admin interface to add image information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 