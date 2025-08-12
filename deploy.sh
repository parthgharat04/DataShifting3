#!/bin/bash

# Data Shifting Application - Production Deployment Script
# Run this script on your production server

echo "🚀 Starting Data Shifting Application Deployment..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run with sudo privileges"
    echo "Usage: sudo bash deploy.sh"
    exit 1
fi

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /var/www/data_shifting
mkdir -p /var/www/data_shifting/{uploads,outputs,logs}

# Set ownership
echo "🔐 Setting file permissions..."
chown -R www-data:www-data /var/www/data_shifting
chmod -R 755 /var/www/data_shifting

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
cd /var/www/data_shifting
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
echo "⚙️ Creating systemd service..."
cat > /etc/systemd/system/data-shifting.service << EOF
[Unit]
Description=Data Shifting Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/data_shifting
Environment="PATH=/var/www/data_shifting/venv/bin"
ExecStart=/var/www/data_shifting/venv/bin/gunicorn --config gunicorn.conf.py wsgi:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "🚀 Starting service..."
systemctl daemon-reload
systemctl enable data-shifting
systemctl start data-shifting

# Check service status
echo "📊 Checking service status..."
systemctl status data-shifting --no-pager

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Copy your application files to /var/www/data_shifting/"
echo "2. Create .env file with your configuration (use env_template.txt as reference)"
echo "3. Restart the service: sudo systemctl restart data-shifting"
echo "4. Check logs: sudo journalctl -u data-shifting -f"
echo ""
echo "🌐 Your application should now be running on port 8000"
echo "🔗 Access it at: http://your-server-ip:8000"
echo ""
echo "📚 For detailed instructions, see PRODUCTION_DEPLOYMENT_GUIDE.md"
