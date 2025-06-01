#!/bin/bash

# Check if environment is development
if [ "$FLASK_ENV" != "development" ]; then
    echo "Error: SSL certificates should only be generated in development environment"
    echo "For production, SSL certificates are managed by Let's Encrypt"
    exit 1
fi

# Create SSL directory if it doesn't exist
mkdir -p ssl

# Generate self-signed certificate for development
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=CZ/ST=Czech Republic/L=Prague/O=Tresinky/CN=localhost"

# Set proper permissions
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

echo "SSL certificates have been generated in the ssl/ directory"
echo "These are self-signed certificates for development use only."
echo "For production, SSL certificates will be managed by Let's Encrypt." 

echo "SSL certificates generated successfully!" 
