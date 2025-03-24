from fastapi import APIRouter, HTTPException, Depends

# Custom package imports
from rag.calls import get_response

router = APIRouter()

@router.get("/{rag}")
def rag_endpoint(rag: str):
    """
    Endpoint to pass a user prompt to the LangChain RAG pipeline.
    """
    try:
        response = get_response(rag)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))