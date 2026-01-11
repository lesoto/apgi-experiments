# APGI Framework Deployment Guide

## 🎯 Overview

This comprehensive guide covers all aspects of deploying the APGI Framework, from simple local setups to production environments.

---

## 📋 Table of Contents

1. [Deployment Options](#deployment-options)
2. [Quick Deploy (Recommended for Beginners)](#quick-deploy)
3. [Manual Docker Deployment](#manual-docker-deployment)
4. [Advanced Deployment](#advanced-deployment)
5. [Production Deployment](#production-deployment)
6. [Configuration Management](#configuration-management)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting Deployment](#troubleshooting-deployment)

---

## 🚀 Deployment Options

### Option 1: Quick Deploy (Recommended)
- **Best for**: Beginners, testing, development
- **Complexity**: Low
- **Time**: 5-10 minutes
- **Requirements**: Docker Desktop

### Option 2: Manual Docker
- **Best for**: Custom configurations, learning
- **Complexity**: Medium
- **Time**: 15-30 minutes
- **Requirements**: Docker, command line comfort

### Option 3: Advanced Deployment
- **Best for**: Production, multi-environment
- **Complexity**: High
- **Time**: 30-60 minutes
- **Requirements**: Docker, networking knowledge

### Option 4: Cloud Deployment
- **Best for**: Scalability, remote access
- **Complexity**: High
- **Time**: 1-2 hours
- **Requirements**: Cloud account, DevOps knowledge

---

## ⚡ Quick Deploy

### Prerequisites Check

Before starting, verify:

```bash
# Check Docker
docker --version
docker-compose --version

# Check Python (optional)
python --version
```

### One-Click Deployment

1. **Download the Framework**
   ```bash
   git clone https://github.com/your-org/apgi-experiments.git
   cd apgi-experiments
   ```

2. **Run Quick Deploy**
   ```bash
   python quick_deploy.py
   ```

3. **Follow Interactive Setup**
   - Environment selection (Development/Production)
   - Port configuration
   - Data directory setup
   - Backup preferences

4. **Access Your Framework**
   - Web Interface: `http://localhost:8000`
   - Monitoring: `http://localhost:8000/monitoring`

### Quick Deploy Commands

```bash
# Check deployment status
python quick_deploy.py status

# View logs
python quick_deploy.py logs

# Stop deployment
python quick_deploy.py stop

# Restart deployment
python quick_deploy.py deploy

# Get help
python quick_deploy.py help
```

---

## 🐳 Manual Docker Deployment

### Step 1: Environment Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-org/apgi-experiments.git
   cd apgi-experiments
   ```

2. **Create Environment File**
   ```bash
   cp .env.example .env
   ```

3. **Edit Environment Variables**
   ```bash
   nano .env
   ```

   Essential variables:
   ```env
   APGI_ENV=production
   APGI_LOG_LEVEL=INFO
   APGUI_THEME=dark
   APGI_SECRET_KEY=your-secret-key-here
   ```

### Step 2: Docker Configuration

1. **Review Docker Compose**
   ```bash
   cat docker-compose.yml
   ```

2. **Customize if Needed**
   - Change ports
   - Add volumes
   - Modify environment variables

3. **Build and Deploy**
   ```bash
   docker-compose up -d --build
   ```

### Step 3: Verify Deployment

1. **Check Container Status**
   ```bash
   docker-compose ps
   ```

2. **View Logs**
   ```bash
   docker-compose logs -f
   ```

3. **Access Application**
   - Navigate to configured port
   - Verify functionality

---

## 🔧 Advanced Deployment

### Multi-Environment Setup

1. **Create Environment Configurations**
   ```bash
   mkdir -p config/environments
   ```

2. **Development Environment**
   ```yaml
   # config/environments/development.yaml
   environment: development
   docker_tag: dev
   ports:
     "8000": 8000
   environment_vars:
     APGI_DEBUG: true
     APGI_LOG_LEVEL: DEBUG
   monitoring_enabled: true
   ```

3. **Production Environment**
   ```yaml
   # config/environments/production.yaml
   environment: production
   docker_tag: latest
   ports:
     "8000": 80
   environment_vars:
     APGI_DEBUG: false
     APGI_LOG_LEVEL: INFO
   backup_enabled: true
   auto_restart: true
   ```

### Automated Deployment Script

1. **Create Deployment Script**
   ```bash
   #!/bin/bash
   # deploy.sh
   
   ENVIRONMENT=${1:-production}
   CONFIG_FILE="config/environments/${ENVIRONMENT}.yaml"
   
   echo "Deploying to ${ENVIRONMENT}..."
   
   # Validate configuration
   python -m apgi_framework.deployment.cli validate-config --config $CONFIG_FILE
   
   # Deploy
   python -m apgi_framework.deployment.cli deploy --config $CONFIG_FILE
   
   # Health check
   python -m apgi_framework.deployment.cli health-check --wait 60
   ```

2. **Make Executable**
   ```bash
   chmod +x deploy.sh
   ```

3. **Deploy**
   ```bash
   ./deploy.sh production
   ```

### Rolling Updates

1. **Zero-Downtime Deployment**
   ```bash
   # Deploy new version alongside old
   docker-compose up -d --scale apgi-framework=2
   
   # Wait for health check
   python -m apgi_framework.deployment.cli health-check --wait 30
   
   # Remove old container
   docker-compose up -d --scale apgi-framework=1
   ```

2. **Rollback if Needed**
   ```bash
   # Tag previous version
   docker tag apgi-framework:previous apgi-framework:rollback
   
   # Deploy rollback
   docker-compose up -d --force-recreate
   ```

---

## 🏭 Production Deployment

### Security Configuration

1. **Generate Secure Keys**
   ```bash
   # Generate secret key
   openssl rand -hex 32
   
   # Generate SSL certificates (optional)
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
   ```

2. **Configure HTTPS**
   ```yaml
   # docker-compose.prod.yml
   services:
     nginx:
       image: nginx:alpine
       ports:
         - "443:443"
         - "80:80"
       volumes:
         - ./nginx/nginx.conf:/etc/nginx/nginx.conf
         - ./nginx/ssl:/etc/nginx/ssl
   ```

3. **Network Security**
   ```yaml
   networks:
     apgi-network:
       driver: bridge
       internal: false
       ipam:
         config:
           - subnet: 172.20.0.0/16
   ```

### Performance Optimization

1. **Resource Limits**
   ```yaml
   services:
     apgi-framework:
       deploy:
         resources:
           limits:
             cpus: '2.0'
             memory: 4G
           reservations:
             cpus: '1.0'
             memory: 2G
   ```

2. **Caching Configuration**
   ```yaml
   redis:
     image: redis:7-alpine
     command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
   ```

3. **Database Optimization**
   ```yaml
   postgres:
     environment:
       POSTGRES_SHARED_PRELOAD_LIBRARIES: pg_stat_statements
       POSTGRES_MAX_CONNECTIONS: 100
     command: >
       postgres
       -c shared_preload_libraries=pg_stat_statements
       -c max_connections=100
       -c shared_buffers=256MB
       -c effective_cache_size=1GB
   ```

### Backup Strategy

1. **Automated Backups**
   ```bash
   #!/bin/bash
   # backup.sh
   
   DATE=$(date +%Y%m%d_%H%M%S)
   BACKUP_DIR="backups/${DATE}"
   
   mkdir -p $BACKUP_DIR
   
   # Backup data
   docker exec apgi-postgres pg_dump -U apgi_user apgi_db > $BACKUP_DIR/database.sql
   
   # Backup files
   docker cp apgi-framework:/app/data $BACKUP_DIR/
   docker cp apgi-framework:/app/apgi_outputs $BACKUP_DIR/
   
   # Compress
   tar -czf "${BACKUP_DIR}.tar.gz" -C backups $DATE
   rm -rf $BACKUP_DIR
   
   # Cleanup old backups (keep 7 days)
   find backups -name "*.tar.gz" -mtime +7 -delete
   ```

2. **Schedule Backups**
   ```bash
   # Add to crontab
   0 2 * * * /path/to/backup.sh
   ```

---

## ⚙️ Configuration Management

### Environment Variables

| Variable | Description | Default | Required |
|-----------|-------------|----------|----------|
| `APGI_ENV` | Environment type | `development` | No |
| `APGI_DEBUG` | Debug mode | `false` | No |
| `APGI_LOG_LEVEL` | Logging level | `INFO` | No |
| `APGI_SECRET_KEY` | Security key | auto-generated | Yes |
| `APGUI_THEME` | GUI theme | `dark` | No |
| `APGI_MAX_WORKERS` | Worker processes | `4` | No |

### Configuration Files

1. **Main Configuration** (`config.yaml`)
   ```yaml
   apgi_framework:
     version: "1.0"
     environment: production
     
   parameters:
     theta0:
       default: 0.5
       range: [0.1, 2.0]
       prior: normal(0.5, 0.2)
   
   database:
     type: postgresql
     host: postgres
     port: 5432
     name: apgi_framework
     user: apgi_user
     password: ${POSTGRES_PASSWORD}
   
   monitoring:
     enabled: true
     metrics_port: 9090
     health_check_interval: 30
   ```

2. **User Preferences** (`user_preferences.yaml`)
   ```yaml
   gui:
     theme: dark
     font_size: 12
     window_size: [1400, 900]
   
   analysis:
     default_trials: 1000
     auto_save: true
     show_warnings: true
   
   data:
     auto_backup: true
     backup_interval: 24  # hours
     compression: true
   ```

### Validation

1. **Validate Configuration**
   ```bash
   python -m apgi_framework.deployment.cli validate-config
   ```

2. **Test Configuration**
   ```bash
   python -m apgi_framework.deployment.cli test-config --environment production
   ```

---

## 📊 Monitoring and Maintenance

### Health Monitoring

1. **Built-in Health Checks**
   ```bash
   # Check application health
   python -m apgi_framework.deployment.cli health-check
   
   # Detailed health report
   python -m apgi_framework.deployment.cli health-check --detailed
   ```

2. **Custom Health Checks**
   ```python
   # custom_health_check.py
   import requests
   import sys
   
   def check_health():
       try:
           response = requests.get("http://localhost:8000/health", timeout=5)
           return response.status_code == 200
       except:
           return False
   
   if not check_health():
       print("Health check failed")
       sys.exit(1)
   else:
       print("Health check passed")
   ```

### Performance Monitoring

1. **Resource Usage**
   ```bash
   # Monitor container resources
   docker stats apgi-framework
   
   # System resources
   htop
   iotop
   ```

2. **Application Metrics**
   ```bash
   # Enable metrics collection
   export APGI_METRICS_ENABLED=true
   
   # View metrics
   curl http://localhost:9090/metrics
   ```

### Log Management

1. **Log Rotation**
   ```yaml
   # docker-compose.yml
   services:
     apgi-framework:
       logging:
         driver: "json-file"
         options:
           max-size: "10m"
           max-file: "3"
   ```

2. **Centralized Logging**
   ```yaml
   # docker-compose.logging.yml
   services:
     apgi-framework:
       logging:
         driver: "fluentd"
         options:
           fluentd-address: localhost:24224
           tag: apgi.framework
   ```

---

## 🔧 Troubleshooting Deployment

### Common Issues

#### Container Won't Start

**Symptoms:**
- `docker-compose up` fails
- Container exits immediately

**Solutions:**
```bash
# Check logs
docker-compose logs apgi-framework

# Check configuration
docker-compose config

# Rebuild image
docker-compose build --no-cache
```

#### Port Conflicts

**Symptoms:**
- "Port already allocated" error
- Cannot access web interface

**Solutions:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Use different port
docker-compose up -d --scale apgi-framework=0
# Edit ports in docker-compose.yml
docker-compose up -d
```

#### Memory Issues

**Symptoms:**
- Container restarts
- Out of memory errors

**Solutions:**
```bash
# Check memory usage
docker stats

# Increase memory limit
docker-compose up -d --scale apgi-framework=0
# Add memory limits to docker-compose.yml
docker-compose up -d

# Swap configuration
sudo swapon --show
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### Network Issues

**Symptoms:**
- Cannot connect to database
- Service discovery failures

**Solutions:**
```bash
# Check network
docker network ls
docker network inspect apgi-network

# Recreate network
docker network rm apgi-network
docker-compose up -d

# DNS issues
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```

### Debug Mode

1. **Enable Debug Logging**
   ```bash
   export APGI_LOG_LEVEL=DEBUG
   docker-compose up -d
   ```

2. **Interactive Debugging**
   ```bash
   # Enter container
   docker exec -it apgi-framework bash
   
   # Run commands inside container
   python -c "import apgi_framework; print('OK')"
   ```

3. **Performance Profiling**
   ```bash
   # Enable profiling
   export APGI_PROFILE=true
   
   # Generate profile
   python -m cProfile -o profile.stats your_script.py
   ```

### Recovery Procedures

1. **Complete Reset**
   ```bash
   # Stop all services
   docker-compose down
   
   # Remove volumes (data loss!)
   docker-compose down -v
   
   # Remove images
   docker system prune -a
   
   # Redeploy
   docker-compose up -d --build
   ```

2. **Data Recovery**
   ```bash
   # Backup current data
   docker cp apgi-framework:/app/data ./backup_data
   
   # Restore from backup
   docker cp ./backup_data apgi-framework:/app/
   docker-compose restart apgi-framework
   ```

---

## 📚 Additional Resources

### Documentation
- [Quick Start Guide](quick_start_guide.md)
- [Step-by-Step Tutorials](step_by_step_tutorials.md)
- [Troubleshooting Guide](troubleshooting.md)
- [API Documentation](../api/index.md)

### Tools and Scripts
- `quick_deploy.py` - One-click deployment
- `deploy.sh` - Advanced deployment script
- `backup.sh` - Automated backup script
- CLI tools - Command-line management

### Support
- [GitHub Issues](https://github.com/your-org/apgi-experiments/issues)
- [Community Forum](https://forum.apgi-framework.org)
- [Documentation](https://docs.apgi-framework.org)

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Docker installed and running
- [ ] Sufficient disk space (>10GB)
- [ ] Sufficient memory (>4GB)
- [ ] Network ports available
- [ ] Configuration files prepared
- [ ] Backup strategy defined

### Post-Deployment
- [ ] Container running successfully
- [ ] Health checks passing
- [ ] Web interface accessible
- [ ] Monitoring dashboard working
- [ ] Logs being collected
- [ ] Backups configured
- [ ] Performance baseline established

### Ongoing Maintenance
- [ ] Regular health checks
- [ ] Log rotation configured
- [ ] Backup schedule active
- [ ] Security updates applied
- [ ] Performance monitoring active
- [ ] Documentation updated

---

**Happy Deploying! 🚀**

---

**Version**: 1.0  
**Last Updated**: 2025-01-11  
**See Also**: [Quick Start Guide](quick_start_guide.md), [Troubleshooting](troubleshooting.md)
