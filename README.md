# RAG-Stocks: AI-Powered Stock Research and Recommendation Platform

## Overview
RAG-Stocks is an advanced stock research and recommendation platform that leverages cutting-edge AI technologies to provide intelligent insights into financial markets. By combining Retrieval-Augmented Generation (RAG), real-time trading data, and natural language processing, this application offers comprehensive stock analysis and personalized investment recommendations.

## Features
- AI-Powered Stock Analysis
- Real-time Market Data
- Natural Language Query Interface
- Intelligent Stock Recommendations
- Portfolio Tracking

## Tech Stack
- **Frontend**: Next.js (React)
- **Backend**: Python
- **AI Technologies**: 
  - LangChain
  - Weaviate Vector Database
- **Trading API**: Alpaca
- **Database**: Neon PostgreSQL

## Prerequisites
- Python 3.9+
- Node.js 18+
- Docker (optional)

## Installation

### Clone the Repository
```bash
git clone https://github.com/laukikk/RAG-Stocks.git
cd RAG-Stocks
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd ../frontend
npm install
```

### Environment Configuration (all FREE plans)
1. Copy `.env.example` to `.env`
2. Fill in required API keys:
   - Alpaca Trading
   - Neon Database
   - OpenAI
   - Weaviate
   - GitHub Token: optional (I'm using GitHub Models)

## Running the Application

### Development Mode
```bash
# Start Backend
cd backend
python src/main.py

# Start Frontend (in another terminal)
cd frontend
npm run dev
```

### Docker Deployment (To-Do)
```bash
docker-compose up --build
```

## Testing (To-Do)
```bash
# Run Backend Tests
cd backend
python -m pytest tests/

# Run Frontend Tests
cd frontend
npm test
```