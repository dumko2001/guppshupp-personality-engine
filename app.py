"""
GuppShupp Memory & Personality Engine - Streamlit Demo

This demo uses DIRECT IMPORTS (not API calls) for deployment reliability.
The FastAPI server in server.py demonstrates the microservice architecture,
but for the hosted demo, we run everything in-process to avoid cold start issues.
"""
import streamlit as st
import asyncio
import json
from pathlib import Path

# Direct imports for deployment safety (no API calls needed)
from src.llm.client import GroqClient
from src.extractors.orchestrator import MemoryOrchestrator
from src.personality.engine import PersonalityEngine
from src.personality.profiles import PROFILES
from src.models.messages import ChatMessage
from src.models.memory import UserMemory

# Page config
st.set_page_config(
    page_title="GuppShupp AI - Memory & Personality",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Premium CSS Theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main Header */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
        text-align: center;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 1rem;
    }
    
    .dark-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        margin-bottom: 1rem;
    }
    
    /* Metrics */
    .metric-container {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        flex: 1;
        color: white;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Personality Cards */
    .personality-calm {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        height: 100%;
    }
    
    .personality-witty {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        height: 100%;
    }
    
    .personality-therapist {
        background: linear-gradient(135deg, #5ee7df 0%, #b490ca 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        height: 100%;
    }
    
    .personality-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .personality-desc {
        font-size: 0.85rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    .personality-response {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 1rem;
        font-size: 0.95rem;
        line-height: 1.6;
        backdrop-filter: blur(10px);
    }
    
    /* Generic Response */
    .generic-response {
        background: #f3f4f6;
        border-radius: 12px;
        padding: 1rem;
        color: #374151;
        border-left: 4px solid #9ca3af;
        margin-bottom: 1.5rem;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Memory Items */
    .memory-item {
        background: #f9fafb;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 3px solid #667eea;
    }
    
    .memory-category {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #667eea;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    
    .memory-content {
        font-size: 0.95rem;
        color: #374151;
        margin-bottom: 0.3rem;
    }
    
    .memory-evidence {
        font-size: 0.8rem;
        color: #6b7280;
        font-style: italic;
    }
    
    .confidence-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 0.7rem;
        padding: 0.2rem 0.5rem;
        border-radius: 20px;
        font-weight: 600;
    }
    
    /* Message List */
    .message-item {
        padding: 0.5rem 0;
        border-bottom: 1px solid #f3f4f6;
        font-size: 0.9rem;
        color: #4b5563;
    }
    
    .message-index {
        color: #9ca3af;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    
    /* Input */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        background: #f3f4f6;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
        margin: 2rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #9ca3af;
        font-size: 0.9rem;
    }
    
    .footer a {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
    }
    
    /* Success/Warning Messages */
    .stSuccess {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 10px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #374151;
    }
</style>
""", unsafe_allow_html=True)


# Initialize clients (cached for performance)
@st.cache_resource
def get_clients():
    """Initialize Groq client and orchestrators once."""
    client = GroqClient()
    orchestrator = MemoryOrchestrator(client)
    engine = PersonalityEngine(client)
    return client, orchestrator, engine


# Load sample messages
@st.cache_data
def load_sample_messages():
    """Load the 30 sample chat messages."""
    data_path = Path(__file__).parent / "data" / "sample_messages.json"
    with open(data_path) as f:
        data = json.load(f)
    return [ChatMessage(**m) for m in data]


def run_async(coro):
    """Helper to run async functions in Streamlit."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Main app
def main():
    # Header
    st.markdown('<p class="main-header">🗣️ GuppShupp AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Memory Extraction & Personality Engine for Bharat\'s First AI Lifelong Friend</p>', unsafe_allow_html=True)
    
    # Initialize
    try:
        client, orchestrator, engine = get_clients()
    except Exception as e:
        st.error(f"❌ Failed to initialize Groq client: {e}")
        st.info("💡 Make sure GROQ_API_KEY is set in your environment or .env file")
        return
    
    messages = load_sample_messages()
    
    # Layout: Two columns
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('<p class="section-header">📝 Chat History</p>', unsafe_allow_html=True)
        
        with st.expander(f"View {len(messages)} Sample Messages"):
            for i, msg in enumerate(messages):
                st.markdown(f'<div class="message-item"><span class="message-index">[{i}]</span>{msg.content}</div>', unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
        
        # Memory extraction
        if st.button("🧠 Extract Memory", type="primary", use_container_width=True):
            with st.spinner("Extracting preferences, emotions, and facts in parallel..."):
                try:
                    memory = run_async(orchestrator.extract_all(messages))
                    st.session_state.memory = memory
                    st.success("✅ Memory extracted successfully!")
                except Exception as e:
                    st.error(f"❌ Extraction failed: {e}")
    
    with col2:
        st.markdown('<p class="section-header">🧠 Extracted Memory</p>', unsafe_allow_html=True)
        
        if "memory" in st.session_state:
            memory = st.session_state.memory
            
            # Metrics with gradient boxes
            st.markdown(f'''
            <div class="metric-container">
                <div class="metric-box">
                    <div class="metric-value">{len(memory.preferences)}</div>
                    <div class="metric-label">Preferences</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{len(memory.emotional_patterns)}</div>
                    <div class="metric-label">Emotions</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{len(memory.facts)}</div>
                    <div class="metric-label">Facts</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Detailed view in tabs
            tab1, tab2, tab3 = st.tabs(["💜 Preferences", "💛 Emotions", "💙 Facts"])
            
            with tab1:
                if memory.preferences:
                    for p in memory.preferences[:5]:
                        st.markdown(f'''
                        <div class="memory-item">
                            <div class="memory-category">{p.category} <span class="confidence-badge">{p.confidence:.0%}</span></div>
                            <div class="memory-content">{p.description}</div>
                            <div class="memory-evidence">"{p.evidence}"</div>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.info("No preferences extracted")
            
            with tab2:
                if memory.emotional_patterns:
                    for e in memory.emotional_patterns[:5]:
                        st.markdown(f'''
                        <div class="memory-item">
                            <div class="memory-category">{e.frequency}</div>
                            <div class="memory-content">{e.pattern}</div>
                            <div class="memory-evidence">Triggers: {', '.join(e.triggers[:3])}</div>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.info("No emotional patterns extracted")
            
            with tab3:
                if memory.facts:
                    for f in memory.facts[:5]:
                        importance_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                        st.markdown(f'''
                        <div class="memory-item">
                            <div class="memory-category">{f.category} {importance_emoji.get(f.importance, "⚪")} <span class="confidence-badge">{f.confidence:.0%}</span></div>
                            <div class="memory-content">{f.fact}</div>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.info("No facts extracted")
            
            # Show errors if any
            if memory.extraction_errors:
                with st.expander("⚠️ Extraction Errors"):
                    for err in memory.extraction_errors:
                        st.warning(err)
        else:
            st.markdown('''
            <div class="glass-card" style="text-align: center; padding: 3rem;">
                <p style="font-size: 3rem; margin-bottom: 1rem;">🧠</p>
                <p style="color: #6b7280; font-size: 1rem;">Click <b>Extract Memory</b> to analyze the chat history</p>
            </div>
            ''', unsafe_allow_html=True)
    
    # Divider
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Personality testing section
    st.markdown('<p class="section-header">💬 Test Personality Engine</p>', unsafe_allow_html=True)
    
    query = st.text_input(
        "Your message:",
        value="I've been so stressed about work lately...",
        placeholder="Type a message to see how different personalities respond",
        label_visibility="collapsed"
    )
    
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    
    if st.button("🎭 Generate Personality Responses", type="primary", use_container_width=True):
        if "memory" not in st.session_state:
            st.warning("⚠️ Please extract memory first!")
        else:
            memory = st.session_state.memory
            
            with st.spinner("Generating responses with different personalities..."):
                try:
                    # Generate generic response (no memory)
                    generic = run_async(engine.generate_generic_response(query))
                    
                    # Generate personalized responses
                    responses = run_async(engine.generate_comparison(query, memory))
                    
                    # Display results
                    st.markdown("### ❌ Without Memory (Generic)")
                    st.markdown(f'<div class="generic-response">{generic}</div>', unsafe_allow_html=True)
                    
                    st.markdown("### ✅ With Memory + Personality")
                    
                    cols = st.columns(3, gap="medium")
                    
                    personality_styles = {
                        "calm-mentor": ("personality-calm", "🧘 Calm Mentor", "Warm, patient guide using Socratic questioning"),
                        "witty-friend": ("personality-witty", "😄 Witty Friend", "Playful companion using humor and references"),
                        "therapist": ("personality-therapist", "💜 Therapist", "Empathetic listener using reflective techniques"),
                    }
                    
                    for i, (pid, resp) in enumerate(responses.items()):
                        with cols[i]:
                            style, title, desc = personality_styles.get(pid, ("personality-calm", pid, ""))
                            st.markdown(f'''
                            <div class="{style}">
                                <div class="personality-title">{title}</div>
                                <div class="personality-desc">{desc}</div>
                                <div class="personality-response">{resp.response}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Generation failed: {e}")
    
    # Footer
    st.markdown('''
    <div class="footer">
        Built for <b>GuppShupp</b> • Founding AI Engineer Assignment • 
        <a href="https://github.com/dumko2001/guppshupp-personality-engine" target="_blank">GitHub</a>
    </div>
    ''', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
