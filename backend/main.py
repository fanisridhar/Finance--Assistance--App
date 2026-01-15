from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.database import engine, Base
from app.routers import auth, transactions, plaid, budget, chat
from app.services.redis_client import get_redis_client

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    # Initialize Redis connection
    await get_redis_client()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Personal Finance Planner API",
    description="API for personal finance management with Plaid integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(plaid.router, prefix="/api/plaid", tags=["Plaid"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(budget.router, prefix="/api/budget", tags=["Budget"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "Personal Finance Planner API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

