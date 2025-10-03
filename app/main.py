from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from typing import List

from app.database import get_db, init_db
from app.models import User
from app.schemas import (
    UserCreate,
    UserResponse,
    UserPublic,
    TransactionCreate,
    TransactionResponse
)
from app.auth import get_current_user
from app import crud
from app.cache import get_cache, set_cache, close_redis
from app.seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("Starting up...")
    await init_db()
    await seed_data()
    yield
    # Shutdown
    print("Shutting down...")
    await close_redis()


app = FastAPI(
    title="FastAPI Multi-User Transaction API",
    description="REST API with users, transactions, PostgreSQL, and Redis caching",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "FastAPI Multi-User Transaction API",
        "status": "running",
        "docs": "/docs"
    }


# User Endpoints
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user.
    Returns the user with auto-generated API key for authentication.
    """
    try:
        db_user = await crud.create_user(db, user)
        return db_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"User creation failed: {str(e)}")


@app.get("/users/me", response_model=UserPublic)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's information.
    Requires X-API-Key header.
    """
    return current_user


@app.get("/users", response_model=List[UserPublic])
async def list_users(db: AsyncSession = Depends(get_db)):
    """
    List all users (public information only).
    """
    users = await crud.get_all_users(db)
    return users


# Transaction Endpoints
@app.post("/transactions", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new transaction for the authenticated user.
    Requires X-API-Key header.
    """
    db_transaction = await crud.create_transaction(db, transaction, current_user.id)

    # Invalidate cache for this user's transactions
    cache_key = f"transactions:user:{current_user.id}"
    from app.cache import delete_cache
    await delete_cache(cache_key)

    return db_transaction


@app.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all transactions for the authenticated user.
    Results are cached in Redis for 30 seconds.
    Requires X-API-Key header.
    """
    cache_key = f"transactions:user:{current_user.id}"

    # Try to get from cache
    cached_data = await get_cache(cache_key)
    if cached_data:
        print(f"Cache hit for {cache_key}")
        return cached_data

    # Cache miss - fetch from database
    print(f"Cache miss for {cache_key}")
    transactions = await crud.get_user_transactions(db, current_user.id)

    # Convert to dict for caching
    transactions_data = [
        {
            "id": t.id,
            "user_id": t.user_id,
            "amount": t.amount,
            "description": t.description,
            "transaction_type": t.transaction_type.value,
            "created_at": t.created_at.isoformat()
        }
        for t in transactions
    ]

    # Cache the result
    await set_cache(cache_key, transactions_data)

    return transactions


@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific transaction by ID.
    User can only access their own transactions.
    Requires X-API-Key header.
    """
    transaction = await crud.get_transaction_by_id(db, transaction_id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to access this transaction"
        )

    return transaction
