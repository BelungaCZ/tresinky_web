#!/bin/bash

# Check if we're in development environment
if [ "$FLASK_ENV" != "development" ]; then
    echo "Error: SSL certificates can only be generated in development environment"
    echo "For production, SSL certificates will be managed by Let's Encrypt"
    exit 1
fi

# Create temporary directory for certificates
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$TEMP_DIR/default.key" \
    -out "$TEMP_DIR/default.crt" \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Set proper permissions
chmod 600 "$TEMP_DIR/default.key"
chmod 644 "$TEMP_DIR/default.crt"

# Copy certificates to nginx_certs volume
echo "Copying certificates to nginx_certs volume..."
docker cp "$TEMP_DIR/default.key" nginx-proxy:/etc/nginx/certs/
docker cp "$TEMP_DIR/default.crt" nginx-proxy:/etc/nginx/certs/

echo "SSL certificates have been generated and copied to nginx_certs volume"
echo "These are self-signed certificates for development use only."
echo "For production, SSL certificates will be managed by Let's Encrypt."
echo "SSL certificates generated successfully!" 
