# Deployment Guide

This guide covers deploying the GuppShupp Memory & Personality Engine to various platforms.

---

## Quick Deploy Options

| Platform | Best For | Free Tier | Setup Time |
|----------|----------|-----------|------------|
| **Streamlit Cloud** | Demo hosting | Yes | 5 min |
| **Railway** | Full API + Frontend | Yes (limited) | 10 min |
| **Render** | API hosting | Yes | 10 min |

---

## Option 1: Streamlit Cloud (Recommended for Demo)

Streamlit Cloud is the easiest option for hosting the demo. It's free and handles everything.

### Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Connect your GitHub repo**

4. **Configure the app**
   - Main file path: `app.py`
   - Python version: 3.10+

5. **Add Secrets**
   - Go to "Advanced settings" → "Secrets"
   - Add:
     ```toml
     GROQ_API_KEY = "your_groq_api_key_here"
     ```

6. **Deploy**

Your app will be live at: `https://your-app-name.streamlit.app`

---

## Option 2: Railway (API + Frontend)

Railway can host both the FastAPI backend and Streamlit frontend.

### Steps

1. **Create `railway.json`** in project root:
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "streamlit run app.py --server.port $PORT --server.address 0.0.0.0",
       "restartPolicyType": "ON_FAILURE"
     }
   }
   ```

2. **Create `Procfile`**:
   ```
   web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```

3. **Push to GitHub**

4. **Go to [railway.app](https://railway.app)**

5. **Create new project → Deploy from GitHub repo**

6. **Add environment variable**
   - Key: `GROQ_API_KEY`
   - Value: Your API key

7. **Deploy**

---

## Option 3: Render (API Only)

Good for hosting just the FastAPI backend.

### Steps

1. **Create `render.yaml`**:
   ```yaml
   services:
     - type: web
       name: guppshupp-api
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn server:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: GROQ_API_KEY
           sync: false
   ```

2. **Push to GitHub**

3. **Go to [render.com](https://render.com)**

4. **New → Web Service → Connect repo**

5. **Add environment variable**: `GROQ_API_KEY`

6. **Deploy**

---

## Local Development

### Setup

```bash
# Clone
git clone https://github.com/dumko2001/guppshupp-personality-engine.git
cd guppshupp-personality-engine

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add GROQ_API_KEY
```

### Run Streamlit Demo

```bash
streamlit run app.py
```

Open: http://localhost:8501

### Run FastAPI Server

```bash
uvicorn server:app --reload --port 8000
```

Open: http://localhost:8000/docs (Swagger UI)

---

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run unit tests (no API calls)
pytest tests/test_models.py -v

# Run integration tests (uses API - be mindful of rate limits)
pytest tests/test_integration.py -v --tb=short
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Your Groq API key from [console.groq.com](https://console.groq.com) |

---

## Troubleshooting

### "GROQ_API_KEY not found"

Make sure the API key is set:
- Local: Check `.env` file exists with the key
- Streamlit Cloud: Add to Secrets in dashboard
- Railway/Render: Add as environment variable

### Rate Limit Errors (429)

The free tier has limits. If you hit them:
- Wait a minute before retrying
- Use fewer messages in extraction
- Upgrade to a paid Groq plan

### Import Errors

Make sure you're running from the project root:
```bash
cd /path/to/guppshupp-personality-engine
streamlit run app.py
```

---

## Project Structure for Contributors

```
gupshup/
├── src/
│   ├── models/           # Pydantic schemas (start here)
│   ├── extractors/       # Memory extraction logic
│   ├── personality/      # Personality transformation
│   ├── llm/              # Groq client wrapper
│   └── api/              # FastAPI routes
├── tests/                # Unit + integration tests
├── data/                 # Sample messages
├── app.py                # Streamlit entry point
├── server.py             # FastAPI entry point
└── requirements.txt
```

### Adding a New Personality

1. Edit `src/personality/profiles.py`
2. Add a new entry to the `PROFILES` dict
3. Test with: `pytest tests/test_integration.py::TestPersonalityEngine -v`

### Adding a New Extractor

1. Create `src/extractors/your_extractor.py`
2. Add prompt to `src/llm/prompts.py`
3. Register in `src/extractors/orchestrator.py`
4. Add tests in `tests/test_integration.py`
