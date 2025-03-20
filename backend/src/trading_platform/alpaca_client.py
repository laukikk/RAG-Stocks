from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class AlpacaClient:
    _instance = None
    _client = None
    
    def __new__(cls):
        """Ensure only one instance of AlpacaClient is created."""
        if cls._instance is None:
            cls._instance = super(AlpacaClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        try:
            api_key = os.getenv('ALPACA_PAPER_API_KEY')
            secret_key = os.getenv('ALPACA_PAPER_API_SECRET')
            self._client = TradingClient(api_key, secret_key, paper=True)
        except Exception as e:
            raise Exception(f"Failed to initialize Alpaca client: {str(e)}")
        
    @property
    def client(self):
        """Get the Alpaca TradingClient instance."""
        return self._client
    
    
if __name__ == "__main__":
    # Example usage
    alpaca_client_instance = AlpacaClient()
    client = alpaca_client_instance.client
    
    # Get account information
    account = client.get_account()
    print("Account Information:")
    print(f"Account ID: {account.id}")
    print(f"Cash: ${account.cash}")
    print(f"Portfolio Value: ${account.portfolio_value}")