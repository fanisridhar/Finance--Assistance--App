from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Transaction Schemas
class TransactionBase(BaseModel):
    amount: float
    date: datetime
    name: str
    merchant_name: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None

class TransactionCreate(TransactionBase):
    plaid_transaction_id: str
    account_id: int
    category_id: Optional[str] = None
    is_pending: bool = False
    payment_channel: Optional[str] = None
    location: Optional[Dict[str, Any]] = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    account_id: int
    category: Optional[str]
    category_confidence: Optional[float]
    is_pending: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Account Schemas
class AccountBase(BaseModel):
    name: str
    type: Optional[str] = None
    balance: float

class AccountResponse(AccountBase):
    id: int
    user_id: int
    plaid_account_id: str
    official_name: Optional[str]
    subtype: Optional[str]
    mask: Optional[str]
    currency: str
    is_active: bool
    
    class Config:
        from_attributes = True

# Budget Schemas
class BudgetCreate(BaseModel):
    category: str
    monthly_limit: float
    period_start: datetime
    period_end: datetime

class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category: str
    monthly_limit: float
    current_spending: float
    period_start: datetime
    period_end: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# Plaid Schemas
class PlaidLinkTokenResponse(BaseModel):
    link_token: str
    expiration: str

class PlaidExchangeTokenRequest(BaseModel):
    public_token: str
    institution_id: Optional[str] = None
    institution_name: Optional[str] = None

class PlaidExchangeTokenResponse(BaseModel):
    success: bool
    item_id: str
    message: str

# Chat Schemas
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    suggestions: Optional[List[str]] = None

