# Free Tier Hosting Options for GSTONGO

## 1. Railway (Recommended for Django)

### Free Tier
- $5 credit/month
- 500 hours execution time
- 1GB RAM, 1GB storage per service
- Custom domains with SSL

### Deployment
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Environment Variables
```env
DEBUG=0
SECRET_KEY=your-secret
DATABASE_URL=railway-postgres-url
RAZORPAY_KEY_ID=xxx
```

---

## 2. Render

### Free Tier
- 750 hours/month (web service)
- 500MB RAM
- Custom domains with SSL
- Automatic deployments from GitHub

### Deployment
```bash
# Connect GitHub repo in Render dashboard
# Create web service:
#   Build Command: cd backend && pip install -r requirements.txt
#   Start Command: gunicorn gstongo.wsgi:application
# Environment variables: Add all from .env
```

---

## 3. PythonAnywhere

### Free Tier
- Always free tier available
- 512MB RAM
- 1 CPU thread
- Custom domain support

### Deployment
```bash
# Sign up at pythonanywhere.com
# Upload files via Files tab or Git
# Open Bash console
mkvirtualenv gstongo --python=/usr/bin/python3.10
pip install -r requirements.txt
python manage.py migrate
```

### WSGI Configuration
```python
# /var/www/<username>_pythonanywhere_com_wsgi.py
import sys
sys.path.insert(0, '/home/<username>/gstongo/backend')
sys.path.insert(0, '/home/<username>/gstongo/backend/gstongo')

from gstongo.wsgi import application
```

---

## 4. Fly.io

### Free Tier
- 3 shared VMs
- 3GB persistent storage
- Custom domains with TLS

### Deployment
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

### fly.toml
```toml
[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"
  DEBUG = "0"
```

---

## 5. Vercel (Frontend) + Railway (Backend)

### Frontend on Vercel (Free)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

### Backend on Railway
- Connect same GitHub repo
- Deploy backend folder
- Update frontend API URL to Railway URL

---

## 6. Cyclic (Full Stack)

### Free Tier
- Unlimited projects
- 1GB RAM
- Custom domains with SSL
- Automatic deployments

### Deployment
```bash
# Connect GitHub repo in Cyclic dashboard
# Root directory: backend
# Build command: pip install -r requirements.txt
# Start command: gunicorn gstongo.wsgi:application
```

---

## Comparison Table

| Provider | RAM | Hours/Month | Database | Django Support | Rating |
|----------|-----|-------------|----------|----------------|--------|
| **Railway** | 1GB | 500 | Paid add-on | ✅ Excellent | ⭐⭐⭐⭐⭐ |
| **Render** | 500MB | 750 | Free tier | ✅ Excellent | ⭐⭐⭐⭐ |
| **PythonAnywhere** | 512MB | Unlimited | Free tier | ✅ Excellent | ⭐⭐⭐⭐ |
| **Fly.io** | shared | Unlimited | Paid add-on | ✅ Good | ⭐⭐⭐⭐ |
| **Vercel** | N/A | N/A | N/A | Frontend only | ⭐⭐⭐⭐⭐ |
| **Cyclic** | 1GB | Unlimited | Paid add-on | ✅ Good | ⭐⭐⭐ |

---

## Recommended Setup

### Option 1: All-in-One (Easiest)
**PythonAnywhere** - Host everything in one place

### Option 2: Modern Stack
**Railway** - Backend + Database  
**Vercel** - Frontend (free for static sites)

### Option 3: Most Features
**Render** - Free web service with reasonable limits

---

## Quick Deployment: Railway (Recommended)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### Step 2: Deploy Backend
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Set environment variables
railway variables set DEBUG=0
railway variables set SECRET_KEY=xxx
railway variables set DATABASE_URL=$POSTGRES_URL

# Deploy
railway up
```

### Step 3: Add Database
```bash
railway add postgresql
```

### Step 4: Configure Domain
```bash
railway domain add www.yourdomain.com
```

---

## Database Options (Free)

| Service | Free Tier |
|---------|-----------|
| Railway Postgres | $5 credit/month |
| Neon | 10 branches, 600 hours |
| Supabase | 500MB database |
| PlanetScale | 1GB storage |
| MongoDB Atlas | 512MB storage |

---

## Estimated Monthly Cost (Free Tier)

| Service | Cost |
|---------|------|
| Railway (Backend + DB) | $0 (first month $5 credit) |
| Vercel (Frontend) | $0 |
| Domain (optional) | ~$12/year |
| **Total** | **~$1/month** |
