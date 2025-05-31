#!/bin/bash

# Create SSL directory if it doesn't exist
mkdir -p ssl

# Generate self-signed certificate for development
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=CZ/ST=Prague/L=Prague/O=Tresinky/CN=localhost"

echo "SSL certificates have been generated in the ssl/ directory"
echo "These are self-signed certificates for development use only."
echo "For production, SSL certificates will be managed by Let's Encrypt." 