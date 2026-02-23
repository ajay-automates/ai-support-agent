"""
AI Support Agent — Premium Streamlit Chat Interface
Upload your business documents and get an AI-powered support chatbot.
"""

import os
import sys

# ============================================================
# CRITICAL: Set env vars BEFORE any LangChain imports
# ============================================================
try:
    import streamlit as st
    if "LANGSMITH_API_KEY" in st.secrets:
        os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGSMITH_API_KEY"]
        os.environ["LANGSMITH_API_KEY"] = st.secrets["LANGSMITH_API_KEY"]
    if "LANGCHAIN_API_KEY" in st.secrets:
        os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
    if "ANTHROPIC_API_KEY" in st.secrets:
        os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
    if "LANGCHAIN_TRACING_V2" in st.secrets:
        os.environ["LANGCHAIN_TRACING_V2"] = st.secrets["LANGCHAIN_TRACING_V2"]
    if "LANGCHAIN_PROJECT" in st.secrets:
        os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]
except Exception:
    pass

os.environ["LANGCHAIN_TRACING_V2"] = os.environ.get("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_PROJECT"] = os.environ.get("LANGCHAIN_PROJECT", "ai-support-agent")
os.environ["LANGSMITH_TRACING"] = "true"

import streamlit as st
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from app.ingest import ingest_text, ingest_file, get_collection_stats, clear_collection
from app.agent import safe_ask

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="AI Support Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# PREMIUM CSS
# ============================================================
st.markdown("""
<style>
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Dark premium sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stMetric label {
        color: #8892b0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #64ffda !important;
        font-size: 2.5rem !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.1) !important;
    }

    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        max-width: 900px;
    }

    /* Hero section */
    .hero-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        border-radius: 20px;
        padding: 40px 35px;
        margin-bottom: 30px;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: white;
        margin: 0;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        color: rgba(255,255,255,0.85);
        margin-top: 8px;
        margin-bottom: 0;
        font-weight: 400;
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 15px;
    }
    .status-ready {
        background: rgba(100, 255, 218, 0.2);
        color: #64ffda;
        border: 1px solid rgba(100, 255, 218, 0.3);
    }
    .status-empty {
        background: rgba(255, 193, 7, 0.15);
        color: #ffc107;
        border: 1px solid rgba(255, 193, 7, 0.3);
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.05);
    }

    /* Source tags */
    .source-pill {
        display: inline-block;
        background: linear-gradient(135deg, #e8f4fd, #e0f0ff);
        border: 1px solid #b3d9f7;
        border-radius: 50px;
        padding: 4px 14px;
        font-size: 0.78rem;
        color: #1565c0;
        font-weight: 500;
        margin-right: 6px;
        margin-top: 8px;
    }

    /* Metrics row */
    .metrics-row {
        display: flex;
        gap: 20px;
        margin-top: 10px;
        padding: 10px 0;
        border-top: 1px solid rgba(0,0,0,0.06);
    }
    .metric-item {
        font-size: 0.78rem;
        color: #888;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
        transform: translateY(-1px);
    }

    /* File uploader */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        border: 2px dashed rgba(255,255,255,0.15) !important;
        border-radius: 12px;
        padding: 10px;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        border-radius: 16px;
        border: 2px solid #667eea;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #764ba2;
        box-shadow: 0 0 0 3px rgba(118, 75, 162, 0.15);
    }

    /* Info/success boxes */
    .stAlert {
        border-radius: 12px;
    }

    /* Powered by footer */
    .powered-by {
        text-align: center;
        padding: 20px 0;
        color: #aaa;
        font-size: 0.8rem;
        margin-top: 40px;
        border-top: 1px solid rgba(0,0,0,0.06);
    }
    .powered-by a {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("# 🤖 AI Agent")
    st.markdown("##### Knowledge Base Manager")

    try:
        stats = get_collection_stats()
        doc_count = stats["document_count"]
    except Exception:
        doc_count = 0

    st.metric("Documents Indexed", doc_count)

    st.markdown("---")

    # Upload files
    st.markdown("#### 📄 Upload Documents")
    uploaded_files = st.file_uploader(
        "PDF, TXT, or MD files",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        help="Documents are chunked and indexed for AI-powered search.",
        label_visibility="collapsed",
    )

    if uploaded_files:
        if st.button("📥 Index Files", type="primary", use_container_width=True):
            with st.spinner("Indexing..."):
                total_chunks = 0
                for uploaded_file in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    try:
                        chunks = ingest_file(tmp_path)
                        total_chunks += chunks
                        st.success(f"✅ {uploaded_file.name}")
                    except Exception as e:
                        st.error(f"❌ {uploaded_file.name}: {str(e)}")
                    finally:
                        os.unlink(tmp_path)
                st.success(f"🎉 {total_chunks} chunks indexed!")
                st.rerun()

    st.markdown("---")

    # Paste text
    st.markdown("#### 📋 Paste Content")
    pasted_text = st.text_area(
        "Paste FAQ, policies, or docs here:",
        height=120,
        placeholder="Our return policy allows returns within 30 days...",
        label_visibility="collapsed",
    )

    if pasted_text:
        if st.button("📥 Index Text", use_container_width=True):
            with st.spinner("Indexing..."):
                chunks = ingest_text(pasted_text, source="pasted_text")
                st.success(f"✅ {chunks} chunks indexed!")
                st.rerun()

    st.markdown("---")

    if doc_count > 0:
        if st.button("🗑️ Clear Knowledge Base", use_container_width=True):
            clear_collection()
            st.success("Cleared!")
            st.rerun()

    st.markdown("---")
    st.markdown("#### ⚙️ Settings")
    prompt_version = st.selectbox(
        "Prompt Style",
        ["v2_cited", "v1_simple"],
        help="v2 = detailed with citations, v1 = concise",
    )

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; font-size:0.75rem; opacity:0.5; padding:10px 0;'>"
        "Built by <a href='https://github.com/ajay-automates' style='color:#64ffda !important;'>Ajay Kumar Reddy</a><br>"
        "<a href='https://github.com/ajay-automates/ai-support-agent' style='color:#64ffda !important;'>GitHub</a> · "
        "Powered by Claude + LangSmith"
        "</div>",
        unsafe_allow_html=True,
    )

# ============================================================
# MAIN CONTENT
# ============================================================

# Hero section
if doc_count == 0:
    status_html = '<span class="status-badge status-empty">⏳ No documents uploaded</span>'
else:
    status_html = f'<span class="status-badge status-ready">✅ {doc_count} chunks ready</span>'

st.markdown(f"""
<div class="hero-container">
    <p class="hero-title">AI Support Agent</p>
    <p class="hero-subtitle">Upload your business docs — get instant, accurate AI answers with source citations.</p>
    {status_html}
</div>
""", unsafe_allow_html=True)

if doc_count == 0:
    st.info("👈 **Get started:** Upload documents or paste text in the sidebar to build your knowledge base.")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            sources_html = "".join([f'<span class="source-pill">📄 {s}</span>' for s in message["sources"]])
            st.markdown(sources_html, unsafe_allow_html=True)
        if message.get("metrics") and not message["metrics"].get("blocked"):
            m = message["metrics"]
            st.markdown(f"""
            <div class="metrics-row">
                <span class="metric-item">⏱️ {m.get('latency_ms', 0):.0f}ms</span>
                <span class="metric-item">🔤 {m.get('input_tokens', 0) + m.get('output_tokens', 0)} tokens</span>
                <span class="metric-item">💰 ${m.get('cost_usd', 0):.4f}</span>
            </div>
            """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask anything about your uploaded documents..."):
    if doc_count == 0:
        st.warning("Please upload documents first using the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching knowledge base..."):
                result = safe_ask(
                    question=prompt,
                    chat_history=st.session_state.chat_history,
                    prompt_version=prompt_version,
                )

            st.markdown(result["answer"])

            if result.get("sources"):
                sources_html = "".join([f'<span class="source-pill">📄 {s}</span>' for s in result["sources"]])
                st.markdown(sources_html, unsafe_allow_html=True)

            if not result.get("blocked"):
                st.markdown(f"""
                <div class="metrics-row">
                    <span class="metric-item">⏱️ {result.get('latency_ms', 0):.0f}ms</span>
                    <span class="metric-item">🔤 {result.get('input_tokens', 0) + result.get('output_tokens', 0)} tokens</span>
                    <span class="metric-item">💰 ${result.get('cost_usd', 0):.4f}</span>
                </div>
                """, unsafe_allow_html=True)

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result.get("sources", []),
            "metrics": result,
        })
        st.session_state.chat_history.append((prompt, result["answer"]))

# Footer
if len(st.session_state.messages) > 0:
    st.markdown("""
    <div class="powered-by">
        Powered by <a href="https://github.com/ajay-automates/ai-support-agent">AI Support Agent</a> · 
        Built with LangChain + Claude + LangSmith
    </div>
    """, unsafe_allow_html=True)
