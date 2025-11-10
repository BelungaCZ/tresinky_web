#!/bin/bash

# Функция логирования
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - process_image.sh - $1" >> logs/processing.log
}

# Функция проверки команды
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_message "ERROR: Command '$1' not found"
        echo "Error: Command '$1' not found. Please install the required package."
        exit 1
    fi
}

log_message "INFO: Starting image processing script"

# Проверяем наличие необходимых команд
check_command "convert"
check_command "identify"

# Check if input file is provided
if [ -z "$1" ]; then
    log_message "ERROR: No input file specified"
    echo "Error: No input file specified"
    exit 1
fi

# Check if type is provided
if [ -z "$2" ]; then
    log_message "ERROR: No type specified (gallery, hero, or thumbnail)"
    echo "Error: No type specified (gallery, hero, or thumbnail)"
    exit 1
fi

# Проверяем наличие входного файла
if [ ! -f "$1" ]; then
    log_message "ERROR: Input file does not exist: $1"
    echo "Error: Input file does not exist: $1"
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

log_message "INFO: Processing file: $filename, type: $type"

# Get the album directory from the input file path
album_dir=$(dirname "$input_file")
album_name=$(basename "$album_dir")

log_message "INFO: Album name: $album_name"

# Function to process image
process_image() {
    local input="$1"
    local output="$2"
    local width="$3"
    local height="$4"
    
    log_message "INFO: Processing image $input -> $output (${width}x${height})"
    
    # Проверяем существование входного файла
    if [ ! -f "$input" ]; then
        log_message "ERROR: Input file not found: $input"
        echo "Error: Input file not found: $input"
        return 1
    fi
    
    # Check if input is HEIC
    if [[ "$input" == *.heic || "$input" == *.HEIC ]]; then
        log_message "INFO: Converting HEIC file: $input"
        
        # Проверяем наличие heif-convert
        if ! command -v "heif-convert" &> /dev/null; then
            log_message "WARNING: heif-convert not found, trying with ImageMagick"
        else
            # Convert HEIC to JPEG first
            temp_jpg="${input%.*}.jpg"
            if heif-convert "$input" "$temp_jpg" 2>/dev/null; then
                input="$temp_jpg"
                log_message "INFO: HEIC converted to JPEG: $temp_jpg"
            else
                log_message "ERROR: Failed to convert HEIC file: $input"
                echo "Error: Failed to convert HEIC file"
                return 1
            fi
        fi
    fi
    
    # Get image dimensions with error checking
    if ! dimensions=$(identify -format "%wx%h" "$input" 2>/dev/null); then
        log_message "ERROR: Failed to get image dimensions for: $input"
        echo "Error: Failed to get image dimensions"
        return 1
    fi
    
    img_width=$(echo $dimensions | cut -d'x' -f1)
    img_height=$(echo $dimensions | cut -d'x' -f2)
    
    log_message "INFO: Original dimensions: ${img_width}x${img_height}"
    
    # Проверяем валидность размеров
    if [ -z "$img_width" ] || [ -z "$img_height" ] || [ "$img_width" -eq 0 ] || [ "$img_height" -eq 0 ]; then
        log_message "ERROR: Invalid image dimensions: ${img_width}x${img_height}"
        echo "Error: Invalid image dimensions"
        return 1
    fi
    
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
    
    log_message "INFO: Target dimensions: ${new_width}x${new_height}"
    
    # Создаем директорию для выходного файла если не существует
    output_dir=$(dirname "$output")
    if [ ! -d "$output_dir" ]; then
        if ! mkdir -p "$output_dir"; then
            log_message "ERROR: Failed to create output directory: $output_dir"
            echo "Error: Failed to create output directory"
            return 1
        fi
    fi
    
    # Resize and convert to WebP while preserving orientation
    if convert "$input" -auto-orient -resize "${new_width}x${new_height}" -quality 85 "$output" 2>/dev/null; then
        log_message "INFO: Successfully processed image: $output"
        
        # Проверяем, что выходной файл был создан и имеет правильный размер
        if [ -f "$output" ] && [ -s "$output" ]; then
            log_message "INFO: Output file verified: $output"
        else
            log_message "ERROR: Output file is empty or missing: $output"
            echo "Error: Output file is empty or missing"
            return 1
        fi
    else
        log_message "ERROR: ImageMagick convert failed for: $input"
        echo "Error: ImageMagick convert failed"
        return 1
    fi
    
    # Clean up temporary JPEG if it was created from HEIC
    if [[ "$1" == *.heic || "$1" == *.HEIC ]] && [ -f "$input" ] && [[ "$input" == *.jpg ]]; then
        rm "$input" 2>/dev/null
        log_message "INFO: Cleaned up temporary JPEG: $input"
    fi
    
    return 0
}

# Process based on type
case "$type" in
    "gallery")
        # Create album directory if it doesn't exist
        if ! mkdir -p "static/images/gallery/$album_name"; then
            log_message "ERROR: Failed to create gallery album directory: static/images/gallery/$album_name"
            echo "Error: Failed to create gallery album directory"
            exit 1
        fi
        
        if process_image "$input_file" "static/images/gallery/$album_name/${name}.webp" 1200 800; then
            log_message "INFO: Gallery image processing completed successfully"
        else
            log_message "ERROR: Gallery image processing failed"
            exit 1
        fi
        ;;
    "hero")
        if process_image "$input_file" "static/images/hero/${name}.webp" 1920 1080; then
            log_message "INFO: Hero image processing completed successfully"
        else
            log_message "ERROR: Hero image processing failed"
            exit 1
        fi
        ;;
    "thumbnail")
        if process_image "$input_file" "static/images/thumbnails/${name}.webp" 400 300; then
            log_message "INFO: Thumbnail processing completed successfully"
        else
            log_message "ERROR: Thumbnail processing failed"
            exit 1
        fi
        ;;
    *)
        log_message "ERROR: Invalid type specified: $type"
        echo "Error: Invalid type specified. Use 'gallery', 'hero', or 'thumbnail'"
        exit 1
        ;;
esac

log_message "INFO: Image processing completed successfully: $filename"
echo "Image processed successfully: $filename" 