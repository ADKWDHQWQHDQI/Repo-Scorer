# DevSecOps Repository Assessment Tool

AI-powered repository governance assessment platform using Azure OpenAI. This tool helps organizations assess their repository management practices across GitHub, GitLab, and Azure DevOps.

## 🚀 Quick Start for Local Development

### Option 1: Automated Setup (Recommended)

**Windows:**

```bash
setup.bat
```

**macOS/Linux:**

```bash
chmod +x setup.sh
./setup.sh
```

Then follow the prompts to configure your credentials in `backend/.env`.

### Option 2: Manual Setup

See detailed instructions in [LOCAL_SETUP.md](LOCAL_SETUP.md).

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **Azure OpenAI Service** account with API key
- **Gmail account** with App Password for email notifications

## 🏗️ Project Structure

```
├── backend/              # FastAPI backend server
│   ├── main.py          # API endpoints
│   ├── orchestrator.py  # Assessment orchestration
│   ├── azure_openai_service.py  # AI integration
│   ├── email_service.py # Email functionality
│   ├── database.py      # Database models & operations
│   ├── config.py        # Assessment questions & config
│   ├── scoring.py       # Scoring logic
│   ├── models.py        # Data models
│   ├── .env.example     # Environment template
│   └── requirements.txt # Python dependencies
│
├── frontend/            # React + TypeScript frontend
│   ├── src/            # Source code
│   │   ├── components/ # React components
│   │   ├── pages/      # Page components
│   │   ├── services/   # API services
│   │   ├── store/      # State management
│   │   └── types/      # TypeScript types
│   ├── public/         # Static assets
│   ├── .env.local      # Local environment config
│   └── package.json    # Node dependencies
│
├── LOCAL_SETUP.md      # Detailed setup guide
├── setup.bat           # Windows setup script
├── setup.sh            # macOS/Linux setup script
└── README.md           # This file
```

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env` from `backend/.env.example`:

```env
# Azure OpenAI (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# Gmail SMTP (Required for email notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-gmail-app-password

# Application
BASE_URL=http://localhost:5173
```

**Getting Gmail App Password:**

1. Enable 2-Step Verification in your Google Account
2. Go to Security > App passwords
3. Generate a password for "Mail"
4. Use the 16-character password in SENDER_PASSWORD

### Frontend Environment Variables

Already configured in `frontend/.env.local`:

```env
VITE_API_URL=http://localhost:8000
```

## 🎯 Running the Application

### Start Backend

```bash
cd backend
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run server
python main.py
```

Backend runs at: **http://localhost:8000**

### Start Frontend (in new terminal)

```bash
cd frontend
npm run dev
```

Frontend runs at: **http://localhost:5173**

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 💡 Features

- ✅ Multi-platform support (GitHub, GitLab, Azure DevOps)
- ✅ AI-powered analysis using Azure OpenAI GPT-4
- ✅ Real-time assessment with instant feedback
- ✅ Email delivery of results with shareable links
- ✅ Comprehensive scoring across 5 pillars:
  - Security
  - Governance
  - Code Review
  - Repository Management
  - Process Metrics
- ✅ Work email validation (blocks personal domains)
- ✅ Responsive UI with modern design

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Azure OpenAI SDK, Pydantic
- **Frontend**: React 18, TypeScript, TailwindCSS, Vite, Zustand
- **AI**: Azure OpenAI GPT-4
- **Database**: SQLite (local) / Azure SQL (production)
- **Email**: SMTP (Gmail)
- **Deployment**: Azure Static Web Apps + Azure App Service

## 📚 API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐛 Troubleshooting

### "Azure OpenAI API key is required"

- Ensure `backend/.env` file exists
- Verify `AZURE_OPENAI_API_KEY` is set correctly
- Check for extra spaces or quotes

### "Email configuration error"

- Confirm Gmail App Password is set in `SENDER_PASSWORD`
- Ensure 2-Step Verification is enabled on your Google account

### "Cannot connect to backend"

- Verify backend is running on port 8000
- Check `frontend/.env.local` has correct backend URL
- Ensure no firewall is blocking the connection

See [LOCAL_SETUP.md](LOCAL_SETUP.md) for more detailed troubleshooting.

## 🚢 Production Deployment

The application is configured for Azure deployment:

- **Frontend**: Azure Static Web Apps
- **Backend**: Azure App Service (Python)
- **Database**: Azure SQL Database

See production configuration in:

- `frontend/.env.production`
- `frontend/public/staticwebapp.config.json`

## 📝 License

This project is proprietary.

## 🤝 Contributing

For contributions, please follow the existing code structure and add appropriate tests.
