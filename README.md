# DevSecOps Repository Assessment Tool

AI-powered repository governance assessment platform using Azure OpenAI.

## Project Structure

```
├── backend/              # FastAPI backend server
│   ├── main.py          # API endpoints
│   ├── database.py      # Database models & operations
│   ├── email_service.py # Email functionality
│   └── requirements.txt # Python dependencies
│
├── frontend/            # React + TypeScript frontend
│   ├── src/            # Source code
│   ├── public/         # Static assets
│   └── package.json    # Node dependencies
│
├── src/                # Core Python package
│   └── repo_scorer/
│       ├── config.py        # Assessment questions & config
│       ├── models.py        # Data models
│       ├── orchestrator.py  # Assessment orchestration
│       ├── scoring.py       # Scoring logic
│       └── services/
│           └── azure_openai_service.py  # AI integration
│
├── .env                # Environment variables (not in git)
├── .gitignore         # Git ignore rules
└── requirements.txt   # Root Python dependencies
```

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Create `.env` files in root and backend directories:

```env
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
```

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Azure OpenAI
- **Frontend**: React, TypeScript, TailwindCSS, Vite
- **AI**: Azure OpenAI GPT-4
