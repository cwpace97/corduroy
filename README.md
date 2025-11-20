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
./full_scrape.sh

# Or for a full reset
./reset_and_scrape.sh
```

## Tech Stack

**Backend:** FastAPI, Strawberry GraphQL, SQLite, Selenium  
**Frontend:** React, Vite, TailwindCSS, Apollo Client
