from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
from app.database import get_db
from app.models import User, PlaidItem, Account, Transaction
from app.schemas import (
    PlaidLinkTokenResponse,
    PlaidExchangeTokenRequest,
    PlaidExchangeTokenResponse
)
from app.services.security import get_current_user
from app.services.plaid_client import get_plaid_client
from app.services.encryption import encrypt_data, decrypt_data
from app.services.transaction_classifier import get_classifier
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.country_code import CountryCode
from datetime import datetime, timedelta
import json

router = APIRouter()

@router.post("/link-token", response_model=PlaidLinkTokenResponse)
async def create_link_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Plaid link token for connecting bank accounts"""
    plaid_client = get_plaid_client()
    
    try:
        link_request = LinkTokenCreateRequest(
            products=["transactions"],
            client_name="Personal Finance Planner",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=str(current_user.id)
            ),
            redirect_uri=os.getenv("PLAID_REDIRECT_URI", "http://localhost:3000")
        )
        
        link_response = plaid_client.link_token_create(link_request)
        
        return PlaidLinkTokenResponse(
            link_token=link_response['link_token'],
            expiration=link_response['expiration']
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create link token: {str(e)}"
        )

@router.post("/exchange-token", response_model=PlaidExchangeTokenResponse)
async def exchange_public_token(
    request: PlaidExchangeTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exchange Plaid public token for access token and sync accounts/transactions"""
    plaid_client = get_plaid_client()
    
    try:
        # Exchange public token for access token
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=request.public_token
        )
        exchange_response = plaid_client.item_public_token_exchange(exchange_request)
        
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']
        
        # Encrypt and store the access token
        encrypted_token = encrypt_data(access_token)
        
        # Check if item already exists
        existing_item = db.query(PlaidItem).filter(PlaidItem.item_id == item_id).first()
        if existing_item:
            existing_item.access_token = encrypted_token
            existing_item.institution_id = request.institution_id
            existing_item.institution_name = request.institution_name
            existing_item.is_active = True
        else:
            new_item = PlaidItem(
                user_id=current_user.id,
                item_id=item_id,
                access_token=encrypted_token,
                institution_id=request.institution_id,
                institution_name=request.institution_name
            )
            db.add(new_item)
        
        db.commit()
        
        # Sync accounts and transactions
        await sync_accounts_and_transactions(current_user.id, item_id, db)
        
        return PlaidExchangeTokenResponse(
            success=True,
            item_id=item_id,
            message="Bank account connected successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange token: {str(e)}"
        )

async def sync_accounts_and_transactions(user_id: int, item_id: str, db: Session):
    """Sync accounts and transactions from Plaid"""
    plaid_client = get_plaid_client()
    
    # Get the Plaid item
    plaid_item = db.query(PlaidItem).filter(PlaidItem.item_id == item_id).first()
    if not plaid_item:
        return
    
    access_token = decrypt_data(plaid_item.access_token)
    
    try:
        # Get accounts
        accounts_request = AccountsGetRequest(access_token=access_token)
        accounts_response = plaid_client.accounts_get(accounts_request)
        
        # Sync accounts
        for account_data in accounts_response['accounts']:
            existing_account = db.query(Account).filter(
                Account.plaid_account_id == account_data['account_id']
            ).first()
            
            if existing_account:
                existing_account.balance = account_data['balances']['available'] or account_data['balances']['current'] or 0
                existing_account.name = account_data['name']
                existing_account.official_name = account_data.get('official_name')
                existing_account.type = account_data['type']
                existing_account.subtype = account_data.get('subtype')
                existing_account.mask = account_data.get('mask')
            else:
                new_account = Account(
                    user_id=user_id,
                    plaid_account_id=account_data['account_id'],
                    name=account_data['name'],
                    official_name=account_data.get('official_name'),
                    type=account_data['type'],
                    subtype=account_data.get('subtype'),
                    mask=account_data.get('mask'),
                    balance=account_data['balances']['available'] or account_data['balances']['current'] or 0,
                    currency=account_data.get('balances', {}).get('iso_currency_code', 'USD')
                )
                db.add(new_account)
        
        db.commit()
        
        # Get transactions (last 30 days)
        start_date = (datetime.now() - timedelta(days=30)).date()
        end_date = datetime.now().date()
        
        transactions_request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )
        transactions_response = plaid_client.transactions_get(transactions_request)
        
        classifier = get_classifier()
        
        # Sync transactions
        for transaction_data in transactions_response['transactions']:
            existing_transaction = db.query(Transaction).filter(
                Transaction.plaid_transaction_id == transaction_data['transaction_id']
            ).first()
            
            if existing_transaction:
                continue  # Skip if already exists
            
            # Find the account
            account = db.query(Account).filter(
                Account.plaid_account_id == transaction_data['account_id']
            ).first()
            
            if not account:
                continue
            
            # Classify transaction
            category, confidence = classifier.classify_transaction(
                transaction_data['name'],
                transaction_data.get('merchant_name')
            )
            embedding = classifier.get_transaction_embedding(
                transaction_data['name'],
                transaction_data.get('merchant_name')
            )
            
            # Get Plaid category
            plaid_category = None
            plaid_category_id = None
            if transaction_data.get('category'):
                plaid_category = transaction_data['category'][0] if transaction_data['category'] else None
                plaid_category_id = transaction_data.get('category_id')
            
            new_transaction = Transaction(
                user_id=user_id,
                account_id=account.id,
                plaid_transaction_id=transaction_data['transaction_id'],
                amount=transaction_data['amount'],
                date=datetime.fromisoformat(transaction_data['date'].replace('Z', '+00:00')),
                name=transaction_data['name'],
                merchant_name=transaction_data.get('merchant_name'),
                category=category,  # Our ML classification
                category_id=plaid_category_id,
                subcategory=plaid_category,
                category_confidence=confidence,
                category_embedding=embedding,
                is_pending=transaction_data.get('pending', False),
                payment_channel=transaction_data.get('payment_channel'),
                location=transaction_data.get('location'),
                metadata=transaction_data.get('metadata')
            )
            db.add(new_transaction)
        
        db.commit()
        
    except Exception as e:
        print(f"Error syncing accounts/transactions: {str(e)}")
        raise

@router.post("/sync")
async def sync_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger sync of accounts and transactions"""
    plaid_items = db.query(PlaidItem).filter(
        PlaidItem.user_id == current_user.id,
        PlaidItem.is_active == True
    ).all()
    
    for item in plaid_items:
        await sync_accounts_and_transactions(current_user.id, item.item_id, db)
    
    return {"message": "Sync completed"}

