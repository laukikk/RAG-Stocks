import os
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Load environment variables
load_dotenv()

# Base class for SQLAlchemy models
Base = declarative_base()

class NeonClient:
    _instance = None
    _engine = None
    _session_factory = None
    _conn = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NeonClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize database connection"""
        NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL")
        if not NEON_DATABASE_URL:
            raise HTTPException(status_code=500, detail="NEON_DATABASE_URL not found in environment variables")
        
        try:
            self._engine = create_engine(NEON_DATABASE_URL)
            self._session_factory = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database engine initialization failed: {str(e)}")
        
        try:
            conn = psycopg2.connect(NEON_DATABASE_URL, cursor_factory=RealDictCursor)
            return conn
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database psycopg2 connection failed: {str(e)}")
    
    @property
    def engine(self):
        """Get SQLAlchemy engine"""
        return self._engine
    
    @property
    def connection(self):
        """Get psycopg2 connection"""
        return self._conn
    
    def get_db_session(self) -> Session:
        """Create a new SQLAlchemy session"""
        return self._session_factory()
            
    def close_connection(self):
        """Close the psycopg2 connection"""
        if self._conn:
            self._conn.close()
            self._conn = None