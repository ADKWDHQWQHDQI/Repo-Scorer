# Repository Scorer

> An intelligent repository quality assessment tool with professional web interface, powered by Azure OpenAI

## Overview

A modern **Streamlit web application** that conducts intelligent repository assessments using Azure OpenAI (GPT-4). The application interprets user answers in real-time, applies weighted scoring based on importance, and produces a comprehensive quality score out of 100.

### Manual Question Importance Weighting

Questions are **manually weighted by importance** to reflect their real-world impact on repository quality:

- **Critical (9-10)**: Security vulnerabilities, branch protection, secret scanning (~40% of total score)
- **High (7-8)**: Access control, code ownership, approval workflows (~30% of total score)
- **Moderate (4-6)**: Templates, commit conventions, repository strategy (~20% of total score)
- **Standard (1-3)**: Naming conventions, cleanup automation, metrics (~10% of total score)

This ensures that implementing critical security and quality practices has the most significant impact on your overall assessment score.

## Architecture

```
User → Streamlit Web UI
         ↓
Question Orchestrator (Python)
         ↓
Azure OpenAI (GPT-4) ← AI analyzes answers & generates insights
         ↓
Scoring Engine
         ↓
Interactive Results Dashboard
```

**Cloud-based AI with enterprise security. No local model required.**

## Scoring Pillars (Total = 100)

| Pillar                    | Weight  |
| ------------------------- | ------- |
| Governance & PR Practices | 20      |
| CI/CD                     | 25      |
| Testing                   | 20      |
| Code Quality              | 20      |
| Documentation & Security  | 15      |
| **Total**                 | **100** |

## Tech Stack

- **Python 3.10+**
- **Streamlit 1.52+** (Modern web interface)
- **Plotly 5.18+** (Interactive visualizations)
- **Azure OpenAI** (GPT-4 deployment)
- **Pydantic** (Data validation)

## Prerequisites

1. **Azure OpenAI Service**: Access to Azure OpenAI with GPT-4 deployment
2. **API Key**: Set up in `.env` file (see Configuration section)

## Configuration

Create a `.env` file in the project root:

```bash
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_API_VERSION=2025-01-01-preview
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Web Interface (Primary)

```bash
streamlit run streamlit_app.py
```

The application will:

1. Open automatically in your browser at `http://localhost:8501`
2. Display a professional welcome page with platform selection
3. Connect to Azure OpenAI for AI analysis
4. Provide binary YES/NO responses for clear assessment
5. Show comprehensive results with interactive charts and detailed breakdowns
6. Allow export of results as JSON

### Features

- **Modern UI**: Professional design with dark blue theme and clean interface
- **AI-Powered Insights**: Real-time analysis using Azure OpenAI GPT-4
- **Visual Feedback**: Progress tracking, gauge charts, and pillar breakdowns
- **Detailed Logging**: Console shows LLM interactions, responses, and scoring decisions
- **Binary Assessment**: Simple YES/NO responses eliminate misclassification
- **Export Results**: Download assessment results as JSON for record-keeping

## Example Output

```
🔍 Scoring Question Importance...
   Question: Are repositories organized using organizations and teams...
   Current max score: 6.67 points
   🤖 Sending request to LLM (qwen2.5:0.5b-instruct)...
   ⏱️  Timeout: 15 seconds
   📥 LLM Response: '8'
   ✨ Parsed Score: 8/10
   ✅ Updated max score: 8.00 points

Repository Quality Score: 87.5 / 100
Grade: Excellent

Pillar Breakdown:
✅ Governance & PR Practices: 18.5/20
✅ CI/CD Pipeline: 23.0/25
✅ Testing Strategy: 17.0/20
⚠️  Code Quality: 15.0/20
✅ Documentation & Security: 14.0/15
```

## How It Works

### Binary Assessment System

The application uses a simplified binary YES/NO system:

- **User selects**: YES or NO radio button
- **Score calculated**: YES = full points, NO = 0 points
- **No LLM classification**: Direct mapping eliminates misclassification
- **Transparent**: Every decision is deterministic and explainable

### AI Responsibilities

- ✅ Score question importance (1-10 scale)
- ✅ Evaluate impact of governance practices
- ✅ Provide varied importance distribution

### AI Does NOT

- ❌ Calculate scores (Python handles this)
- ❌ Classify YES/NO answers (direct user input)
- ❌ Define questions (fixed bank)
- ❌ Invent responses (user selects explicitly)

## Why This Design

✅ **Simple & Fast**: Binary responses, no ambiguity  
✅ **Accurate**: No misclassification of YES as NO  
✅ **Transparent**: Clear logging of all decisions  
✅ **Local**: No secrets, no external API calls  
✅ **Privacy-Friendly**: All processing on your machine  
✅ **Explainable**: Every score is traceable  
✅ **Professional UI**: Modern web interface with charts

## Development

Project structure:

```
├── streamlit_app.py          # Main Streamlit application
├── src/
│   └── repo_scorer/
│       ├── orchestrator.py   # Assessment orchestration
│       ├── config.py          # Question definitions
│       ├── models.py          # Data models
│       ├── scoring.py         # Scoring logic
│       └── services/
│           └── azure_openai_service.py  # Azure OpenAI integration
├── requirements.txt
└── README.md
```

## Contributing

This is a self-contained assessment tool. To add questions:

1. Edit `src/repo_scorer/config.py`
2. Add questions to appropriate pillar
3. Restart the Streamlit app

## Troubleshooting

**Issue**: "Cannot connect to Azure OpenAI service"

- **Solution**: Verify your API key and endpoint in `.env` file
- Check network connectivity to Azure

**Issue**: "Deployment not accessible"

- **Solution**: Verify deployment name matches your Azure OpenAI deployment
- Ensure your API key has proper permissions

---

Built with ❤️ using Azure OpenAI - Enterprise-grade AI security

## License

MIT
