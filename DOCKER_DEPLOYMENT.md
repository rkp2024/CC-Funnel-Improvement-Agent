# 🐳 Docker Deployment Guide
## Jupiter Edge+ Credit Card Agent API

---

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space

### Install Docker (Ubuntu/Debian)

```bash
# Update package index
sudo apt update

# Install dependencies
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

---

## 🚀 Quick Start

### 1. Configure Environment

```bash
cd /home/ubuntu/rohit/Funnel-Improvement-main

# Copy environment template
cp env.example .env

# Edit configuration
nano .env
```

**Required variables:**
```env
# API Configuration
API_KEY=your_secure_api_key_here

# WhatsApp Configuration
WHATSAPP_VERIFY_TOKEN=your_verify_token
WHATSAPP_APP_SECRET=your_app_secret

# Hugging Face
HF_TOKEN=your_hf_token_here
```

### 2. Build and Run

```bash
# Build the Docker image
docker compose build

# Start the container
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

**Expected Output:**
```
✅ API Server started successfully!
📍 Documentation available at: http://localhost:8000/docs
```

### 3. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# Test API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"user_id": "test123", "message": "Hi"}'
```

---

## 📦 Docker Commands Reference

### Container Management

```bash
# Start containers
docker compose up -d

# Stop containers
docker compose down

# Restart containers
docker compose restart

# View running containers
docker compose ps

# View logs (follow mode)
docker compose logs -f

# View logs for specific service
docker compose logs -f jupiter-api

# Execute command in container
docker compose exec jupiter-api bash

# View resource usage
docker stats
```

### Image Management

```bash
# Build image
docker compose build

# Build without cache
docker compose build --no-cache

# Pull latest base images
docker compose pull

# List images
docker images

# Remove unused images
docker image prune -a
```

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect funnel-improvement-main_logs

# Remove unused volumes
docker volume prune
```

---

## 🔧 Configuration

### Environment Variables

All configuration is done via `.env` file:

```env
# ==================== API Configuration ====================
API_KEY=your_secure_random_key_here
API_PORT=8000
API_HOST=0.0.0.0

# ==================== WhatsApp Configuration ====================
WHATSAPP_VERIFY_TOKEN=your_webhook_verify_token
WHATSAPP_APP_SECRET=your_meta_app_secret
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token

# ==================== Hugging Face Configuration ====================
HF_TOKEN=your_huggingface_token

# ==================== Environment ====================
ENVIRONMENT=production
```

### Port Configuration

To change the exposed port, edit `docker-compose.yml`:

```yaml
ports:
  - "8080:8000"  # Host:Container
```

### Resource Limits

Add resource constraints in `docker-compose.yml`:

```yaml
services:
  jupiter-api:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

---

## 🌐 Production Deployment

### Option 1: Direct Exposure (Simple)

```bash
# Expose port 8000
docker compose up -d

# Configure firewall
sudo ufw allow 8000/tcp
```

**Access:** `http://your-server-ip:8000`

### Option 2: Nginx Reverse Proxy (Recommended)

#### 1. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/jupiter-api
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logging
    access_log /var/log/nginx/jupiter-api-access.log;
    error_log /var/log/nginx/jupiter-api-error.log;

    # Proxy to Docker container
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint (no auth)
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
```

#### 2. Enable Site

```bash
# Enable configuration
sudo ln -s /etc/nginx/sites-available/jupiter-api /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

#### 3. Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

### Option 3: Docker Compose with Nginx

Uncomment the nginx service in `docker-compose.yml` and create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream jupiter_api {
        server jupiter-api:8000;
    }

    server {
        listen 80;
        server_name _;

        location / {
            proxy_pass http://jupiter_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

Then run:
```bash
docker compose up -d
```

---

## 📊 Monitoring & Logging

### View Logs

```bash
# All logs
docker compose logs -f

# Last 100 lines
docker compose logs --tail=100

# Logs since 1 hour ago
docker compose logs --since 1h

# Export logs to file
docker compose logs > logs/docker-$(date +%Y%m%d).log
```

### Monitor Resources

```bash
# Real-time stats
docker stats jupiter-edge-api

# Container details
docker inspect jupiter-edge-api

# Health status
docker compose ps
```

### Log Rotation

Logs are automatically rotated (configured in `docker-compose.yml`):
- Max size: 10MB per file
- Max files: 3
- Total max: 30MB

### Application Logs

Application logs are persisted in `./logs/` directory:

```bash
# View API logs
tail -f logs/api_server.log

# Search for errors
grep "ERROR" logs/api_server.log

# Count requests
grep "POST /api/chat" logs/api_server.log | wc -l
```

---

## 🔒 Security Best Practices

### 1. Use Strong API Keys

```bash
# Generate secure API key
openssl rand -hex 32
```

Update `.env`:
```env
API_KEY=generated_secure_key_here
```

### 2. Limit Network Exposure

```bash
# Only expose to localhost
# In docker-compose.yml:
ports:
  - "127.0.0.1:8000:8000"
```

### 3. Run as Non-Root User

Already configured in `Dockerfile`:
```dockerfile
USER appuser
```

### 4. Keep Images Updated

```bash
# Pull latest base images
docker compose pull

# Rebuild
docker compose build --no-cache

# Restart
docker compose up -d
```

### 5. Scan for Vulnerabilities

```bash
# Scan image
docker scan jupiter-edge-api

# Or use Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image jupiter-edge-api
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs jupiter-api

# Check container status
docker compose ps

# Inspect container
docker inspect jupiter-edge-api
```

**Common issues:**
- Port 8000 already in use: Change port in `docker-compose.yml`
- Missing environment variables: Check `.env` file
- Insufficient resources: Check `docker stats`

### API Returns 503 Service Unavailable

```bash
# Check if agent initialized
docker compose logs | grep "Agent Engine"

# Check data files
docker compose exec jupiter-api ls -la app/data/
docker compose exec jupiter-api ls -la app/rag/
```

**Fix:**
- Ensure `card_data.json` exists in both locations
- Restart container: `docker compose restart`

### High Memory Usage

```bash
# Check memory
docker stats jupiter-edge-api

# Add memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

### Logs Not Persisting

```bash
# Check volume
docker volume inspect funnel-improvement-main_logs

# Ensure logs directory exists
mkdir -p logs
chmod 777 logs

# Restart container
docker compose down && docker compose up -d
```

### Cannot Connect to API

```bash
# Check if container is running
docker compose ps

# Check port binding
docker compose port jupiter-api 8000

# Test from inside container
docker compose exec jupiter-api curl http://localhost:8000/health

# Check firewall
sudo ufw status
sudo ufw allow 8000/tcp
```

---

## 🔄 Updates & Maintenance

### Update Application Code

```bash
# Pull latest code
git pull origin main

# Rebuild image
docker compose build

# Restart with new image
docker compose up -d

# Verify
curl http://localhost:8000/health
```

### Update Dependencies

```bash
# Update requirements.txt
nano requirements.txt

# Rebuild without cache
docker compose build --no-cache

# Restart
docker compose up -d
```

### Backup Data

```bash
# Backup logs
tar -czf backup-logs-$(date +%Y%m%d).tar.gz logs/

# Backup environment
cp .env .env.backup

# Backup data
tar -czf backup-data-$(date +%Y%m%d).tar.gz app/data/ app/rag/
```

### Restore from Backup

```bash
# Restore logs
tar -xzf backup-logs-20260212.tar.gz

# Restore environment
cp .env.backup .env

# Restore data
tar -xzf backup-data-20260212.tar.gz
```

---

## 📈 Scaling

### Horizontal Scaling (Multiple Instances)

```yaml
# docker-compose.yml
services:
  jupiter-api:
    # ... existing config ...
    deploy:
      replicas: 3
```

### Load Balancing with Nginx

```nginx
upstream jupiter_cluster {
    least_conn;
    server jupiter-api-1:8000;
    server jupiter-api-2:8000;
    server jupiter-api-3:8000;
}

server {
    location / {
        proxy_pass http://jupiter_cluster;
    }
}
```

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml jupiter

# Scale service
docker service scale jupiter_jupiter-api=3

# View services
docker service ls
```

---

## 🧪 Testing in Docker

### Run Tests Inside Container

```bash
# Execute bash in container
docker compose exec jupiter-api bash

# Inside container, run tests
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"user_id": "test", "message": "hi"}'
```

### Test from Host

```bash
# Health check
curl http://localhost:8000/health

# Full API test
bash test_api.sh
```

---

## 📞 Support

### Useful Commands

```bash
# Container shell
docker compose exec jupiter-api bash

# View environment variables
docker compose exec jupiter-api env

# Check disk usage
docker system df

# Clean up everything
docker system prune -a --volumes
```

### Get Help

```bash
# Docker help
docker --help
docker compose --help

# View API documentation
# Open browser: http://localhost:8000/docs
```

---

**Last Updated:** Feb 12, 2026  
**Version:** 1.0.0
