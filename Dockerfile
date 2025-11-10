# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for image processing
RUN apt-get update && apt-get install -y \
    build-essential \
    imagemagick \
    libmagickwand-dev \
    libheif-dev \
    libheif-examples \
    && rm -rf /var/lib/apt/lists/*

# Configure ImageMagick policy to allow the operations we need
RUN mkdir -p /etc/ImageMagick-6 && \
    { \
    echo '<policymap>'; \
    echo '  <policy domain="coder" rights="read|write" pattern="{PDF,EPHEMERAL,URL,HTTPS,MVG}" />'; \
    echo '  <policy domain="path" rights="read|write" pattern="@*" />'; \
    echo '  <policy domain="resource" name="memory" value="2GiB"/>'; \
    echo '  <policy domain="resource" name="map" value="4GiB"/>'; \
    echo '  <policy domain="resource" name="width" value="16KP"/>'; \
    echo '  <policy domain="resource" name="height" value="16KP"/>'; \
    echo '  <policy domain="resource" name="area" value="128MB"/>'; \
    echo '  <policy domain="resource" name="disk" value="4GiB"/>'; \
    echo '  <policy domain="resource" name="file" value="768"/>'; \
    echo '  <policy domain="resource" name="thread" value="2"/>'; \
    echo '  <policy domain="resource" name="throttle" value="0"/>'; \
    echo '  <policy domain="resource" name="time" value="3600"/>'; \
    echo '</policymap>'; \
    } > /etc/ImageMagick-6/policy.xml

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p static/uploads logs

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application using gunicorn config file
CMD ["sh", "-c", "if [ \"$FLASK_ENV\" = \"production\" ]; then gunicorn app:app -c gunicorn.conf.py; else python app.py; fi"] 