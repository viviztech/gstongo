Perfect 👍 here’s a **useful, clean, production-style `frontend/README.md`** you can use.
It explains **what’s running, ports, DNS, and how traffic flows** — very helpful for devs & DevOps.

You can **copy-paste this exactly** 👇

---

```md
# Gstongo Frontend

This folder contains the frontend application for **Gstongo**, built with Vite and deployed using Docker + Nginx.

---

## 🚀 Deployment Overview

The frontend is deployed as a **Docker container** and served through **server-level Nginx** using the domain name.

### 🔹 Container Details
- **Container Name:** `gstongo-frontend`
- **Docker Image:** `sribalajidevops/gstongo-frontend:latest`
- **Internal Container Port:** `80` (Nginx inside container)
- **Host Port:** `3000`

```

Host:3000 → Container:80

```

---

## 🌐 Domain & Access

- **DNS Name:** https://gstongo.com  
- **Handled by:** Server Nginx (port 80 / 443)
- **SSL:** Managed via Certbot on server Nginx

Server Nginx proxies traffic to the frontend container running on port `3000`.

---

## 🔁 Traffic Flow

```

User Browser
↓
[https://gstongo.com](https://gstongo.com)
↓
Server Nginx (80 / 443)
↓
Frontend Container (localhost:3000 → container:80)

````

---

## 🔗 Backend API Connection

- **Backend Container Port:** `8000`
- **API Access Pattern:** `/api`
- **Example:** https://gstongo.com/api

The frontend uses an environment variable at build time:

```env
VITE_BACKEND_URL=https://gstongo.com/api
````

Backend routing is handled by **server Nginx**, not the frontend container.

---

## 🛠 CI/CD Notes

* CI/CD is triggered on changes inside `frontend/**`
* GitHub Actions:

  * Builds Docker image
  * Pushes to Docker Hub
  * Deploys container on EC2
* Frontend container **must not bind to port 80 on host** (reserved for server Nginx)

---

## ✅ Key Notes

* Do NOT expose frontend container directly on port 80
* Server Nginx owns ports `80` and `443`
* Frontend container runs safely on `3000`
* This setup avoids port conflicts and supports SSL

---

## 👨‍💻 Maintainers

* Frontend: React / Vite
* Deployment: Docker + Nginx + GitHub Actions

````

---

## ✅ Next steps
After adding this file:

```bash
git add frontend/README.md
git commit -m "Add frontend deployment documentation"
git push origin main
````


