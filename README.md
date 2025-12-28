# GuppShupp Memory & Personality Engine

**AI-powered memory extraction and personality transformation for companion AI** — Built for the Founding AI Engineer assignment.

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Groq](https://img.shields.io/badge/LLM-Groq-orange.svg)
![FastAPI](https://img.shields.io/badge/API-FastAPI-green.svg)
![Streamlit](https://img.shields.io/badge/Demo-Streamlit-red.svg)

---

## 🎯 What This Does

Given **30 chat messages** from a user, this system:

1. **Extracts Memory** — Identifies preferences, emotional patterns, and facts
2. **Transforms Personality** — Generates responses in different tones (Calm Mentor, Witty Friend, Therapist)
3. **Shows Before/After** — Demonstrates how memory + personality changes the response

---

## 🏗 Architectural Decisions

### 1. Async Concurrency for High Throughput

To meet the "High-Throughput" requirement, I utilized Python's `asyncio`. The Memory Extraction module uses `asyncio.gather` to run the Preference, Emotion, and Fact extractors **in parallel**.

```python
results = await asyncio.gather(
    self.preference_extractor.extract(formatted),
    self.emotion_extractor.extract(formatted),
    self.fact_extractor.extract(formatted),
    return_exceptions=True  # Fault tolerance
)
```

**Result:** Reduces extraction latency from ~3s to ~0.8s on Groq.

### 2. Fault Tolerance Strategy

The orchestrator implements `return_exceptions=True`. In a production environment with millions of users, a failure in the "Fact Module" should not prevent the user from receiving a reply. The system **gracefully degrades** rather than crashing.

```python
# Handle partial failures gracefully
preferences = results[0] if not isinstance(results[0], Exception) else []
emotions = results[1] if not isinstance(results[1], Exception) else []
facts = results[2] if not isinstance(results[2], Exception) else []
```

### 3. Pydantic & Structured Outputs

Instead of relying on Regex or fragile text parsing, I use **Pydantic V2** models. These serve two purposes:

1. **Runtime Validation:** Ensures the UI never receives malformed data
2. **Schema Injection:** The Pydantic schemas constrain the LLM's output format

```python
class Preference(BaseModel):
    category: Literal["communication", "interests", "lifestyle", "values"]
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    source_message_ids: list[int]
    evidence: str
```

### 4. Confidence Scoring & Source Attribution

Every extracted memory item includes:
- **Confidence score (0-1)** — How certain are we about this extraction?
- **Source message IDs** — Which messages support this?
- **Evidence** — Direct quote or paraphrase

This makes the system **auditable** and **debuggable**.

### 5. Deployment Strategy

The GitHub repo shows a **microservice architecture** (FastAPI + Streamlit), but the hosted demo uses **direct imports** to avoid cold-start issues on free tiers:

```python
# DON'T DO THIS (risky for assignments):
# response = requests.post("http://api-url/extract", json=...)

# DO THIS (direct import):
from src.extractors.orchestrator import MemoryOrchestrator
memory = await orchestrator.extract_all(messages)
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/dumko2001/guppshupp-personality-engine.git
cd guppshupp-personality-engine
pip install -r requirements.txt
```

### 2. Set API Key

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Run the Demo

```bash
streamlit run app.py
```

### 4. (Optional) Run the API Server

```bash
uvicorn server:app --reload --port 8000
```

---

## 📁 Project Structure

```
gupshup/
├── src/
│   ├── models/           # Pydantic schemas
│   │   ├── memory.py     # UserMemory, Preference, Emotion, Fact
│   │   ├── messages.py   # ChatMessage
│   │   └── personality.py
│   │
│   ├── extractors/       # Memory extraction
│   │   ├── orchestrator.py  # Parallel extraction coordinator
│   │   ├── preferences.py
│   │   ├── emotions.py
│   │   └── facts.py
│   │
│   ├── personality/      # Personality Engine
│   │   ├── engine.py     # Response transformation
│   │   └── profiles.py   # Calm Mentor, Witty Friend, Therapist
│   │
│   ├── llm/              # Groq client
│   │   ├── client.py     # JSON mode + retry logic
│   │   └── prompts.py    # Extraction prompts
│   │
│   └── api/              # FastAPI routes
│       └── routes.py
│
├── app.py                # Streamlit demo
├── server.py             # FastAPI server
├── data/
│   └── sample_messages.json  # 30 sample messages
│
├── requirements.txt
└── README.md
```

---

## 🔧 Tech Stack

| Component | Technology | Why |
|-----------|------------|-----|
| **LLM** | Groq (llama-3.3-70b) | 280 tok/s, JSON mode |
| **Backend** | FastAPI | Async-first, production-ready |
| **Frontend** | Streamlit | Rapid demo, Python-native |
| **Validation** | Pydantic V2 | Type safety + JSON schema |

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/extract` | POST | Extract memory from messages |
| `/api/respond` | POST | Generate personality response |
| `/api/compare` | POST | Compare all personalities |
| `/health` | GET | Health check |

---

## 🎭 Personality Profiles

| Profile | Tone | Style |
|---------|------|-------|
| **🧘 Calm Mentor** | Warm, patient | Socratic questioning |
| **😄 Witty Friend** | Playful, quick | Humor, pop culture |
| **💜 Therapist** | Empathetic | Reflective listening |

---

## 📝 Sample Output

### Extracted Memory

```json
{
  "preferences": [
    {
      "category": "interests",
      "description": "Enjoys hiking and outdoor activities",
      "confidence": 0.9,
      "source_message_ids": [2, 12],
      "evidence": "User mentioned 'hiking this weekend was amazing'"
    }
  ],
  "emotional_patterns": [
    {
      "pattern": "Becomes stressed about work deadlines",
      "triggers": ["deadlines", "manager expectations"],
      "frequency": "frequent",
      "source_message_ids": [0, 7, 13]
    }
  ],
  "facts": [
    {
      "category": "professional",
      "fact": "Works at a startup for 2 years",
      "importance": "high",
      "confidence": 0.95
    }
  ]
}
```

### Personality Response Comparison

**Query:** "I've been so stressed about work lately..."

| Without Memory | With Memory (Calm Mentor) |
|----------------|---------------------------|
| Generic advice about stress | References their hiking hobby as a stress relief strategy |

---

## 🔒 Security

- API keys stored in `.env` (gitignored)
- No secrets in source code
- Rate limiting handled client-side

---

## 📄 License

MIT

---

Built with ❤️ for GuppShupp • Founding AI Engineer Assignment
