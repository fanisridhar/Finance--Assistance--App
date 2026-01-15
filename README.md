# Personal Finance Planner Agent

A personal finance management system that aggregates banking data, categorizes spending, and provides AI-powered budget suggestions.

## Tech Stack

- Frontend: Next.js 14 (React)
- Backend: FastAPI (Python)
- Database: PostgreSQL
- Cache: Redis
- Banking Integration: Plaid (Sandbox)
- AI/ML: LangChain for explainability
- Security: Encryption for sensitive data

## Features

- Secure bank data integration via Plaid
- Automatic transaction classification with embeddings
- AI-powered budget suggestions
- Interactive chat UI for budget queries
- Transaction analysis and insights

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker (optional, for containerized setup)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Environment Variables

Create `.env` files in both `backend/` and `frontend/` directories. See `.env.example` files for required variables.

### Running Locally

Backend:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm run dev
```

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── routers/      # API routes
│   │   ├── services/     # Business logic
│   │   ├── models.py     # Database models
│   │   └── schemas.py    # Pydantic schemas
│   ├── main.py          # FastAPI app entry point
│   └── requirements.txt  # Python dependencies
├── frontend/            # Next.js frontend
│   ├── app/             # Next.js app directory
│   ├── lib/             # Utility functions
│   └── package.json     # Node dependencies
├── docker-compose.yml   # Docker setup
├── SETUP.md            # Detailed setup instructions
└── README.md           # This file
```

## Quick Start

1. Clone and setup environment variables:
   ```bash
   # Backend
   cd backend
   cp .env.example .env
   # Edit .env with your Plaid and OpenAI credentials
   
   # Frontend
   cd frontend
   cp .env.local.example .env.local
   ```

2. Start services (PostgreSQL and Redis must be running):
   ```bash
   # Option 1: Use the start script
   ./start.sh
   
   # Option 2: Manual start
   # Terminal 1 - Backend
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   
   # Terminal 2 - Frontend
   cd frontend
   npm install
   npm run dev
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Features Overview

### Authentication
- User registration and login
- JWT-based authentication
- Secure password hashing

### Bank Integration
- Plaid Link integration for secure bank connections
- Automatic transaction syncing
- Support for multiple accounts

### AI-Powered Features
- Transaction classification using ML embeddings
- LangChain agent for natural language queries
- Budget suggestions based on spending patterns
- Explainable AI for financial insights

### Budget Management
- Create and manage budgets by category
- Real-time spending tracking
- Budget alerts and notifications
- Historical budget analysis

### Chat Interface
- Natural language queries about finances
- Budget recommendations
- Spending analysis
- Financial advice

## Security

- All sensitive data (Plaid access tokens) is encrypted at rest
- JWT tokens for authentication
- Password hashing with bcrypt
- CORS protection
- Input validation with Pydantic

## Development

See SETUP.md for detailed setup instructions and troubleshooting.

## License

This project is for educational purposes.
