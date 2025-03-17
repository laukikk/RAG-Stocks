from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import functions from other modules
from neon_postgres import get_user_portfolios
from llm_config import get_response


app = FastAPI()

# Add CORS middleware to allow requests from the frontend (Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js app's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic models for request bodies
class TradeRequest(BaseModel):
    symbol: str
    quantity: int
    side: str  # "buy" or "sell"

class RagQuery(BaseModel):
    query: str

@app.get("/")
def root():
    """
    Basic health check endpoint.
    """
    return {"message": "Welcome to the RAG-Stocks API"}

@app.get("/portfolios/{user_id}")
def user_portfolios(user_id: int):
    """
    Example endpoint that retrieves user portfolios from Neon Postgres.
    """
    try:
        portfolios = get_user_portfolios(user_id)
        return {"portfolios": portfolios}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rag/{rag}")
def rag_endpoint(rag: str):
    """
    Endpoint to pass a user prompt to the LangChain RAG pipeline.
    """
    try:
        response = get_response(rag)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

