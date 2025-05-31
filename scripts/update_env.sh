#!/bin/bash

# Update .env.production
cat > .env.production << EOL
# Flask configuration
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=XXXXX

# Database configuration
DATABASE_URL=sqlite:///tresinky.db

# Nginx configuration
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# Domain configuration
VIRTUAL_HOST=sad-tresinky-cetechovice.cz
LETSENCRYPT_HOST=sad-tresinky-cetechovice.cz
LETSENCRYPT_EMAIL=ssfskype@gmail.com
EOL

# Create .env.development
cat > .env.development << EOL
# Flask configuration
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=dev-secret-key-here

# Database configuration
DATABASE_URL=sqlite:///tresinky.db

# Nginx configuration
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# Domain configuration
VIRTUAL_HOST=sad-tresinky-cetechovice.cz
LETSENCRYPT_HOST=sad-tresinky-cetechovice.cz
LETSENCRYPT_EMAIL=ssfskype@gmail.com
EOL

# Create .env.example
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
LETSENCRYPT_EMAIL=your-email@example.com
EOL

echo "Environment files have been updated!"
echo "Please verify the contents of .env.production, .env.development, and .env.example" 