# Repository Scorer

> An intelligent repository quality assessment tool with professional web interface, powered by local LLM (Ollama)

## Overview

A modern **Streamlit web application** that conducts intelligent repository assessments using local LLM (Ollama). The application interprets user answers in real-time, applies weighted scoring, and produces a comprehensive quality score out of 100.

### AI-Powered Question Importance Weighting

**NEW:** The LLM intelligently evaluates and weights each question based on its importance:

- **On-Demand Scoring**: Each question is scored right before it's displayed to you
- **Critical practices get higher scores**: Security, branch protection, and CI/CD enforcement are weighted more heavily
- **Fair scoring**: Points are redistributed based on actual impact on repository health
- **Visible in Results**: Detailed breakdown shows importance rating, priority level, and impact score for each question
- **Transparent Process**: Console logs show LLM requests, responses, and parsed scores in real-time

This ensures that critical governance practices contribute more to your final score than minor improvements.

## Architecture

```
User → Streamlit Web UI
         ↓
Question Orchestrator (Python)
         ↓
Local LLM (Ollama) ← AI scores importance & classifies answers
         ↓
Scoring Engine
         ↓
Interactive Results Dashboard
```

**No databases. No GitHub access. No secrets. 100% local.**

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
- **Ollama** (Local LLM)
- **Pydantic** (Data validation)

## Recommended Models

| Model                 | Characteristics      |
| --------------------- | -------------------- |
| `phi-3:mini`          | Extremely fast       |
| `llama3.2:3b`         | Fast, good reasoning |
| `mistral:7b-instruct` | Better reasoning     |

**Start with `phi-3:mini`**

## Prerequisites

1. **Install Ollama**: [https://ollama.ai](https://ollama.ai)
2. **Pull a model**:
   ```bash
   ollama pull phi-3:mini
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
3. Score question importance on-demand as you progress
4. Provide binary YES/NO responses for clear assessment
5. Show comprehensive results with interactive charts and detailed breakdowns
6. Allow export of results as JSON

### Features

- **Modern UI**: Professional design with dark blue theme and clean interface
- **Real-time Scoring**: Questions scored individually as you answer them
- **Visual Feedback**: Progress tracking, gauge charts, and pillar breakdowns
- **Detailed Logging**: Console shows LLM interactions, responses, and scoring decisions
- **Binary Assessment**: Simple YES/NO responses eliminate misclassification
- **Export Results**: Download assessment results as JSON for record-keeping

## Example Output

```
🔍 Scoring Question Importance...
   Question: Are repositories organized using organizations and teams...
   Current max score: 6.67 points
   🤖 Sending request to LLM (phi-3:mini)...
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

## Configuration

Edit `.env` file to customize:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi-3:mini
```

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
│           └── ollama_service.py  # LLM interaction
├── requirements.txt
└── README.md
```

## Contributing

This is a self-contained assessment tool. To add questions:

1. Edit `src/repo_scorer/config.py`
2. Add questions to appropriate pillar
3. Restart the Streamlit app

## License

MIT

## Troubleshooting

**Issue**: "Cannot connect to Ollama"

- **Solution**: Ensure Ollama is running: `ollama serve`

**Issue**: "Model not found"

- **Solution**: Pull the model: `ollama pull phi-3:mini`

**Issue**: "Importance scoring timeout"

- **Solution**: Model may be slow. Check system resources or try a faster model like `phi-3:mini`

---

Built with ❤️ using local AI - no data leaves your machine

## License

MIT
