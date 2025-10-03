# FastAPI Multi-User Transaction API

A REST API built with FastAPI demonstrating database integration, caching, and containerization.

## Features

- **User Management**: Create users with auto-generated API keys
- **Transaction Management**: Create and retrieve financial transactions
- **Authentication**: API key-based authentication via `X-API-Key` header
- **PostgreSQL**: Persistent data storage with SQLAlchemy ORM
- **Redis Caching**: 30-second cache for transaction queries
- **Auto-Seeding**: Automatically generates 5 users with 10 transactions each on startup
- **Docker Compose**: One-command deployment

## Quick Start

Run the entire application stack:

```bash
docker-compose up --build
```

The API will be available at: http://localhost:8000

Interactive API documentation: http://localhost:8000/docs

## API Endpoints

### Users
- `POST /users` - Create a new user (returns API key)
- `GET /users/me` - Get authenticated user info
- `GET /users` - List all users

### Transactions
- `POST /transactions` - Create a transaction (requires auth)
- `GET /transactions` - Get user's transactions (cached for 30s)
- `GET /transactions/{id}` - Get specific transaction (requires auth)

## Authentication

All protected endpoints require the `X-API-Key` header:

```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/users/me
```

## Example Usage

### 1. Create a User

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com"
  }'
```

Response:
```json
{
  "id": 6,
  "username": "john_doe",
  "email": "john@example.com",
  "api_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "created_at": "2025-10-03T12:00:00"
}
```

**Save the API key for authentication!**

### 2. Create a Transaction

```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "amount": 150.50,
    "description": "Grocery shopping",
    "transaction_type": "payment"
  }'
```

### 3. Get Transactions (Cached)

```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/transactions
```

First call fetches from database, subsequent calls within 30s return cached data.

## Dummy Data

On startup, the application creates 5 users:
- `user1@example.com` through `user5@example.com`
- Each user has 10 random transactions
- API keys are printed in the startup logs

Check the logs to get API keys:
```bash
docker-compose logs app | grep "API Key"
```

## Transaction Types

- `deposit`
- `withdrawal`
- `transfer`
- `payment`

## Architecture

```
├── app/
│   ├── main.py          # FastAPI app & endpoints
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # Database operations
│   ├── auth.py          # API key authentication
│   ├── cache.py         # Redis integration
│   ├── database.py      # DB connection
│   ├── config.py        # Settings
│   └── seed.py          # Data seeding
├── docker-compose.yml   # Orchestration
├── Dockerfile          # App container
└── requirements.txt    # Dependencies
```

## Services

- **FastAPI**: Port 8000
- **PostgreSQL**: Port 5432
- **Redis**: Port 6379

## Stopping the Application

```bash
docker-compose down
```

To remove volumes (delete all data):

```bash
docker-compose down -v
```

## Development

To rebuild after code changes:

```bash
docker-compose up --build
```
