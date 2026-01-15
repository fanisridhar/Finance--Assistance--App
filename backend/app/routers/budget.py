from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Budget, Transaction, User
from app.schemas import BudgetCreate, BudgetResponse
from app.services.security import get_current_user

router = APIRouter()

@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new budget"""
    new_budget = Budget(
        user_id=current_user.id,
        category=budget_data.category,
        monthly_limit=budget_data.monthly_limit,
        period_start=budget_data.period_start,
        period_end=budget_data.period_end
    )
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    
    # Update current spending
    await update_budget_spending(new_budget.id, db)
    
    return new_budget

@router.get("/", response_model=List[BudgetResponse])
async def get_budgets(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all budgets for the user"""
    query = db.query(Budget).filter(Budget.user_id == current_user.id)
    
    if active_only:
        query = query.filter(Budget.is_active == True)
    
    budgets = query.all()
    
    # Update spending for each budget
    for budget in budgets:
        await update_budget_spending(budget.id, db)
        db.refresh(budget)
    
    return budgets

@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    await update_budget_spending(budget.id, db)
    db.refresh(budget)
    
    return budget

@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    budget.category = budget_data.category
    budget.monthly_limit = budget_data.monthly_limit
    budget.period_start = budget_data.period_start
    budget.period_end = budget_data.period_end
    
    db.commit()
    db.refresh(budget)
    
    await update_budget_spending(budget.id, db)
    db.refresh(budget)
    
    return budget

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    db.delete(budget)
    db.commit()
    
    return None

async def update_budget_spending(budget_id: int, db: Session):
    """Update the current spending for a budget"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        return
    
    # Calculate spending for the budget period
    transactions = db.query(Transaction).filter(
        and_(
            Transaction.user_id == budget.user_id,
            Transaction.category == budget.category,
            Transaction.date >= budget.period_start,
            Transaction.date <= budget.period_end,
            Transaction.is_pending == False,
            Transaction.amount < 0  # Only expenses
        )
    ).all()
    
    total_spending = sum(abs(t.amount) for t in transactions)
    budget.current_spending = total_spending
    db.commit()

