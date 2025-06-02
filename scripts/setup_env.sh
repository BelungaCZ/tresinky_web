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

# Function to handle environment file creation
create_env_file() {
    local env_file=".env.$1"
    if [ -f "$env_file" ]; then
        read -p "Warning: $env_file already exists. Do you want to overwrite it? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Skipping $env_file creation"
            return
        fi
    fi
    
    cp .env.example "$env_file"
    if [ "$1" = "production" ]; then
        sed -i '' 's/FLASK_ENV=development/FLASK_ENV=production/' "$env_file"
    fi
    echo "Created $env_file"
}

# Create development environment file
create_env_file "development"

# Create production environment file
create_env_file "production"

echo "Environment files setup complete!"
echo "Please review and update the values in .env.development and .env.production" 