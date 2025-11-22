# Ski Resort Dashboard - Frontend

React frontend for the Ski Resort Dashboard application.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm preview
```

## Features

- Modern React 18 with functional components and hooks
- TailwindCSS for styling
- Apollo Client for GraphQL queries
- Responsive design
- Expandable resort cards
- Real-time data updates

## Environment

The frontend expects the GraphQL backend to be running at `http://localhost:8000/graphql`. This can be configured in `src/main.jsx`.

## Components

- **App.jsx**: Main application component with GraphQL query
- **ResortCard.jsx**: Individual resort display with expandable details
- **LoadingSpinner.jsx**: Loading state component

## Development

The app uses Vite for fast development and hot module replacement (HMR).

