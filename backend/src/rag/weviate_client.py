import os
import weaviate
from dotenv import load_dotenv
from weaviate.classes.init import Auth

# Load environment variables
load_dotenv()

class WeviateClient:
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WeviateClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Weaviate client"""
        WEAVIATE_URL = os.getenv("WEAVIATE_URL")
        WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
        
        try:
            self._client = weaviate.connect_to_weaviate_cloud(
                cluster_url=WEAVIATE_URL,
                auth_credentials=Auth.api_key(WEAVIATE_API_KEY)
            )
        except Exception as e:
            raise Exception(f"Weaviate client initialization failed: {str(e)}")
        
    @property
    def client(self):
        """Get Weaviate client"""
        return self._client
    
    def close(self):
        """Close the Weaviate client connection"""
        if self._client:
            self._client.close()
            self._client = None
    
if __name__ == "__main__":
    weaviate_client = WeviateClient()
    weaviate_client.close()