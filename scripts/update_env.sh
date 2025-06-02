#!/bin/bash

# Function to handle environment file update
update_env_file() {
    local env_file=".env.$1"
    if [ -f "$env_file" ]; then
        read -p "Warning: $env_file already exists. Do you want to update it? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Skipping $env_file update"
            return
        fi
    fi
    
    # Create backup of existing file
    if [ -f "$env_file" ]; then
        cp "$env_file" "${env_file}.bak"
        echo "Created backup of existing $env_file as ${env_file}.bak"
    fi
    
    # Update environment file
    cat > "$env_file" << EOL
# Flask configuration
FLASK_ENV=$1
FLASK_APP=app.py
SECRET_KEY=$(openssl rand -hex 32)

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
    echo "Updated $env_file"
}

# Update development environment file
update_env_file "development"

# Update production environment file
update_env_file "production"

echo "Environment files update complete!"
echo "Please review the updated values in .env.development and .env.production" 