# Repository Scorer

> An intelligent repository quality assessment tool powered by local LLM (Ollama)

## Overview

A local LLM (Ollama) conducts an intelligent questionnaire, interprets user answers, applies weighted scoring, and produces a repo quality score out of 100.

### 🆕 AI-Driven Adaptive Questioning

The tool features **adaptive questioning** where AI dynamically decides what to ask next based on your responses:

- **Complete answers** → Skip follow-ups (faster assessment)
- **Partial/vague answers** → AI asks targeted follow-ups (deeper insights)
- **Different users get different question paths** (truly adaptive)

This is **true agent-like behavior** - AI controls the conversation flow, not just classification.

### 🎯 AI-Powered Question Importance Weighting

**NEW:** The LLM intelligently evaluates and weights each question based on its importance:

- **Dynamic Weight Assignment**: When questions are loaded, the AI examines each one and assigns an importance score (1-10)
- **Critical practices get higher scores**: Security, branch protection, and CI/CD enforcement are weighted more heavily
- **Fair scoring**: Points are redistributed based on actual impact on repository health
- **Visible in CLI**: Each question shows its importance rating (⭐⭐⭐⭐⭐) and weighted score

This ensures that critical governance practices contribute more to your final score than minor improvements.

📖 **Learn more**: See [ADAPTIVE_QUESTIONING_ENHANCEMENT.md](ADAPTIVE_QUESTIONING_ENHANCEMENT.md) and [VISUAL_FLOW.md](VISUAL_FLOW.md)

## Architecture

```
User
  ↓
Question Orchestrator (Python)
  ↓
Local LLM (Ollama) ← AI classifies answers + Decides next question
  ↓
Scoring Engine
  ↓
Final Score + Explanation
```

**No databases. No GitHub access. No secrets.**

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
- **Ollama** (local LLM)
- **FastAPI** (optional API)
- **Pydantic** (validation)

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

### CLI Mode (Interactive)

```bash
python src/repo_scorer/cli.py
```

The tool will:

1. Ask questions one at a time
2. Interpret your natural language answers
3. Calculate scores deterministically
4. Show final breakdown and summary

### API Mode (Optional)

```bash
uvicorn src.repo_scorer.main:app --reload
```

Then visit: `http://localhost:8000/docs`

## Example Output

```json
{
  "final_score": 67.5,
  "breakdown": {
    "governance": 12.5,
    "ci_cd": 22.5,
    "testing": 15,
    "code_quality": 10,
    "docs_security": 7.5
  },
  "summary": "Good CI/CD practices, but testing and governance need improvement."
}
```

## How It Works

### AI Responsibilities

- ✅ Ask questions naturally
- ✅ Understand fuzzy answers
- ✅ Classify answers as: `yes`, `partial`, `no`, `unsure`
- ✅ Ask follow-ups if unclear

### AI Does NOT

- ❌ Calculate scores (Python handles this)
- ❌ Define weights (predefined)
- ❌ Invent questions (fixed bank)

### Answer Classification

| User Answer       | Internal Value |
| ----------------- | -------------- |
| Yes               | 1.0            |
| Partial/Sometimes | 0.5            |
| No                | 0.0            |
| Not sure          | 0.25           |

## Why This Design

✅ Clear AI involvement  
✅ Simple architecture  
✅ No secrets required  
✅ Local LLM (privacy-friendly)  
✅ Explainable scoring  
✅ Extendable later  
✅ Fast & efficient

## License

MIT
