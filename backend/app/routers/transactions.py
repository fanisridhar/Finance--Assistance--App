from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Transaction, User
from app.schemas import TransactionResponse
from app.services.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None,
    account_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions with optional filters"""
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if category:
        query = query.filter(Transaction.category == category)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    
    transactions = query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()
    return transactions

@router.get("/summary")
async def get_transaction_summary(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction summary for the last N days"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    transactions = db.query(Transaction).filter(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.is_pending == False
        )
    ).all()
    
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    net = total_income - total_expenses
    
    # Group by category
    category_totals = {}
    for t in transactions:
        if t.amount < 0:  # Only expenses
            category = t.category or "Uncategorized"
            category_totals[category] = category_totals.get(category, 0) + abs(t.amount)
    
    # Get top categories
    top_categories = sorted(
        category_totals.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10]
    
    return {
        "period_days": days,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net": net,
        "transaction_count": len(transactions),
        "category_breakdown": dict(top_categories)
    }

@router.get("/categories")
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all unique categories from transactions"""
    categories = db.query(Transaction.category).filter(
        Transaction.user_id == current_user.id,
        Transaction.category.isnot(None)
    ).distinct().all()
    
    return [cat[0] for cat in categories]

