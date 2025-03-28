from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Custom package imports
from routers.trading_routes import trading_platform_router
from routers.database_routes import database_router
from routers.rag_routes import router as rag_router

app = FastAPI(
    title="RAG-Stocks API",
    description="API for RAG-powered stock trading platform",
    version="0.1.0"
)

@app.get("/", tags=["Health"])
def root():
    """
    Basic health check endpoint.
    """
    return {"message": "Welcome to the RAG-Stocks API", "status": "healthy"}

# Routers
app.include_router(trading_platform_router)
app.include_router(database_router)
app.include_router(rag_router, prefix="/rag", tags=["rag"])

# CORS middleware to allow requests from the frontend (Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Consider using environment variables
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)