# GSTONGO AWS Free Tier Deployment Guide

AWS Free Tier includes:
- 750 hours/month of t2.micro or t3.micro (12 months)
- 20 GB of RDS storage (12 months)
- 5 GB of S3 storage
- 750 hours/month of Elastic Beanstalk

---

## Step 1: Launch EC2 Instance (Free Tier)

### 1.1 Create Key Pair
```bash
# AWS Console > EC2 > Key Pairs > Create key pair
# Name: gstongo-key
# Type: RSA
# Format: .pem
```

### 1.2 Launch Instance
```bash
# AWS Console > EC2 > Launch Instances
# AMI: Ubuntu Server 22.04 LTS (Free Tier eligible)
# Instance Type: t2.micro or t3.micro (Free Tier eligible)
# VPC: Default
# Security Group (create new):
#   - SSH (22): My IP
#   - HTTP (80): 0.0.0.0/0
#   - HTTPS (443): 0.0.0.0/0
```

### 1.3 Connect
```bash
chmod 400 gstongo-key.pem
ssh -i gstongo-key.pem ubuntu@<EC2_PUBLIC_IP>
```

---

## Step 2: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx git

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Redis (for caching)
sudo apt install -y redis-server
```

---

## Step 3: Configure PostgreSQL

```bash
sudo -u postgres psql

# In psql:
CREATE DATABASE gstongo_db;
CREATE USER gstongo_user WITH PASSWORD 'YourSecurePassword123!';
GRANT ALL PRIVILEGES ON DATABASE gstongo_db TO gstongo_user;
ALTER USER gstongo_user WITH SUPERUSER;
\q
```

---

## Step 4: Setup Application

```bash
# Create project directory
cd /var/www
sudo mkdir gstongo
sudo chown -R $USER:$USER gstongo
cd gstongo

# Clone and setup
git clone <YOUR_REPO_URL> .
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp gstongo/.env.example .env
nano .env
```

**`.env` configuration:**
```env
DEBUG=0
SECRET_KEY=generate-random-secret-key
ALLOWED_HOSTS=<EC2_IP>,localhost

DATABASE_URL=postgres://gstongo_user:YourSecurePassword123!@localhost:5432/gstongo_db
REDIS_URL=redis://localhost:6379/0

RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret

DEFAULT_FROM_EMAIL=your-email@gmail.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

```bash
# Run migrations
python manage.py migrate
python manage.py setup_initial_data
python manage.py collectstatic --noinput

# Build frontend
cd ../frontend
npm install
npm run build
```

---

## Step 5: Configure Gunicorn

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```ini
[Unit]
Description=gunicorn daemon for GSTONGO
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/gstongo/backend
Environment="PATH=/var/www/gstongo/backend/venv/bin"
ExecStart=/var/www/gstongo/backend/venv/bin/gunicorn \
    --workers 2 \
    --bind unix:/var/www/gstongo/gunicorn.sock \
    gstongo.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

---

## Step 6: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/gstongo
```

```nginx
server {
    listen 80;
    server_name <EC2_IP> localhost;

    # Frontend
    location / {
        root /var/www/gstongo/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Django API
    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/var/www/gstongo/gunicorn.sock;
    }

    # Static files
    location /static/ {
        alias /var/www/gstongo/backend/staticfiles/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/gstongo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Step 7: Add SSL (Let's Encrypt - Free)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d <EC2_IP>.nip.io  # Or your domain
```

---

## Step 8: Keep Server Running After Reboot

Use **tmux** or **screen** to keep processes running:

```bash
# Install tmux
sudo apt install -y tmux

# Start tmux session
tmux new -s gstongo

# Run server
cd /var/www/gstongo/backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Detach: Ctrl+B, D
# Reattach: tmux attach -s gstongo
```

Or use **pm2** for Node.js-like process management:

```bash
sudo npm install -g pm2
cd /var/www/gstongo/backend
pm2 start manage.py --interpreter python3 -- runserver 0.0.0.0:8000
pm2 startup
pm2 save
```

---

## Step 9: Free Tier Resources

| Resource | Free Limit | GSTONGO Usage |
|----------|-----------|---------------|
| EC2 t2.micro | 750 hrs/month | ✅ Within limit |
| RDS PostgreSQL | 750 hrs/month | ✅ Use local PostgreSQL on EC2 instead |
| S3 | 5 GB | ✅ Minimal usage |
| Data Transfer | 15 GB/month | ✅ Within limit |

**Note:** For production, use local PostgreSQL on EC2 to save RDS hours.

---

## Quick Commands

```bash
# SSH into server
ssh -i gstongo-key.pem ubuntu@<EC2_IP>

# Check Gunicorn status
sudo systemctl status gunicorn

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# View logs
sudo journalctl -u gunicorn -f

# Backup database
pg_dump -U gstongo_user gstongo_db > backup.sql

# Restore database
psql -U gstongo_user gstongo_db < backup.sql
```

---

## Estimated Free Tier Cost (Monthly)
| Service | Cost |
|---------|------|
| EC2 t2.micro | $0 (12 months) |
| EBS Storage | ~$1 |
| Data Transfer | ~$1 |
| **Total** | **~$2/month** |

After 12 months: ~$10-15/month for EC2 + storage.
