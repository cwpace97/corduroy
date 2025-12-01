# Corduroy

A full-stack web application that scrapes and displays real-time ski resort data for Colorado mountains. View live lift and run status, difficulty levels, and grooming information through a modern React dashboard powered by a GraphQL API. For personal use. 

## What It Does

- **Scrapes** ski resort websites for current lift and run conditions
- **Stores** historical data in a SQLite database
- **Serves** data via a GraphQL API (FastAPI + Strawberry)
- **Displays** interactive resort cards with expandable details

## File Structure

```
corduroy/
├── backend/
│   ├── server.py           # FastAPI server with GraphQL
│   ├── schema.py           # GraphQL schema definitions
│   └── resolvers.py        # Data resolvers
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React app
│   │   ├── components/     # ResortCard, LoadingSpinner
│   │   └── pages/          # HomePage, DetailsPage
│   ├── package.json
│   └── vite.config.js
├── scrapers/
│   ├── base_scraper.py     # Selenium base class
│   ├── ...
├── init_db.py              # Database setup
├── requirements.txt
├── requirements.lock
└── ski.db                  # SQLite database
```

## Setup & Run

### Prerequisites
- Python 3.8+
- Node.js 18+

### Installation

```bash
# Install Python dependencies
pip install -r requirements.lock

# Install frontend dependencies
cd frontend && npm install && cd ..

# Initialize database
python init_db.py
```

### Running the Application

**Terminal 1 - Backend:**
```bash
./start_backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start_frontend.sh
```

**Access:**
- Web Dashboard: http://localhost:5173
- GraphQL API: http://localhost:8000/graphql

### Update Resort Data

```bash
./refresh_resorts.sh

# Or for a full reset
./reset_and_scrape.sh
```

## Tech Stack

**Backend:** FastAPI, Strawberry GraphQL, SQLite, Selenium  
**Frontend:** React, Vite, TailwindCSS, Apollo Client

## Production Deployment

### Nginx Reverse Proxy Setup

This application uses nginx as a reverse proxy to route traffic between the frontend and backend services, with SSL/HTTPS support for production deployments.

#### Architecture

```
Internet → Nginx (443/80) 
  ├─ /api/* → Backend (8000)
  ├─ /graphql → Backend (8000)
  └─ /* → Frontend (3000)
```

#### Prerequisites

- Domain name pointing to your server
- nginx installed on your server
- Ports 80 and 443 open in your firewall

#### Installation Steps

1. **Install nginx** (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install nginx -y
   
   # CentOS/RHEL
   sudo yum install nginx -y
   ```

2. **Copy nginx configuration**:
   ```bash
   # Copy the nginx.conf to nginx sites-available
   sudo cp nginx.conf /etc/nginx/sites-available/corduroy
   
   # The configuration is already set up for tracks.ski
   # Create symlink to enable the site
   sudo ln -s /etc/nginx/sites-available/corduroy /etc/nginx/sites-enabled/
   ```

3. **Set up SSL certificates with Let's Encrypt**:
   ```bash
   # Install certbot
   sudo apt install certbot python3-certbot-nginx -y
   
   # Obtain SSL certificate for tracks.ski (replace email with your email)
   sudo certbot --nginx -d tracks.ski
   
   # Certbot will automatically update nginx.conf with certificate paths
   ```

4. **Update SSL certificate paths in nginx.conf**:
   After running certbot, your certificate paths will be automatically configured. The nginx.conf already has the correct paths for tracks.ski:
   ```nginx
   ssl_certificate /etc/letsencrypt/live/tracks.ski/fullchain.pem;
   ssl_certificate_key /etc/letsencrypt/live/tracks.ski/privkey.pem;
   ```

5. **Test nginx configuration**:
   ```bash
   sudo nginx -t
   ```

6. **Start/restart nginx**:
   ```bash
   sudo systemctl start nginx
   sudo systemctl enable nginx  # Enable on boot
   sudo systemctl reload nginx   # After configuration changes
   ```

#### Docker Deployment

1. **Build and start services**:
   ```bash
   # Build and start frontend and backend
   docker-compose --profile app up -d --build
   
   # Or start individually
   docker-compose up -d backend
   docker-compose up -d frontend
   ```

2. **Set environment variables**:
   Create a `.env` file in the project root:
   ```bash
   # Backend CORS origins (comma-separated)
   ALLOWED_ORIGINS=https://tracks.ski
   
   # Frontend GraphQL URL (use relative path for same-origin)
   NEXT_PUBLIC_GRAPHQL_URL=/graphql
   ```

3. **Verify services are running**:
   ```bash
   # Check container status
   docker-compose ps
   
   # Check logs
   docker-compose logs backend
   docker-compose logs frontend
   ```

#### Environment Variables

**Backend (`backend/server.py`)**:
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins
  - Example: `https://tracks.ski`
  - Default: `http://localhost:3000,http://localhost:5173`

**Frontend (`frontend/`)**:
- `NEXT_PUBLIC_GRAPHQL_URL`: GraphQL API endpoint URL
  - Production: `/graphql` (relative path through nginx)
  - Development: `http://localhost:8000/graphql`

#### Production Checklist

- [ ] Domain DNS records configured
- [ ] nginx installed and configured
- [ ] SSL certificates obtained and configured
- [ ] Firewall ports 80 and 443 open
- [ ] Backend and frontend services running (Docker or systemd)
- [ ] Environment variables set correctly
- [ ] CORS origins configured for production domain
- [ ] Database initialized and accessible
- [ ] Health checks passing (`/health` endpoint)
- [ ] SSL certificate auto-renewal configured (certbot)

#### SSL Certificate Auto-Renewal

Let's Encrypt certificates expire every 90 days. Set up auto-renewal:

```bash
# Test renewal process
sudo certbot renew --dry-run

# Certbot creates a systemd timer automatically, verify it's active:
sudo systemctl status certbot.timer
```

#### Troubleshooting

**nginx won't start**:
```bash
# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Test configuration syntax
sudo nginx -t
```

**502 Bad Gateway**:
- Verify backend/frontend services are running: `docker-compose ps`
- Check service logs: `docker-compose logs backend frontend`
- Verify upstream ports match (3000 for frontend, 8000 for backend)

**SSL certificate issues**:
- Ensure domain DNS is properly configured
- Verify port 80 is accessible for Let's Encrypt challenges
- Check certificate expiration: `sudo certbot certificates`

**CORS errors**:
- Verify `ALLOWED_ORIGINS` includes your production domain
- Check backend logs for CORS-related errors
- Ensure requests are going through nginx (not directly to backend)

#### Deployment Platforms

**AWS ECS**:
- Use Application Load Balancer (ALB) with SSL termination
- Configure target groups for frontend (port 3000) and backend (port 8000)
- Use ALB rules to route `/api/*` and `/graphql` to backend, rest to frontend
- Or use nginx container in ECS task with ALB pointing to it

**Other Platforms**:
- The nginx configuration works with any platform that allows nginx installation
- Ensure containers/services are accessible on localhost:3000 and localhost:8000
- Update upstream definitions if using different ports or hostnames
