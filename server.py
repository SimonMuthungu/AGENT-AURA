# server.py
from fastapi import FastAPI
from langserve import add_routes
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# 1. Import your entire agent script logic
# NOTE: Vercel runs all code on import, so your agent is created here.
# If you don't like the final 'result = aura.invoke' line running on import, 
# you should remove it from agent.py before deployment.
from agent import aura  

# 2. Initialize FastAPI
app = FastAPI(
    title="AURA Project Health Agent",
    version="1.0",
    description="Analyzes project health using Supabase data."
)

# 3. Add CORS middleware (Crucial for playground access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Expose the Agent using LangServe
# The agent will be accessible at: YOUR_VERCEL_URL/aura-agent/
add_routes(
    app,
    aura,
    path="/aura-agent",
)

# Optional: Add a simple health check route
@app.get("/")
def home():
    return {"message": "AURA Agent Service is running. Access the agent at /aura-agent/playground/"}