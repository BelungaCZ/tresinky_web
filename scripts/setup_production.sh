#!/bin/bash

echo "🚀 Setting up production environment..."

# Check if .env.production already exists
if [ -f .env.production ]; then
    echo "Warning: .env.production already exists!"
    echo "This script will not overwrite your existing production environment file."
    echo "If you want to create a new one, please backup and remove the existing file first."
    exit 1
fi

# Create .env.production from template
cp .env.example .env.production

# Generate and update a secure random secret key using dedicated script
echo "🔑 Generating secure secret key..."
./scripts/update_secret_key.sh production

echo "✅ Production environment file has been created!"

# Create SSL data structure for Let's Encrypt persistence
echo "🔒 Setting up SSL data structure..."

# Create ssl-data directories if they don't exist
mkdir -p ssl-data/{certs,vhost.d,html,acme}

# Set proper permissions (if running as root)
if [ "$EUID" -eq 0 ]; then
    chown -R root:root ssl-data
    chmod -R 755 ssl-data
    echo "✅ SSL directory permissions set (root:root, 755)"
else
    echo "ℹ️  SSL directories created. Set permissions manually if needed:"
    echo "   sudo chown -R root:root ssl-data && sudo chmod -R 755 ssl-data"
fi

echo "✅ SSL data structure created:"
echo "   - ssl-data/certs/    (SSL certificates and keys)"
echo "   - ssl-data/vhost.d/  (Virtual host configurations)"
echo "   - ssl-data/html/     (ACME HTTP-01 challenge files)"
echo "   - ssl-data/acme/     (Let's Encrypt account data - PERSISTENCE FIX!)"

echo ""
echo "🎉 Production environment setup completed!"
echo ""
echo "📋 Next steps:"
echo "   1. Review and update values in .env.production if needed"
echo "   2. Switch to production: ./scripts/switch_env.sh production"
echo "   3. SSL certificates will be automatically managed by Let's Encrypt"
echo ""
echo "⚠️  IMPORTANT: Keep a secure backup of .env.production file!"
echo "💾 The ssl-data/ directory will persist SSL certificates between deployments"

# Ask if user wants to test SSL configuration after setup
echo ""
read -p "🧪 Run comprehensive SSL configuration test to verify setup? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔍 Running SSL configuration test..."
    ./scripts/ssl-test.sh --quick
else
    echo "ℹ️  SSL test skipped. Run manually: ./scripts/ssl-test.sh" 