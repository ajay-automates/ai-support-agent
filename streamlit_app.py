"""
AI Support Agent — Streamlit Chat Interface
Upload your business documents and get an AI-powered support chatbot.
"""

import os
import sys

# ============================================================
# CRITICAL: Set env vars BEFORE any LangChain imports
# LangChain reads these at import time
# ============================================================
# Try loading from Streamlit secrets first
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

# Force these regardless
os.environ["LANGCHAIN_TRACING_V2"] = os.environ.get("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_PROJECT"] = os.environ.get("LANGCHAIN_PROJECT", "ai-support-agent")
os.environ["LANGSMITH_TRACING"] = "true"

import streamlit as st
import tempfile

# Setup paths
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
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #888;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    .stChatMessage {
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR — Document Management
# ============================================================
with st.sidebar:
    st.markdown("## 📄 Knowledge Base")
    st.markdown("Upload your business documents to train the AI agent.")

    # Collection stats
    try:
        stats = get_collection_stats()
        doc_count = stats["document_count"]
        st.metric("Documents Indexed", doc_count)
    except Exception:
        doc_count = 0
        st.metric("Documents Indexed", 0)

    st.markdown("---")

    # Upload files
    st.markdown("### Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF, TXT, or MD files",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        help="Your documents will be chunked and indexed for AI search.",
    )

    if uploaded_files:
        if st.button("📥 Index Uploaded Files", type="primary", use_container_width=True):
            with st.spinner("Indexing documents..."):
                total_chunks = 0
                for uploaded_file in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    try:
                        chunks = ingest_file(tmp_path)
                        total_chunks += chunks
                        st.success(f"✅ {uploaded_file.name}: {chunks} chunks indexed")
                    except Exception as e:
                        st.error(f"❌ {uploaded_file.name}: {str(e)}")
                    finally:
                        os.unlink(tmp_path)
                st.success(f"🎉 Total: {total_chunks} chunks indexed!")
                st.rerun()

    st.markdown("---")

    # Paste text directly
    st.markdown("### Or Paste Text")
    pasted_text = st.text_area(
        "Paste your FAQ, policies, or documentation here:",
        height=150,
        placeholder="e.g., Our return policy allows returns within 30 days of purchase...",
    )

    if pasted_text:
        if st.button("📥 Index Pasted Text", use_container_width=True):
            with st.spinner("Indexing text..."):
                chunks = ingest_text(pasted_text, source="pasted_text")
                st.success(f"✅ {chunks} chunks indexed from pasted text!")
                st.rerun()

    st.markdown("---")

    if doc_count > 0:
        if st.button("🗑️ Clear Knowledge Base", use_container_width=True):
            clear_collection()
            st.success("Knowledge base cleared!")
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    prompt_version = st.selectbox(
        "Prompt Version",
        ["v2_cited", "v1_simple"],
        help="v2_cited gives detailed answers with source citations. v1_simple is more concise.",
    )

    # Debug: show tracing status
    tracing_status = os.environ.get("LANGCHAIN_TRACING_V2", "not set")
    api_key_set = "✅" if os.environ.get("LANGCHAIN_API_KEY") else "❌"
    st.caption(f"LangSmith: Tracing={tracing_status} | Key={api_key_set}")

    st.markdown("---")
    st.markdown(
        "Built by [Ajay Kumar Reddy](https://github.com/ajay-automates) "
        "| [GitHub](https://github.com/ajay-automates/ai-support-agent)"
    )

# ============================================================
# MAIN CHAT INTERFACE
# ============================================================
st.markdown('<p class="main-header">🤖 AI Support Agent</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload your docs → Get an AI that answers customer questions with citations</p>', unsafe_allow_html=True)

if doc_count == 0:
    st.info("👈 **Get started:** Upload documents or paste text in the sidebar to build your knowledge base.")
else:
    st.success(f"✅ Knowledge base ready with **{doc_count}** document chunks. Start chatting below!")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            sources_text = " | ".join([f"📄 {s}" for s in message["sources"]])
            st.caption(f"Sources: {sources_text}")
        if message.get("metrics"):
            m = message["metrics"]
            cols = st.columns(3)
            cols[0].caption(f"⏱️ {m.get('latency_ms', 0):.0f}ms")
            cols[1].caption(f"🔤 {m.get('input_tokens', 0) + m.get('output_tokens', 0)} tokens")
            cols[2].caption(f"💰 ${m.get('cost_usd', 0):.6f}")

if prompt := st.chat_input("Ask a question about the uploaded documents..."):
    if doc_count == 0:
        st.warning("Please upload documents first using the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base..."):
                result = safe_ask(
                    question=prompt,
                    chat_history=st.session_state.chat_history,
                    prompt_version=prompt_version,
                )

            st.markdown(result["answer"])

            if result.get("sources"):
                sources_text = " | ".join([f"📄 {s}" for s in result["sources"]])
                st.caption(f"Sources: {sources_text}")

            if not result.get("blocked"):
                cols = st.columns(3)
                cols[0].caption(f"⏱️ {result.get('latency_ms', 0):.0f}ms")
                cols[1].caption(f"🔤 {result.get('input_tokens', 0) + result.get('output_tokens', 0)} tokens")
                cols[2].caption(f"💰 ${result.get('cost_usd', 0):.6f}")

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result.get("sources", []),
            "metrics": result,
        })
        st.session_state.chat_history.append((prompt, result["answer"]))
