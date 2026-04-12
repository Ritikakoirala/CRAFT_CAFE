# Craft Cafe - Production Deployment Guide

## 🏗️ System Architecture

```
                                    ┌─────────────────────────────────────┐
                                    │          Cloudflare CDN             │
                                    │     (SSL + Caching + Firewall)    │
                                    └──────────────┬──────────────────┘
                                               │
                                    ┌───────────▼──────────────────┐
                                    │        Nginx           │
                                    │   (Reverse Proxy)    │
                                    │   Port 80/443       │
                                    └──────────┬───────────┘
                                               │
                       ┌───────────────────────┼───────────────────────┐
                       │                       │                       │
              ┌────────▼────────┐   ┌───────▼────────┐   ┌───────▼────────┐
              │   Django App     │   │  PostgreSQL   │   │    Redis     │
              │   (Gunicorn)    │   │   (DB)      │   │   (Cache)    │
              │   Port 8000     │   │   Port 5432  │   │   Port 6379  │
              └──────────────────┘   └──────────────┘   └──────────────┘
```

## 📁 Production Folder Structure

```
craft_cafe_v2/
├── .env.example          # Environment template
├── .gitignore
├── Dockerfile          # Container definition
├── docker-compose.yml  # Multi-service orchestration
├── requirements.txt   # Python dependencies
├── manage.py
├── DEPLOY.md         # This file
│
├── nginx/
│   ├── nginx.conf       # Main Nginx config
│   └── conf.d/
│       └── craft_cafe.conf  # Site config
│
├── scripts/
│   └── backup.sh       # Database backup script
│
├── static/            # Static assets (CSS/JS)
├── media/            # User uploads
├── templates/         # Django templates
├── logs/             # Application logs
│
├── craft_cafe/        # Django project
│   ├── settings.py   # Production settings
│   ├── urls.py
│   ├── wsgi.py
│   └── middleware.py  # Security middleware
│
└── cafe/            # Main application
    ├── models.py
    ├── views.py
    ├── urls.py
    └── ...
```

## 🚀 Deployment Steps

### Prerequisites
- Docker & Docker Compose installed
- Domain name with DNS configured
- Cloudflare account (free tier)

### Step 1: Clone & Configure
```bash
# Clone repository
git clone your-repo craft_cafe_v2
cd craft_cafe_v2

# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env
```

### Step 2: Generate Secure Keys
```bash
# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Add to .env as SECRET_KEY=
```

### Step 3: Build & Start
```bash
# Build container images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### Step 4: Database Setup
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Step 5: SSL Certificate (Let's Encrypt)
```bash
# Install certbot
docker pull certbot/certbot

# Generate certificate (replace domain)
docker run --rm -v ./ssl:/etc/letsencrypt certbot/certbot certonly \
  --webroot -w /app/staticfiles \
  -d craftcafe.np -d www.craftcafe.np
```

### Step 6: Verify Deployment
```bash
# Check health endpoint
curl http://localhost/health/

# View logs
docker-compose logs -f web
```

## 🔐 Security Checklist

- [x] HTTPS enforced (via Nginx)
- [x] Security headers (CSP, X-Frame-Options, etc.)
- [x] CSRF protection enabled
- [x] Rate limiting configured
- [x] Secure cookie settings
- [x] HSTS enabled
- [x] SECRET_KEY changed from default
- [x] DEBUG=False in production
- [x] ALLOWED_HOSTS configured
- [x] Database credentials secured
- [x] SSL/TLS configured

## 📊 Monitoring

### Health Check
```bash
curl http://localhost/health/
# {"status": "healthy", "service": "craft_cafe", "version": "1.0.0"}
```

### View Logs
```bash
# Application logs
docker-compose logs -f web

# Error logs
docker-compose logs web | grep ERROR
```

## 💾 Backup & Recovery

### Manual Backup
```bash
docker-compose exec db pg_dump -U postgres cafe_db > backup.sql
```

### Restore
```bash
cat backup.sql | docker-compose exec -T db psql -U postgres cafe_db
```

## 🌐 Hosting Options (Nepal Context)

| Service | Type | Cost (NPR/month) | Notes |
|---------|------|----------------|-------|
| DigitalOcean | VPS | ~1,500 | Full control |
| AWS EC2 | Cloud | ~2,000 | Scalable |
| Render | PaaS | ~1,000 | Easy deploy |
| Hetzner | VPS | ~800 | Best value |

### Recommended: DigitalOcean + Cloudflare
1. Create Droplet (Ubuntu 20.04)
2. Install Docker
3. Deploy with docker-compose
4. Point Cloudflare DNS

## 📞 Support

- Check logs: `docker-compose logs -f`
- Restart: `docker-compose restart web`
- Reload: `docker-compose exec web python manage.py migrate`