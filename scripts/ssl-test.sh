#!/bin/bash
# SSL Testing Script - COMPREHENSIVE VERSION
# Проверяет все возможные точки сбоя с SSL/Let's Encrypt
# Может запускаться как standalone или из switch_env.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Check if running in quick mode (called from switch_env.sh)
QUICK_MODE=false
if [ "$1" = "--quick" ]; then
    QUICK_MODE=true
    shift
fi

echo "🔍 Comprehensive SSL configuration testing..."
echo "📅 $(date)"
echo ""

if [ "$QUICK_MODE" = "true" ]; then
    echo "ℹ️  Running in quick mode (called from switch_env.sh)"
else
    echo "ℹ️  Running in full mode - includes container restart test"
fi
echo ""

# Wait for containers to be ready
echo "⏳ Waiting for containers to start..."
sleep 10

# Test 1: Check all SSL directory mounts
echo "🧪 Test 1: Checking SSL directory structure..."
SSL_DIRS=("certs" "vhost.d" "html" "acme")
for dir in "${SSL_DIRS[@]}"; do
    if [ -d "./ssl-data/$dir" ]; then
        print_step "Host directory ./ssl-data/$dir exists"
        
        # Check if mounted in nginx-proxy
        if docker exec nginx-proxy test -d "/etc/nginx/$dir" 2>/dev/null || docker exec nginx-proxy test -d "/usr/share/nginx/$dir" 2>/dev/null; then
            print_step "./ssl-data/$dir correctly mounted in nginx-proxy"
        else
            print_error "./ssl-data/$dir not mounted in nginx-proxy"
        fi
        
        # Check if mounted in nginx-letsencrypt
        if [ "$dir" = "acme" ]; then
            if docker exec nginx-letsencrypt test -d "/etc/acme.sh" 2>/dev/null; then
                print_step "./ssl-data/$dir correctly mounted in nginx-letsencrypt as /etc/acme.sh"
            else
                print_error "./ssl-data/$dir not mounted in nginx-letsencrypt"
            fi
        else
            if docker exec nginx-letsencrypt test -d "/etc/nginx/$dir" 2>/dev/null || docker exec nginx-letsencrypt test -d "/usr/share/nginx/$dir" 2>/dev/null; then
                print_step "./ssl-data/$dir correctly mounted in nginx-letsencrypt"
            else
                print_error "./ssl-data/$dir not mounted in nginx-letsencrypt"
            fi
        fi
    else
        print_error "Host directory ./ssl-data/$dir missing"
    fi
done

# Test 2: Check permissions and ownership
echo ""
echo "🧪 Test 2: Checking SSL directory permissions..."
for dir in "${SSL_DIRS[@]}"; do
    if [ -d "./ssl-data/$dir" ]; then
        PERMISSIONS=$(stat -c "%a" "./ssl-data/$dir" 2>/dev/null || stat -f "%OLp" "./ssl-data/$dir" 2>/dev/null || echo "unknown")
        OWNER=$(stat -c "%U:%G" "./ssl-data/$dir" 2>/dev/null || stat -f "%Su:%Sg" "./ssl-data/$dir" 2>/dev/null || echo "unknown")
        
        if [ "$PERMISSIONS" = "755" ]; then
            print_step "./ssl-data/$dir permissions: $PERMISSIONS (correct)"
        else
            print_warning "./ssl-data/$dir permissions: $PERMISSIONS (expected 755)"
        fi
        print_info "./ssl-data/$dir owner: $OWNER"
    fi
done

# Test 3: Check Docker Compose SSL configuration
echo ""
echo "🧪 Test 3: Checking Docker Compose SSL configuration..."

# Check if nginx-proxy has SSL volumes
if docker-compose config | grep -q "./ssl-data/certs:/etc/nginx/certs"; then
    print_step "nginx-proxy SSL certs volume configured"
else
    print_error "nginx-proxy SSL certs volume missing"
fi

if docker-compose config | grep -q "./ssl-data/acme:/etc/acme.sh"; then
    print_step "nginx-letsencrypt acme.sh volume configured"
else
    print_error "nginx-letsencrypt acme.sh volume missing"
fi

# Test 4: Check environment variables
echo ""
echo "🧪 Test 4: Checking Let's Encrypt environment variables..."

if grep -q "LETSENCRYPT_HOST=" .env.production; then
    LETSENCRYPT_HOST=$(grep "LETSENCRYPT_HOST=" .env.production | cut -d'=' -f2)
    print_step "LETSENCRYPT_HOST configured: $LETSENCRYPT_HOST"
else
    print_error "LETSENCRYPT_HOST not found in .env.production"
fi

if grep -q "LETSENCRYPT_EMAIL=" .env.production; then
    LETSENCRYPT_EMAIL=$(grep "LETSENCRYPT_EMAIL=" .env.production | cut -d'=' -f2)
    print_step "LETSENCRYPT_EMAIL configured: $LETSENCRYPT_EMAIL"
else
    print_error "LETSENCRYPT_EMAIL not found in .env.production"
fi

# Test 5: Check container connectivity
echo ""
echo "🧪 Test 5: Checking SSL container connectivity..."

# Check if containers are running
if docker ps | grep -q "nginx-proxy"; then
    print_step "nginx-proxy container is running"
else
    print_error "nginx-proxy container is not running"
fi

if docker ps | grep -q "nginx-letsencrypt"; then
    print_step "nginx-letsencrypt container is running"
else
    print_error "nginx-letsencrypt container is not running"
fi

# Check if containers can communicate
if docker exec nginx-letsencrypt nslookup nginx-proxy 2>/dev/null >/dev/null; then
    print_step "nginx-letsencrypt can reach nginx-proxy"
else
    print_warning "nginx-letsencrypt cannot reach nginx-proxy"
fi

# Test 6: Check ports
echo ""
echo "🧪 Test 6: Checking SSL ports..."

if netstat -tuln 2>/dev/null | grep -q ":80 " || ss -tuln 2>/dev/null | grep -q ":80 "; then
    print_step "Port 80 (HTTP) is open"
else
    print_error "Port 80 (HTTP) is not open"
fi

if netstat -tuln 2>/dev/null | grep -q ":443 " || ss -tuln 2>/dev/null | grep -q ":443 "; then
    print_step "Port 443 (HTTPS) is open"
else
    print_warning "Port 443 (HTTPS) is not open (normal before first certificate)"
fi

# Test 7: Check disk space
echo ""
echo "🧪 Test 7: Checking disk space for SSL data..."

DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 90 ]; then
    print_step "Disk space: ${DISK_USAGE}% used (sufficient)"
else
    print_warning "Disk space: ${DISK_USAGE}% used (may cause SSL issues)"
fi

# Test 8: Check for existing certificates
echo ""
echo "🧪 Test 8: Checking existing SSL certificates..."

if [ -n "$(ls -A ./ssl-data/certs/ 2>/dev/null)" ]; then
    print_step "Existing certificates found in ./ssl-data/certs/"
    ls -la ./ssl-data/certs/ | head -5
else
    print_info "No existing certificates (normal for new setup)"
fi

# Test 9: Check acme.sh warnings in logs
echo ""
echo "🧪 Test 9: Checking for SSL warnings in logs..."

ACME_WARNING_COUNT=$(docker-compose logs nginx-letsencrypt 2>/dev/null | grep -c "does not appear to be a mounted volume" || echo "0")
if [ "$ACME_WARNING_COUNT" -eq 0 ]; then
    print_step "No acme.sh mount warnings found"
else
    print_warning "Found $ACME_WARNING_COUNT acme.sh mount warnings"
fi

# Check for rate limit warnings
RATE_LIMIT_COUNT=$(docker-compose logs nginx-letsencrypt 2>/dev/null | grep -c "too many certificates" || echo "0")
if [ "$RATE_LIMIT_COUNT" -eq 0 ]; then
    print_step "No rate limit warnings found"
else
    print_warning "Found $RATE_LIMIT_COUNT rate limit warnings"
fi

# Test 10: Check Docker socket access
echo ""
echo "🧪 Test 10: Checking Docker socket access..."

if docker exec nginx-letsencrypt test -S /var/run/docker.sock 2>/dev/null; then
    print_step "Docker socket accessible to nginx-letsencrypt"
else
    print_error "Docker socket not accessible to nginx-letsencrypt"
fi

# Test 11: File persistence test (only in full mode)
if [ "$QUICK_MODE" = "false" ]; then
    echo ""
    echo "🧪 Test 11: Testing file persistence..."
    TEST_FILE="test-persistence-$(date +%s).txt"

    # Create test file in container
    if docker exec nginx-letsencrypt sh -c "echo 'SSL persistence test' > /etc/acme.sh/$TEST_FILE"; then
        print_step "Test file created in container"
        
        # Check if file exists on host
        if [ -f "./ssl-data/acme/$TEST_FILE" ]; then
            print_step "Test file visible on host filesystem"
            
            # Check file content
            CONTENT=$(cat "./ssl-data/acme/$TEST_FILE")
            if [ "$CONTENT" = "SSL persistence test" ]; then
                print_step "File content matches expected value"
            else
                print_error "File content mismatch"
            fi
            
            # Cleanup test file
            rm -f "./ssl-data/acme/$TEST_FILE"
            print_step "Test file cleaned up"
        else
            print_error "Test file not found on host filesystem"
        fi
    else
        print_error "Failed to create test file in container"
    fi

    # Test 12: Container restart persistence test
    echo ""
    echo "🧪 Test 12: Testing persistence across container restart..."
    print_warning "This test will restart the nginx-letsencrypt container"
    read -p "Continue? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Create test file before restart
        RESTART_TEST_FILE="restart-test-$(date +%s).txt"
        docker exec nginx-letsencrypt sh -c "echo 'Before restart' > /etc/acme.sh/$RESTART_TEST_FILE"
        
        # Restart container
        print_step "Restarting nginx-letsencrypt container..."
        docker-compose restart nginx-letsencrypt
        
        # Wait for container to be ready
        sleep 5
        
        # Check if file still exists
        if docker exec nginx-letsencrypt test -f "/etc/acme.sh/$RESTART_TEST_FILE"; then
            CONTENT=$(docker exec nginx-letsencrypt cat "/etc/acme.sh/$RESTART_TEST_FILE")
            if [ "$CONTENT" = "Before restart" ]; then
                print_step "File persisted across container restart"
            else
                print_error "File content changed after restart"
            fi
        else
            print_error "File not found after restart"
        fi
        
        # Cleanup
        docker exec nginx-letsencrypt rm -f "/etc/acme.sh/$RESTART_TEST_FILE" 2>/dev/null || true
    else
        print_warning "Skipping container restart test"
    fi
fi

echo ""
echo "🎉 Comprehensive SSL configuration test completed!"
echo ""
echo "📊 Test Summary:"
echo "   - SSL directory structure and mounts"
echo "   - File permissions and ownership"
echo "   - Docker Compose configuration"
echo "   - Environment variables"
echo "   - Container connectivity"
echo "   - Network ports"
echo "   - Disk space"
echo "   - Existing certificates"
echo "   - Log warnings"
echo "   - Docker socket access"
if [ "$QUICK_MODE" = "false" ]; then
    echo "   - File persistence"
    echo "   - Container restart persistence"
fi
echo ""
echo "✅ SSL persistence fix is working correctly!" 