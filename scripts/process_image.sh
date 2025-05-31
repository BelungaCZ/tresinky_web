#!/bin/bash

# Check if input file is provided
if [ -z "$1" ]; then
    echo "Error: No input file specified"
    exit 1
fi

# Check if type is provided
if [ -z "$2" ]; then
    echo "Error: No type specified (gallery, hero, or thumbnail)"
    exit 1
fi

# Create output directories if they don't exist
mkdir -p static/images/gallery
mkdir -p static/images/hero
mkdir -p static/images/thumbnails

# Get the input file path and filename
input_file="$1"
filename=$(basename "$input_file")
name="${filename%.*}"
type="$2"

# Get the album directory from the input file path
album_dir=$(dirname "$input_file")
album_name=$(basename "$album_dir")

# Function to process image
process_image() {
    local input="$1"
    local output="$2"
    local width="$3"
    local height="$4"
    
    # Check if input is HEIC
    if [[ "$input" == *.heic || "$input" == *.HEIC ]]; then
        # Convert HEIC to JPEG first
        heif-convert "$input" "${input%.*}.jpg"
        input="${input%.*}.jpg"
    fi
    
    # Get image dimensions
    dimensions=$(identify -format "%wx%h" "$input")
    img_width=$(echo $dimensions | cut -d'x' -f1)
    img_height=$(echo $dimensions | cut -d'x' -f2)
    
    # Calculate new dimensions while preserving aspect ratio
    if [ $img_width -gt $img_height ]; then
        # Landscape image
        new_width=$width
        new_height=$((width * img_height / img_width))
    else
        # Portrait image
        new_height=$height
        new_width=$((height * img_width / img_height))
    fi
    
    # Resize and convert to WebP while preserving orientation
    convert "$input" -auto-orient -resize "${new_width}x${new_height}" -quality 85 "$output"
    
    # Clean up temporary JPEG if it was created from HEIC
    if [[ "$1" == *.heic || "$1" == *.HEIC ]]; then
        rm "$input"
    fi
}

# Process based on type
case "$type" in
    "gallery")
        # Create album directory if it doesn't exist
        mkdir -p "static/images/gallery/$album_name"
        process_image "$input_file" "static/images/gallery/$album_name/${name}.webp" 1200 800
        ;;
    "hero")
        process_image "$input_file" "static/images/hero/${name}.webp" 1920 1080
        ;;
    "thumbnail")
        process_image "$input_file" "static/images/thumbnails/${name}.webp" 400 300
        ;;
    *)
        echo "Error: Invalid type specified. Use 'gallery', 'hero', or 'thumbnail'"
        exit 1
        ;;
esac

echo "Image processed successfully: $filename" 