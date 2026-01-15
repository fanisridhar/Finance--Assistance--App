from plaid.api import plaid_api
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
import os
from dotenv import load_dotenv

load_dotenv()

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")
PLAID_PRODUCTS = os.getenv("PLAID_PRODUCTS", "transactions").split(",")

configuration = Configuration(
    host=plaid_api.PlaidEnvironment[PLAID_ENV],
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET
    }
)

api_client = ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

def get_plaid_client():
    return plaid_client

