from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import API routes
from src.api import tasks, health, auth
from src.core.config import settings

# Create FastAPI app instance
app = FastAPI(
    title="Todo API",
    description="Multi-user todo application API",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(health.router, prefix="/api", tags=["health"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    # uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

    # http://localhost:8000/api/health

    # http://localhost:8000/docs

# main.py is main agent who assign jobs to

# sub-agents:
# auth.py (Guard Agent) - Verifies Token
# tasks.py (Worker Agent) - Processes Request
# database.py (Connector Agent) - Queries DB

# what we send request/query as per form placeholder, what we want to do by --> frontend 
# we see at same frontend --> Response back to User

# 📊 Agent Workflow - Real Example
# Let's say user creates a task "Buy Groceries":
# ┌─────────────────────────────────────────────────────┐
# │ FRONTEND: User fills form                           │
# │ Title: "Buy Groceries"                              │
# │ Description: "Milk, Bread, Eggs"                    │
# │ Clicks: "Create Task" button                        │
# └────────────────┬────────────────────────────────────┘
#                  │
#                  ▼
# ┌─────────────────────────────────────────────────────┐
# │ MAIN AGENT (main.py)                                │
# │ "Incoming POST request to /api/tasks"               │
# │ "Route this to Task Agent"                          │
# └────────────────┬────────────────────────────────────┘
#                  │
#                  ▼
# ┌─────────────────────────────────────────────────────┐
# │ GATEKEEPER AGENT (middleware/auth.py)               │
# │ "Check JWT token first!"                            │
# │ "Token valid? Yes ✓"                                │
# │ "User ID: 83a37cf8-db4f-4c84..."                    │
# └────────────────┬────────────────────────────────────┘
#                  │
#                  ▼
# ┌─────────────────────────────────────────────────────┐
# │ TASK AGENT (tasks.py)                               │
# │ "Create task for this user"                         │
# │ "Prepare data: title, description, user_id"         │
# │ "Send to Database Agent"                            │
# └────────────────┬────────────────────────────────────┘
#                  │
#                  ▼
# ┌─────────────────────────────────────────────────────┐
# │ DATABASE AGENT (database.py)                        │
# │ "INSERT INTO task..."                               │
# │ "Connected to Neon PostgreSQL"                      │
# │ "Data saved! Task ID: 4"                            │
# └────────────────┬────────────────────────────────────┘
#                  │
#                  ▼
# ┌─────────────────────────────────────────────────────┐
# │ Response flows back through agents                  │
# │ Database → Task Agent → Main Agent → Frontend       │
# └────────────────┬────────────────────────────────────┘
#                  │
#                  ▼
# ┌─────────────────────────────────────────────────────┐
# │ FRONTEND: Task appears in dashboard!                │
# │ "Buy Groceries" - ID:000004 - Created!              │
# └─────────────────────────────────────────────────────┘

# Frontend (Next.js)
#                            │
#                            ▼
#                     ┌──────────────┐
#                     │  Main Agent  │ ← Orchestrator
#                     │   (main.py)  │
#                     └──────┬───────┘
#                            │
#            ┌───────────────┼───────────────┐
#            │               │               │
#            ▼               ▼               ▼
#     ┌──────────┐    ┌──────────┐   ┌──────────┐
#     │  Auth    │    │  Task    │   │  Health  │
#     │  Agent   │    │  Agent   │   │  Agent   │
#     └────┬─────┘    └────┬─────┘   └──────────┘
#          │               │
#          └───────┬───────┘
#                  │
#          ┌───────▼────────┐
#          │  Gatekeeper    │ ← JWT Verification
#          │  Agent         │
#          └───────┬────────┘
#                  │
#          ┌───────▼────────┐
#          │  Database      │ ← Neon PostgreSQL
#          │  Agent         │
#          └────────────────┘

