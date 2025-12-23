# Football Predictor Pro - Production Deployment Guide

## 🚀 Production-Ready Configuration

This guide will help you deploy Football Predictor Pro for millions of users with high performance, security, and scalability.

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional but recommended)
- Nginx (for reverse proxy)

## 🔧 Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp env.example .env

# Edit .env with your production values
nano .env
```

**Critical Settings:**
- `SECRET_KEY`: Generate a strong secret key (min 50 characters)
- `DEBUG=False`: Always False in production
- `ALLOWED_HOSTS`: Your domain names
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb football_predictor_prod

# Run migrations
python manage.py migrate --settings=football_predictor.settings_production

# Create database indexes
python manage.py optimize_db --settings=football_predictor.settings_production

# Create superuser
python manage.py createsuperuser --settings=football_predictor.settings_production
```

### 3. Install Dependencies

```bash
# Install production requirements
pip install -r requirements_production.txt
```

### 4. Collect Static Files

```bash
python manage.py collectstatic --noinput --settings=football_predictor.settings_production
```

## 🐳 Docker Deployment (Recommended)

### Using Docker Compose

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale web=4 --scale api=4
```

### Manual Docker Build

```bash
# Build image
docker build -t football-predictor:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -p 8001:8001 \
  --env-file .env \
  football-predictor:latest
```

## 🔒 Security Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable SSL/TLS (HTTPS)
- [ ] Set up firewall rules
- [ ] Configure rate limiting
- [ ] Enable security headers
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Set up monitoring and alerts

## 📊 Performance Optimization

### Database

- Use PostgreSQL connection pooling (pgBouncer recommended)
- Create indexes on frequently queried fields
- Run `ANALYZE` regularly
- Monitor slow queries

### Caching

- Redis for session storage and caching
- Cache frequently accessed data (team forms, predictions)
- Use cache versioning for invalidation

### Application

- Use Gunicorn with multiple workers
- Enable WhiteNoise for static files
- Use CDN for static assets
- Enable gzip compression

### Monitoring

- Set up application performance monitoring (APM)
- Monitor database query performance
- Track cache hit rates
- Monitor server resources (CPU, memory, disk)

## 🔍 Monitoring & Logging

### Log Files

- Application logs: `logs/django.log`
- Error logs: `logs/errors.log`
- Access logs: Gunicorn access logs

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health/

# Check API health
curl http://localhost:8001/health
```

### Key Metrics to Monitor

- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate
- Database connection pool usage
- Cache hit rate
- Memory usage
- CPU usage

## 📈 Scaling Strategies

### Horizontal Scaling

1. **Load Balancer**: Use Nginx or cloud load balancer
2. **Multiple Workers**: Scale Gunicorn workers based on CPU cores
3. **Multiple Instances**: Run multiple Django instances behind load balancer
4. **Database Replication**: Use PostgreSQL read replicas
5. **Redis Cluster**: For high-traffic caching

### Vertical Scaling

- Increase server resources (CPU, RAM)
- Use faster database storage (SSD)
- Optimize database queries
- Increase Redis memory

## 🛠️ Maintenance

### Regular Tasks

```bash
# Database maintenance
python manage.py optimize_db --settings=football_predictor.settings_production

# Clear old cache
python manage.py shell --settings=football_predictor.settings_production
>>> from django.core.cache import cache
>>> cache.clear()

# Backup database
pg_dump football_predictor_prod > backup_$(date +%Y%m%d).sql

# Rotate logs
logrotate /etc/logrotate.d/football-predictor
```

## 🚨 Troubleshooting

### High Memory Usage

- Reduce Gunicorn workers
- Check for memory leaks
- Increase Redis maxmemory
- Monitor query cache size

### Slow Response Times

- Check database query performance
- Verify Redis is working
- Check network latency
- Review slow query logs

### High Error Rate

- Check application logs
- Verify database connectivity
- Check Redis connectivity
- Review rate limiting settings

## 📞 Support

For production issues:
1. Check logs: `logs/django.log` and `logs/errors.log`
2. Monitor health endpoints
3. Review system resources
4. Check database and Redis status

## 🔄 Updates & Deployments

```bash
# Pull latest code
git pull origin main

# Run migrations
python manage.py migrate --settings=football_predictor.settings_production

# Collect static files
python manage.py collectstatic --noinput --settings=football_predictor.settings_production

# Restart services
docker-compose -f docker-compose.prod.yml restart
# OR
systemctl restart gunicorn
```

---

**Note**: This is a production-ready configuration. Always test in staging before deploying to production!

