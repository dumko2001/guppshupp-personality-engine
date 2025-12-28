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
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .personality-card {
        background-color: #fafafa;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
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
    st.markdown('<p class="main-header">🗣️ GuppShupp Memory & Personality Engine</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered memory extraction and personality transformation for Bharat\'s First AI Lifelong Friend</p>', unsafe_allow_html=True)
    
    # Initialize
    try:
        client, orchestrator, engine = get_clients()
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")
        st.info("Make sure GROQ_API_KEY is set in your environment or .env file")
        return
    
    messages = load_sample_messages()
    
    # Layout: Two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Chat History (30 messages)")
        
        with st.expander("View Sample Messages", expanded=False):
            for i, msg in enumerate(messages):
                st.text(f"[{i}] {msg.content}")
        
        st.divider()
        
        # Memory extraction
        if st.button("🧠 Extract Memory", type="primary", use_container_width=True):
            with st.spinner("Extracting preferences, emotions, and facts in parallel..."):
                try:
                    memory = run_async(orchestrator.extract_all(messages))
                    st.session_state.memory = memory
                    st.success("Memory extracted successfully!")
                except Exception as e:
                    st.error(f"Extraction failed: {e}")
    
    with col2:
        st.subheader("🧠 Extracted Memory")
        
        if "memory" in st.session_state:
            memory = st.session_state.memory
            
            # Metrics row
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Preferences", len(memory.preferences))
            with m2:
                st.metric("Emotions", len(memory.emotional_patterns))
            with m3:
                st.metric("Facts", len(memory.facts))
            
            # Detailed view in tabs
            tab1, tab2, tab3 = st.tabs(["Preferences", "Emotions", "Facts"])
            
            with tab1:
                if memory.preferences:
                    for p in memory.preferences:
                        st.markdown(f"""
                        **{p.category.title()}** (confidence: {p.confidence:.0%})
                        > {p.description}
                        
                        *Evidence: {p.evidence}*
                        """)
                else:
                    st.info("No preferences extracted")
            
            with tab2:
                if memory.emotional_patterns:
                    for e in memory.emotional_patterns:
                        st.markdown(f"""
                        **Pattern:** {e.pattern}
                        - Triggers: {', '.join(e.triggers)}
                        - Frequency: {e.frequency}
                        - Emotions: {', '.join(e.emotional_range)}
                        """)
                else:
                    st.info("No emotional patterns extracted")
            
            with tab3:
                if memory.facts:
                    for f in memory.facts:
                        importance_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                        st.markdown(f"""
                        {importance_emoji.get(f.importance, "⚪")} **{f.category.title()}** (confidence: {f.confidence:.0%})
                        > {f.fact}
                        """)
                else:
                    st.info("No facts extracted")
            
            # Show errors if any
            if memory.extraction_errors:
                with st.expander("⚠️ Extraction Errors"):
                    for err in memory.extraction_errors:
                        st.warning(err)
        else:
            st.info("Click 'Extract Memory' to analyze the chat history")
    
    st.divider()
    
    # Personality testing section
    st.subheader("💬 Test Personality Engine")
    
    query = st.text_input(
        "Your message:",
        value="I've been so stressed about work lately...",
        placeholder="Type a message to see how different personalities respond",
    )
    
    if st.button("🎭 Generate Personality Responses", type="primary", use_container_width=True):
        if "memory" not in st.session_state:
            st.warning("Please extract memory first!")
        else:
            memory = st.session_state.memory
            
            # Show before/after comparison
            st.markdown("### Response Comparison")
            
            with st.spinner("Generating responses with different personalities..."):
                try:
                    # Generate generic response (no memory)
                    generic = run_async(engine.generate_generic_response(query))
                    
                    # Generate personalized responses
                    responses = run_async(engine.generate_comparison(query, memory))
                    
                    # Display results
                    st.markdown("#### ❌ Without Memory (Generic)")
                    st.markdown(f"""
                    <div style="background-color: #f0f0f0; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    {generic}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("#### ✅ With Memory + Personality")
                    
                    cols = st.columns(3)
                    for i, (pid, resp) in enumerate(responses.items()):
                        with cols[i]:
                            profile = PROFILES[pid]
                            st.markdown(f"**{profile.name}**")
                            st.markdown(f"*{profile.description}*")
                            st.markdown(f"""
                            <div style="background-color: #e8f4f8; padding: 1rem; border-radius: 8px; border-left: 4px solid #1f77b4;">
                            {resp.response}
                            </div>
                            """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Generation failed: {e}")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem;">
    Built for GuppShupp • Founding AI Engineer Assignment • 
    <a href="https://github.com/dumko2001/guppshupp-personality-engine" target="_blank">GitHub</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
