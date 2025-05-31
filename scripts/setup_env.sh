#!/bin/bash

# Create .env.example if it doesn't exist
if [ ! -f .env.example ]; then
    cat > .env.example << EOL
# Flask configuration
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here

# Database configuration
DATABASE_URL=sqlite:///tresinky.db

# Nginx configuration
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# Domain configuration
VIRTUAL_HOST=sad-tresinky-cetechovice.cz
LETSENCRYPT_HOST=sad-tresinky-cetechovice.cz
LETSENCRYPT_EMAIL=admin@sad-tresinky-cetechovice.cz
EOL
    echo "Created .env.example"
fi

# Create development environment file
if [ ! -f .env.development ]; then
    cp .env.example .env.development
    echo "Created .env.development"
fi

# Create production environment file
if [ ! -f .env.production ]; then
    cp .env.example .env.production
    # Set production-specific values
    sed -i '' 's/FLASK_ENV=development/FLASK_ENV=production/' .env.production
    echo "Created .env.production"
fi

echo "Environment files setup complete!"
echo "Please review and update the values in .env.development and .env.production" 