# Production Deployment Guide for Millions of Users

## 🚀 Quick Start - Production Mode

### 1. Install Production Dependencies

```bash
cd Football-main
pip install -r requirements_production.txt
```

### 2. Configure Environment Variables

Create a `.env` file in `Football-main/` directory:

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-min-50-characters
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_SETTINGS_MODULE=football_predictor.settings_production

# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://user:password@localhost:5432/football_predictor

# Redis (Required for caching and rate limiting)
REDIS_URL=redis://127.0.0.1:6379/1

# FastAPI Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8001
FASTAPI_WORKERS=8  # Adjust based on CPU cores (2 * cores + 1)

# Gunicorn Configuration
GUNICORN_BIND=0.0.0.0:8000
GUNICORN_WORKERS=8  # Adjust based on CPU cores

# CORS (comma-separated list of allowed origins)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 3. Start Production Servers

#### Option A: Using Production Scripts (Recommended)

**Terminal 1 - Django Server:**
```bash
python run_django_production.py
```

**Terminal 2 - FastAPI Server:**
```bash
python run_api_production.py
```

#### Option B: Using Docker Compose (Best for Production)

```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### Option C: Manual Start

**Django (Gunicorn):**
```bash
cd Football-main
gunicorn --config gunicorn_config.py football_predictor.wsgi:application
```

**FastAPI (Uvicorn):**
```bash
cd Football-main
uvicorn fastapi_predictor_production:app --host 0.0.0.0 --port 8001 --workers 8
```

## 📊 Production Features

### ✅ Implemented Features

1. **Rate Limiting**
   - 100 requests per minute per IP address
   - Redis-based rate limiting
   - Prevents abuse and ensures fair usage

2. **Redis Caching**
   - Prediction results cached for 30 minutes
   - Football data cached for 1 hour
   - Reduces database load and improves response times

3. **Connection Pooling**
   - Database connection pooling (10-minute reuse)
   - Redis connection pooling
   - Optimized for high concurrency

4. **Monitoring & Metrics**
   - `/health` - Comprehensive health check
   - `/metrics` - Performance metrics
   - Request logging and tracking
   - Cache hit rate monitoring

5. **Security**
   - CORS configuration
   - Trusted host middleware
   - SSL/TLS ready
   - Security headers

6. **Scalability**
   - Multiple worker processes
   - Async request handling
   - Non-blocking I/O
   - Horizontal scaling ready

### 📈 Performance Optimizations

- **Model Loading**: Models load in background threads (non-blocking)
- **Data Pre-loading**: Football data pre-loaded at startup
- **Async Processing**: Predictions run in thread pool to avoid blocking
- **Connection Reuse**: Database and Redis connections are pooled
- **Response Caching**: Frequently requested predictions are cached

## 🔧 Configuration

### Worker Configuration

**FastAPI Workers:**
- Default: `(CPU cores * 2) + 1`
- Maximum: 16 workers (configurable)
- Formula optimized for I/O-bound workloads

**Gunicorn Workers:**
- Default: `(CPU cores * 2) + 1`
- Worker class: `sync` (suitable for Django)
- Max requests: 1000 per worker (prevents memory leaks)

### Rate Limits

- **Predictions**: 100 requests/minute per IP
- **Health/Metrics**: No limit (but monitor for abuse)
- Configurable via Redis keys

### Cache Settings

- **Predictions**: 30 minutes TTL
- **Football Data**: 1 hour TTL
- **Redis Memory**: Configure maxmemory policy (allkeys-lru recommended)

## 📊 Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8001/health
```

Returns:
- API status
- Model loading status
- Redis connection status
- Uptime
- Basic metrics

### Metrics Endpoint

```bash
curl http://localhost:8001/metrics
```

Returns:
- Total requests
- Success/failure rates
- Cache hit rates
- Average response times
- Requests per second

### Logging

- All requests are logged with timing information
- Errors are logged with full stack traces
- Logs include IP addresses for security monitoring

## 🚨 Scaling for Millions of Users

### Horizontal Scaling

1. **Load Balancer**: Use Nginx or cloud load balancer
   ```nginx
   upstream api_backend {
       least_conn;
       server api1:8001;
       server api2:8001;
       server api3:8001;
   }
   ```

2. **Multiple API Instances**: Run multiple FastAPI instances
   ```bash
   # Instance 1
   uvicorn fastapi_predictor_production:app --port 8001 --workers 8
   
   # Instance 2
   uvicorn fastapi_predictor_production:app --port 8002 --workers 8
   
   # Instance 3
   uvicorn fastapi_predictor_production:app --port 8003 --workers 8
   ```

3. **Database Replication**: Use PostgreSQL read replicas
   - Master for writes
   - Replicas for reads

4. **Redis Cluster**: For high-traffic caching
   - Redis Sentinel for high availability
   - Redis Cluster for horizontal scaling

### Vertical Scaling

- Increase server resources (CPU, RAM)
- Use faster storage (SSD/NVMe)
- Optimize database queries
- Increase Redis memory

### Recommended Architecture

```
                    [Load Balancer]
                         |
        +----------------+----------------+
        |                |                |
   [API Instance 1] [API Instance 2] [API Instance 3]
        |                |                |
        +----------------+----------------+
                         |
        +----------------+----------------+
        |                |                |
   [PostgreSQL Master] [PostgreSQL Replica]
        |                |
   [Redis Cluster]
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
- [ ] Review CORS origins
- [ ] Use strong database passwords
- [ ] Enable Redis authentication

## 📝 Maintenance

### Regular Tasks

1. **Monitor Metrics**: Check `/metrics` endpoint regularly
2. **Database Maintenance**: Run `optimize_db` command weekly
3. **Cache Cleanup**: Monitor Redis memory usage
4. **Log Rotation**: Configure logrotate for log files
5. **Backup Database**: Daily backups recommended

### Updates

```bash
# Pull latest code
git pull origin main

# Run migrations
python manage.py migrate --settings=football_predictor.settings_production

# Collect static files
python manage.py collectstatic --noinput --settings=football_predictor.settings_production

# Restart services
# Docker:
docker-compose -f docker-compose.prod.yml restart

# Or manually:
# Stop and restart run_api_production.py and run_django_production.py
```

## 🐛 Troubleshooting

### High Memory Usage
- Reduce worker count
- Check for memory leaks
- Increase Redis maxmemory
- Monitor query cache size

### Slow Response Times
- Check database query performance
- Verify Redis is working
- Check network latency
- Review slow query logs
- Check cache hit rates

### High Error Rate
- Check application logs
- Verify database connectivity
- Check Redis connectivity
- Review rate limiting settings
- Check model loading status

## 📞 Support

For production issues:
1. Check `/health` endpoint
2. Review `/metrics` endpoint
3. Check application logs
4. Monitor system resources
5. Verify database and Redis status

---

**Note**: This configuration is optimized for production use with millions of users. Always test in staging before deploying to production!

