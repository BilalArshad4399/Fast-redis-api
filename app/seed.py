import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import random

from app.database import AsyncSessionLocal, init_db
from app.models import User, Transaction, TransactionType
from app.crud import generate_api_key


async def seed_data():
    """Seed database with dummy data"""
    async with AsyncSessionLocal() as db:
        # Check if data already exists
        result = await db.execute(select(User))
        existing_users = result.scalars().all()

        if existing_users:
            print("Database already seeded. Skipping...")
            return

        print("Seeding database with dummy data...")

        # Create 5 users
        users = []
        for i in range(1, 6):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                api_key=generate_api_key()
            )
            db.add(user)
            users.append(user)

        await db.commit()

        # Refresh to get IDs
        for user in users:
            await db.refresh(user)

        print(f"Created {len(users)} users:")
        for user in users:
            print(f"  - {user.username} (API Key: {user.api_key})")

        # Create 10 transactions per user
        transaction_types = [t for t in TransactionType]
        descriptions = [
            "Coffee shop payment",
            "Salary deposit",
            "ATM withdrawal",
            "Online shopping",
            "Restaurant bill",
            "Utility payment",
            "Transfer to friend",
            "Subscription payment",
            "Freelance income",
            "Gas station payment"
        ]

        total_transactions = 0
        for user in users:
            for i in range(10):
                transaction = Transaction(
                    user_id=user.id,
                    amount=round(random.uniform(10.0, 1000.0), 2),
                    description=random.choice(descriptions),
                    transaction_type=random.choice(transaction_types)
                )
                db.add(transaction)
                total_transactions += 1

        await db.commit()
        print(f"Created {total_transactions} transactions")
        print("Database seeding completed!")


async def run_seed():
    """Initialize database and seed data"""
    print("Initializing database...")
    await init_db()
    await seed_data()


if __name__ == "__main__":
    asyncio.run(run_seed())
