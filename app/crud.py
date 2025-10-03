from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import secrets

from app.models import User, Transaction
from app.schemas import UserCreate, TransactionCreate


def generate_api_key() -> str:
    """Generate a secure random API key"""
    return secrets.token_urlsafe(32)


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Create a new user with auto-generated API key"""
    api_key = generate_api_key()
    db_user = User(
        username=user.username,
        email=user.email,
        api_key=api_key
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_api_key(db: AsyncSession, api_key: str) -> Optional[User]:
    """Get user by API key"""
    result = await db.execute(select(User).where(User.api_key == api_key))
    return result.scalar_one_or_none()


async def get_all_users(db: AsyncSession) -> List[User]:
    """Get all users"""
    result = await db.execute(select(User))
    return result.scalars().all()


async def create_transaction(
    db: AsyncSession,
    transaction: TransactionCreate,
    user_id: int
) -> Transaction:
    """Create a new transaction for a user"""
    db_transaction = Transaction(
        user_id=user_id,
        amount=transaction.amount,
        description=transaction.description,
        transaction_type=transaction.transaction_type
    )
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    return db_transaction


async def get_transaction_by_id(
    db: AsyncSession,
    transaction_id: int
) -> Optional[Transaction]:
    """Get transaction by ID"""
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    return result.scalar_one_or_none()


async def get_user_transactions(
    db: AsyncSession,
    user_id: int
) -> List[Transaction]:
    """Get all transactions for a user"""
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
    )
    return result.scalars().all()
