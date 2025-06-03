#!/bin/bash

# Check if environment argument is provided
if [ -z "$1" ]; then
    echo "Usage: ./switch_env.sh [development|production]"
    exit 1
fi

ENV=$1

# Validate environment
if [ "$ENV" != "development" ] && [ "$ENV" != "production" ]; then
    echo "Error: Environment must be either 'development' or 'production'"
    exit 1
fi

# Check if environment file exists
if [ ! -f ".env.$ENV" ]; then
    echo "Error: .env.$ENV file not found!"
    echo "Please run ./scripts/setup_env.sh first to create environment files."
    exit 1
fi

# Create symlink to the appropriate environment file
ln -sf ".env.$ENV" .env

# Export environment variable
export FLASK_ENV=$ENV

# Stop existing containers
docker compose down

# Start containers with new environment
docker compose up -d

echo "✅ Switched to $ENV environment"
echo "Environment variables are now loaded from .env.$ENV"
