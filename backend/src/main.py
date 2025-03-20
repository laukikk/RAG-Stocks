from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

# Custom imports
from postgresql.calls import get_user_portfolios
from postgresql.neon_client import NeonClient
from rag.calls import get_response

# Initialize Clients
app = FastAPI()
neon_client = NeonClient()

# Add CORS middleware to allow requests from the frontend (Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic models for request bodies
class TradeRequest(BaseModel):
    symbol: str
    quantity: int
    side: str

class RagQuery(BaseModel):
    query: str

@app.get("/")
def root():
    """
    Basic health check endpoint.
    """
    return {"message": "Welcome to the RAG-Stocks API"}

@app.get("/portfolios/{user_id}")
def user_portfolios(user_id: int, db: Session = Depends(neon_client.get_db_session)):
    """
    Example endpoint that retrieves user portfolios from Neon Postgres.
    """
    try:
        portfolios = get_user_portfolios(user_id, db)
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

