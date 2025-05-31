#!/bin/bash

# Check if .env.production already exists
if [ -f .env.production ]; then
    echo "Warning: .env.production already exists!"
    echo "This script will not overwrite your existing production environment file."
    echo "If you want to create a new one, please backup and remove the existing file first."
    exit 1
fi

# Create .env.production from template
cp .env.example .env.production

# Generate a secure random secret key
SECRET_KEY=$(openssl rand -hex 32)

# Update the secret key in .env.production
sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env.production

echo "Production environment file has been created!"
echo "Please review and update any other values in .env.production if needed."
echo "IMPORTANT: This file will not be committed to the repository."
echo "Make sure to keep a secure backup of this file!" 