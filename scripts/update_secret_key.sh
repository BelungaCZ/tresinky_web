#!/bin/bash

# Function to generate a secure random secret key
generate_secret_key() {
    openssl rand -hex 32
}

# Function to update secret key in environment file
update_secret_key() {
    local env_file=$1
    local new_key=$2
    
    if [ -f "$env_file" ]; then
        # Backup the original file
        cp "$env_file" "${env_file}.bak"
        
        # Update the secret key
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/^SECRET_KEY=.*/SECRET_KEY=$new_key/" "$env_file"
        else
            # Linux
            sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$new_key/" "$env_file"
        fi
        
        echo "Updated secret key in $env_file"
        echo "Backup created at ${env_file}.bak"
    else
        echo "Error: $env_file not found!"
        exit 1
    fi
}

# Check if environment argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 [development|production] [optional: existing secret key]"
    exit 1
fi

ENV=$1
EXISTING_KEY=$2

# Validate environment
if [ "$ENV" != "development" ] && [ "$ENV" != "production" ]; then
    echo "Error: Environment must be either 'development' or 'production'"
    exit 1
fi

# Generate or use existing secret key
if [ -z "$EXISTING_KEY" ]; then
    NEW_KEY=$(generate_secret_key)
    echo "Generated new secret key"
else
    NEW_KEY=$EXISTING_KEY
    echo "Using provided secret key"
fi

# Update the secret key
update_secret_key ".env.$ENV" "$NEW_KEY"

echo ""
echo "Secret key has been updated for $ENV environment"
echo "To apply the changes, restart your application:"
echo "docker compose down && docker compose up -d" 