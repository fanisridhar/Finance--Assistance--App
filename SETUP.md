# Setup Instructions

## Prerequisites

1. Python 3.11+ - Download from https://www.python.org/downloads/
2. Node.js 18+ - Download from https://nodejs.org/
3. PostgreSQL 14+ - Download from https://www.postgresql.org/download/
4. Redis 6+ - Download from https://redis.io/download
5. Docker & Docker Compose (Optional) - Download from https://www.docker.com/

## Option 1: Local Setup (Without Docker)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the `backend/` directory:
```bash
cp .env.example .env
```

5. Edit `.env` and add your configuration:
   - Get Plaid credentials from https://dashboard.plaid.com/
   - Get OpenAI API key from https://platform.openai.com/
   - Generate encryption key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

6. Start PostgreSQL and Redis:
```bash
# PostgreSQL (macOS with Homebrew)
brew services start postgresql@14

# Redis (macOS with Homebrew)
brew services start redis

# Or use your system's package manager
```

7. Create the database:
```bash
createdb finance_planner
# Or using psql:
# psql -U postgres -c "CREATE DATABASE finance_planner;"
```

8. Run the backend:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file:
```bash
cp .env.local.example .env.local
```

4. Edit `.env.local` and set:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

5. Run the frontend:
```bash
npm run dev
```

## Option 2: Docker Setup

1. Create a `.env` file in the project root with all required variables (see backend/.env.example)

2. Start all services:
```bash
docker-compose up -d
```

3. View logs:
```bash
docker-compose logs -f
```

4. Stop services:
```bash
docker-compose down
```

## Accessing the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Getting Plaid Credentials

1. Sign up at https://dashboard.plaid.com/
2. Create a new application
3. Get your `client_id` and `secret` from the dashboard
4. Use the sandbox environment for testing
5. Add these to your `.env` file

## Getting OpenAI API Key

1. Sign up at https://platform.openai.com/
2. Create an API key
3. Add it to your `.env` file as `OPENAI_API_KEY`

## First Steps

1. Register a new account at http://localhost:3000/login
2. Connect a bank account using Plaid Link (sandbox credentials)
3. View your transactions and create budgets
4. Use the chat interface to ask questions about your finances

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in `.env` matches your PostgreSQL setup

### Redis Connection Issues
- Ensure Redis is running: `redis-cli ping`
- Should return `PONG`

### Plaid Integration Issues
- Verify your Plaid credentials in `.env`
- Check that you're using the correct environment (sandbox for testing)
- Ensure your redirect URI matches your frontend URL

### Frontend Not Connecting to Backend
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Ensure backend is running on port 8000
- Check CORS settings in backend `main.py`
