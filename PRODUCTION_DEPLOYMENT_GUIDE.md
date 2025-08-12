# Production Deployment Guide
## Data Shifting Application - Flask to Production Server

**Version:** 2.0 (Enhanced Multi-line Support)  
**Target Environment:** Internal Production Server  
**Last Updated:** December 2024

---

## 📋 Overview

This guide outlines the necessary changes to deploy the Data Shifting Flask application from development to production on an internal server. The application currently runs in development mode and needs production hardening for security, performance, and maintainability.

---

## 🚨 Critical Changes Required

### 1. **Remove Development Mode (CRITICAL)**

**File:** `app.py`  
**Current Code (REMOVE):**
```python
if __name__ == '__main__':
    app.run(debug=True)  # ← REMOVE THIS LINE
```

**Replace With:**
```python
if __name__ == '__main__':
    # Development only - comment out for production
    # app.run(debug=False, host='0.0.0.0', port=5000)
    pass
```

**Why:** `debug=True` exposes sensitive information and should NEVER be in production.

---

### 2. **Environment Configuration**

**Create new file:** `.env` (in root directory)
```bash
# Production Environment Variables
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_secure_random_key_here_32_characters_minimum
UPLOAD_FOLDER=/var/www/data_shifting/uploads
OUTPUT_FOLDER=/var/www/data_shifting/outputs
LOG_LEVEL=INFO
MAX_FILE_SIZE=104857600
```

**Create new file:** `.env.example` (template for other developers)
```bash
# Template - Copy to .env and fill in actual values
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=change_this_to_secure_random_key
UPLOAD_FOLDER=/path/to/uploads
OUTPUT_FOLDER=/path/to/outputs
LOG_LEVEL=INFO
MAX_FILE_SIZE=104857600
```

---

### 3. **Update app.py Configuration**

**File:** `app.py`  
**Add these imports at the top:**
```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
```

**Replace the configuration section:**
```python
# OLD CODE (REPLACE):
app.secret_key = 'data_shifting_secret_key'
BASE_UPLOAD_FOLDER = 'uploads'
BASE_OUTPUT_FOLDER = 'outputs'

# NEW CODE:
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_key_for_development_only')
BASE_UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
BASE_OUTPUT_FOLDER = os.environ.get('OUTPUT_FOLDER', 'outputs')

# Add file size limit
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_FILE_SIZE', 100 * 1024 * 1024))  # Default 100MB
```

**Update directory creation:**
```python
# OLD CODE:
if not os.path.exists(BASE_UPLOAD_FOLDER):
    os.makedirs(BASE_UPLOAD_FOLDER)
if not os.path.exists(BASE_OUTPUT_FOLDER):
    os.makedirs(BASE_OUTPUT_FOLDER)

# NEW CODE:
# Ensure directories exist with proper permissions
os.makedirs(BASE_UPLOAD_FOLDER, mode=0o755, exist_ok=True)
os.makedirs(BASE_OUTPUT_FOLDER, mode=0o755, exist_ok=True)
```

---

### 4. **Add Production Logging**

**File:** `app.py`  
**Add after app configuration:**
```python
# Production Logging Configuration
if not app.debug:
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs', mode=0o755)
    
    # Configure rotating file handler
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        'logs/data_shifting.log', 
        maxBytes=10*1024*1024,  # 10MB per file
        backupCount=10
    )
    
    # Set log format
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Add handler to app logger
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Data Shifting Application Startup')
```

---

### 5. **Add Error Handlers**

**File:** `app.py`  
**Add before the main routes:**
```python
# Production Error Handlers
@app.errorhandler(500)
def internal_error(error):
    app.logger.error('Server Error: %s', error)
    return render_template('error.html', error="Internal server error"), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(413)
def too_large(error):
    return render_template('error.html', error="File too large"), 413
```

---

### 6. **Create WSGI Entry Point**

**Create new file:** `wsgi.py` (in root directory)
```python
"""
WSGI entry point for production deployment
"""
from app import app

if __name__ == "__main__":
    app.run()
```

---

### 7. **Update Requirements**

**File:** `requirements.txt`  
**Add these production dependencies:**
```txt
Flask==2.3.3
Werkzeug==2.3.7
python-dotenv==1.0.0
gunicorn==21.2.0
```

---

### 8. **Create Production Configuration Files**

**Create new file:** `gunicorn.conf.py`
```python
"""
Gunicorn configuration for production deployment
"""
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "data_shifting_app"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

---

### 9. **Create Error Template**

**File:** `templates/error.html`
```html
<!DOCTYPE html>
<html>
<head>
    <title>Error - Data Shifting Application</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .error-container { text-align: center; margin-top: 100px; }
        .error-code { font-size: 72px; color: #e74c3c; margin-bottom: 20px; }
        .error-message { font-size: 18px; color: #2c3e50; }
        .back-link { margin-top: 30px; }
        .back-link a { color: #3498db; text-decoration: none; }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-code">⚠️</div>
        <div class="error-message">{{ error }}</div>
        <div class="back-link">
            <a href="{{ url_for('home') }}">← Back to Home</a>
        </div>
    </div>
</body>
</html>
```

---

## 🚀 Deployment Steps

### **Step 1: Prepare the Code**
1. Apply all the changes above to your codebase
2. Test locally with `debug=False`
3. Commit changes to version control

### **Step 2: Server Setup**
```bash
# Create application directory
sudo mkdir -p /var/www/data_shifting
sudo chown www-data:www-data /var/www/data_shifting

# Create required subdirectories
sudo mkdir -p /var/www/data_shifting/{uploads,outputs,logs}
sudo chown -R www-data:www-data /var/www/data_shifting
```

### **Step 3: Install Dependencies**
```bash
# Create virtual environment
python3 -m venv /var/www/data_shifting/venv
source /var/www/data_shifting/venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### **Step 4: Configure Environment**
```bash
# Copy and edit environment file
cp .env.example .env
nano .env  # Edit with actual values
```

### **Step 5: Test Gunicorn**
```bash
# Test the application
cd /var/www/data_shifting
source venv/bin/activate
gunicorn --config gunicorn.conf.py wsgi:app
```

### **Step 6: Create Systemd Service**
**File:** `/etc/systemd/system/data-shifting.service`
```ini
[Unit]
Description=Data Shifting Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/data_shifting
Environment="PATH=/var/www/data_shifting/venv/bin"
ExecStart=/var/www/data_shifting/venv/bin/gunicorn --config gunicorn.conf.py wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### **Step 7: Enable and Start Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable data-shifting
sudo systemctl start data-shifting
sudo systemctl status data-shifting
```

---

## 🔒 Security Considerations

### **File Permissions**
```bash
# Set proper permissions
sudo chmod 755 /var/www/data_shifting
sudo chmod 755 /var/www/data_shifting/uploads
sudo chmod 755 /var/www/data_shifting/outputs
sudo chmod 755 /var/www/data_shifting/logs
```

### **Firewall Configuration**
```bash
# Allow only necessary ports
sudo ufw allow 8000  # If using Gunicorn directly
sudo ufw allow 80     # If using Nginx
sudo ufw allow 443    # If using HTTPS
```

### **SSL/HTTPS (Recommended)**
- Use Let's Encrypt for free SSL certificates
- Configure Nginx as reverse proxy with SSL termination
- Redirect HTTP to HTTPS

---

## 📊 Monitoring & Maintenance

### **Log Files Location**
- **Application Logs:** `/var/www/data_shifting/logs/data_shifting.log`
- **Gunicorn Access:** `/var/www/data_shifting/logs/gunicorn_access.log`
- **Gunicorn Errors:** `/var/www/data_shifting/logs/gunicorn_error.log`

### **Service Management**
```bash
# Check status
sudo systemctl status data-shifting

# Restart service
sudo systemctl restart data-shifting

# View logs
sudo journalctl -u data-shifting -f

# Stop service
sudo systemctl stop data-shifting
```

### **Health Check Endpoint**
**Add to app.py:**
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
```

---

## 🧪 Testing Checklist

- [ ] Application starts without debug mode
- [ ] Environment variables are loaded correctly
- [ ] File uploads work with size limits
- [ ] Error pages display properly
- [ ] Logs are written to log files
- [ ] Service starts automatically on boot
- [ ] File permissions are correct
- [ ] Health check endpoint responds

---

## 🆘 Troubleshooting

### **Common Issues**

1. **Permission Denied Errors**
   ```bash
   sudo chown -R www-data:www-data /var/www/data_shifting
   ```

2. **Port Already in Use**
   ```bash
   sudo netstat -tlnp | grep :8000
   sudo kill -9 <PID>
   ```

3. **Service Won't Start**
   ```bash
   sudo systemctl status data-shifting
   sudo journalctl -u data-shifting -n 50
   ```

4. **Environment Variables Not Loading**
   ```bash
   # Check if .env file exists and has correct format
   cat .env
   # Ensure python-dotenv is installed
   pip install python-dotenv
   ```

---

## 📞 Support

For deployment issues:
1. Check the logs: `sudo journalctl -u data-shifting -f`
2. Verify file permissions and ownership
3. Ensure all environment variables are set
4. Test the application manually before starting the service

---

## 📝 Change Summary

| Component | Development | Production |
|-----------|-------------|------------|
| Debug Mode | `debug=True` | `debug=False` |
| Secret Key | Hardcoded | Environment Variable |
| File Paths | Relative | Absolute |
| Logging | Console | File-based |
| Server | Flask Dev Server | Gunicorn |
| Error Handling | Basic | Comprehensive |
| Security | Minimal | Hardened |

---

**Note:** This guide assumes a Linux server environment. Adjust paths and commands for Windows Server if needed.
