#!/bin/bash

# Fix nginx upstream configuration script
# Исправление проблемы с неправильным upstream в nginx-proxy

echo "🔧 Fixing nginx-proxy upstream configuration..."

# Step 0: Detect current environment
echo "🔍 Step 0: Detecting current environment..."

if [ -L .env ]; then
    CURRENT_ENV=$(readlink .env)
    if [[ "$CURRENT_ENV" == *"development"* ]]; then
        ENV_TYPE="development"
        echo "💻 Development environment detected (.env -> $CURRENT_ENV)"
    elif [[ "$CURRENT_ENV" == *"production"* ]]; then
        ENV_TYPE="production"
        echo "🌐 Production environment detected (.env -> $CURRENT_ENV)"
    else
        echo "❓ Unknown environment: .env -> $CURRENT_ENV"
        echo "❓ Defaulting to production"
        ENV_TYPE="production"
    fi
else
    echo "⚠️  No .env symlink found, defaulting to production"
    ENV_TYPE="production"
fi

# Step 1: Create nginx env files
echo "📋 Step 1: Creating nginx environment files for $ENV_TYPE..."

# Always create both files for flexibility
echo "📝 Creating .env.nginx.production..."
cat > .env.nginx.production << EOF
# Nginx configuration (БЕЗ VIRTUAL_HOST!)
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# SSL configuration
DEFAULT_HOST=sad-tresinky-cetechovice.cz
ALLOW_SELF_SIGNED=false
SSL_MODE=production

# Let's Encrypt configuration
LETSENCRYPT_EMAIL=stashok@speakasap.com

# Debug configuration
DEBUG=false
EOF

echo "📝 Creating .env.nginx.development..."
cat > .env.nginx.development << EOF
# Nginx configuration for development (БЕЗ VIRTUAL_HOST!)
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# SSL configuration for development
DEFAULT_HOST=localhost
ALLOW_SELF_SIGNED=true
SSL_MODE=development

# Let's Encrypt configuration
LETSENCRYPT_EMAIL=stashok@speakasap.com

# Debug configuration
DEBUG=true
EOF

echo "✅ Created nginx environment files for $ENV_TYPE environment"
echo "✅ Both .env.nginx.production and .env.nginx.development are ready"

# Step 2: Stop containers
echo "🛑 Step 2: Stopping containers..."
docker compose down

# Step 3: Start containers with new configuration
echo "🚀 Step 3: Starting containers with new configuration..."
docker compose up -d

# Step 4: Wait for containers to start
echo "⏳ Step 4: Waiting for containers to start..."
sleep 30

# Step 5: Check nginx upstream configuration
echo "🔍 Step 5: Checking nginx upstream configuration..."
docker compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf | grep -A10 "upstream sad-tresinky"

echo ""
echo "🎯 Fix completed for $ENV_TYPE environment! Now test the contact form:"

if [ "$ENV_TYPE" = "production" ]; then
    echo "1. Go to https://sad-tresinky-cetechovice.cz/kontakt"
else
    echo "1. Go to http://localhost:5000/kontakt or https://sad-tresinky-cetechovice.cz/kontakt"
fi

echo "2. Fill and submit the contact form"
echo "3. Check logs: docker compose logs web | grep POST"
echo "4. Check email reception"

echo ""
echo "📊 Environment: $ENV_TYPE"
echo "🔗 .env symlink: .env -> $(readlink .env 2>/dev/null || 'not found')"
echo "If the upstream shows only web container (172.18.0.2:5000), the fix is successful!" 