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

# Export environment variable
export FLASK_ENV=$ENV

# Stop existing containers
docker-compose down

# Start containers with new environment
docker-compose up -d

echo "Switched to $ENV environment"
echo "Environment variables loaded from .env.$ENV" 