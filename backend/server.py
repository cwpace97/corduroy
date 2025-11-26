#!/usr/bin/env python3
"""FastAPI GraphQL server for ski resort data"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
import strawberry

from .schema import Query

# Create Strawberry schema
schema = strawberry.Schema(query=Query)

# Create FastAPI app
app = FastAPI(title="Ski Resort API", version="1.0.0")

# Configure CORS - allow origins from environment variable or default to localhost
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    # Split comma-separated origins from environment variable
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]
else:
    # Default to localhost for development
    allowed_origins = ["http://localhost:5173", "http://localhost:3000", "http://localhost:5174"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create GraphQL router
graphql_app = GraphQLRouter(schema)

# Mount GraphQL endpoint
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ski Resort API",
        "graphql": "/graphql"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

