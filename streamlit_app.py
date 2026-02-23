"""
AI Support Agent — Premium Edition
A distinctive, production-grade AI support chatbot interface.
"""

import os
import sys

# ============================================================
# Set env vars BEFORE any LangChain imports
# ============================================================
try:
    import streamlit as st
    for key in ["LANGSMITH_API_KEY", "LANGCHAIN_API_KEY", "ANTHROPIC_API_KEY", "LANGCHAIN_TRACING_V2", "LANGCHAIN_PROJECT"]:
        if key in st.secrets:
            os.environ[key] = st.secrets[key]
    if "LANGSMITH_API_KEY" in st.secrets and "LANGCHAIN_API_KEY" not in os.environ:
        os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGSMITH_API_KEY"]
except Exception:
    pass

os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_PROJECT", "ai-support-agent")
os.environ.setdefault("LANGSMITH_TRACING", "true")

import streamlit as st
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
from app.ingest import ingest_text, ingest_file, get_collection_stats, clear_collection
from app.agent import safe_ask

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Support Agent AI",
    page_icon="\u26a1",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# PREMIUM DESIGN SYSTEM
# Aesthetic: Editorial luxury meets tech
# Font: DM Sans (display) + JetBrains Mono (metrics)
# Palette: Deep ink (#0a0a0b), electric indigo (#5b5bd6)
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&family=Playfair+Display:wght@700;800&display=swap');

    #MainMenu, footer, header {visibility: hidden;}
    .main .block-container { padding: 2rem 1rem 4rem 1rem; max-width: 880px; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    [data-testid="stSidebar"] { background: #0a0a0b; border-right: 1px solid rgba(255,255,255,0.06); }
    [data-testid="stSidebar"] * { color: #a0a0a8 !important; font-family: 'DM Sans', sans-serif !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 { color: #ffffff !important; letter-spacing: -0.3px; }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.06) !important; margin: 1.2rem 0 !important; }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] { color: #5b5bd6 !important; font-family: 'JetBrains Mono', monospace !important; font-size: 2.8rem !important; font-weight: 500 !important; }
    [data-testid="stSidebar"] .stMetric label { color: #5a5a65 !important; font-size: 0.7rem !important; text-transform: uppercase !important; letter-spacing: 1.5px !important; }
    [data-testid="stSidebar"] .stButton > button { background: #5b5bd6 !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; padding: 11px 20px !important; font-weight: 600 !important; font-size: 0.85rem !important; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important; box-shadow: 0 1px 3px rgba(91, 91, 214, 0.3), 0 6px 16px rgba(91, 91, 214, 0.15) !important; }
    [data-testid="stSidebar"] .stButton > button:hover { background: #4c4cbf !important; box-shadow: 0 2px 8px rgba(91, 91, 214, 0.4), 0 12px 28px rgba(91, 91, 214, 0.2) !important; transform: translateY(-1px) !important; }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] { border: 1.5px dashed rgba(255,255,255,0.08) !important; border-radius: 12px !important; background: rgba(255,255,255,0.02) !important; }
    [data-testid="stSidebar"] textarea { background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 10px !important; font-size: 0.82rem !important; }
    [data-testid="stSidebar"] textarea:focus { border-color: #5b5bd6 !important; box-shadow: 0 0 0 2px rgba(91, 91, 214, 0.15) !important; }

    .hero { position: relative; background: #0a0a0b; border-radius: 24px; padding: 48px 44px 44px; margin-bottom: 32px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06); }
    .hero::before { content: ''; position: absolute; top: -60%; right: -20%; width: 500px; height: 500px; background: radial-gradient(circle, rgba(91, 91, 214, 0.15) 0%, transparent 70%); pointer-events: none; }
    .hero::after { content: ''; position: absolute; bottom: -40%; left: -10%; width: 350px; height: 350px; background: radial-gradient(circle, rgba(214, 91, 161, 0.08) 0%, transparent 70%); pointer-events: none; }
    .hero-eyebrow { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 3px; color: #5b5bd6; margin-bottom: 16px; position: relative; }
    .hero-title { font-family: 'Playfair Display', serif; font-size: 3.2rem; font-weight: 800; color: #ffffff; line-height: 1.1; margin: 0 0 14px 0; letter-spacing: -1.5px; position: relative; }
    .hero-desc { font-family: 'DM Sans', sans-serif; font-size: 1.05rem; color: #6b6b76; line-height: 1.6; max-width: 520px; margin: 0; position: relative; }
    .hero-status { display: inline-flex; align-items: center; gap: 8px; margin-top: 24px; padding: 8px 18px; border-radius: 100px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; letter-spacing: 0.5px; position: relative; }
    .hero-status.ready { background: rgba(52, 199, 89, 0.1); color: #34c759; border: 1px solid rgba(52, 199, 89, 0.2); }
    .hero-status.empty { background: rgba(255, 179, 64, 0.1); color: #ffb340; border: 1px solid rgba(255, 179, 64, 0.15); }
    .hero-status .dot { width: 6px; height: 6px; border-radius: 50%; animation: pulse 2s infinite; }
    .hero-status.ready .dot { background: #34c759; }
    .hero-status.empty .dot { background: #ffb340; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

    [data-testid="stChatMessage"] { border-radius: 18px !important; padding: 18px 22px !important; margin-bottom: 14px !important; border: 1px solid rgba(0,0,0,0.04) !important; box-shadow: 0 1px 4px rgba(0,0,0,0.03) !important; }
    .src-pill { display: inline-flex; align-items: center; gap: 5px; background: #f0f0ff; border: 1px solid #d8d8f0; border-radius: 100px; padding: 5px 14px; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #5b5bd6; font-weight: 500; margin-right: 6px; margin-top: 10px; letter-spacing: 0.3px; }
    .m-strip { display: flex; gap: 24px; margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(0,0,0,0.04); }
    .m-item { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #9898a6; display: flex; align-items: center; gap: 5px; letter-spacing: 0.3px; }
    [data-testid="stChatInput"] textarea { font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important; border-radius: 14px !important; border: 1.5px solid #e0e0e6 !important; padding: 14px 18px !important; }
    [data-testid="stChatInput"] textarea:focus { border-color: #5b5bd6 !important; box-shadow: 0 0 0 3px rgba(91, 91, 214, 0.08) !important; }
    .stAlert { border-radius: 14px !important; }
    .app-footer { text-align: center; padding: 28px 0 8px; margin-top: 48px; border-top: 1px solid rgba(0,0,0,0.05); font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #b0b0ba; letter-spacing: 0.5px; }
    .app-footer a { color: #5b5bd6; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("#### \u26a1 AGENT CONSOLE")
    try:
        stats = get_collection_stats()
        doc_count = stats["document_count"]
    except Exception:
        doc_count = 0
    st.metric("INDEXED CHUNKS", doc_count)
    st.markdown("---")

    st.markdown("##### Upload Documents")
    uploaded_files = st.file_uploader("Drop PDF, TXT, or MD files", type=["pdf", "txt", "md"], accept_multiple_files=True, label_visibility="collapsed")
    if uploaded_files:
        if st.button("Index Files \u2192", type="primary", use_container_width=True):
            with st.spinner("Indexing..."):
                total_chunks = 0
                for uf in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uf.name)[1]) as tmp:
                        tmp.write(uf.getvalue())
                        tmp_path = tmp.name
                    try:
                        chunks = ingest_file(tmp_path)
                        total_chunks += chunks
                        st.success(f"\u2713 {uf.name}")
                    except Exception as e:
                        st.error(f"\u2717 {uf.name}: {e}")
                    finally:
                        os.unlink(tmp_path)
                st.success(f"{total_chunks} chunks indexed")
                st.rerun()

    st.markdown("---")
    st.markdown("##### Paste Content")
    pasted_text = st.text_area("paste", height=100, placeholder="Paste your FAQ, policies, product docs...", label_visibility="collapsed")
    if pasted_text:
        if st.button("Index Text \u2192", use_container_width=True):
            with st.spinner("Indexing..."):
                chunks = ingest_text(pasted_text, source="pasted_text")
                st.success(f"{chunks} chunks indexed")
                st.rerun()

    if doc_count > 0:
        st.markdown("---")
        if st.button("Clear Knowledge Base", use_container_width=True):
            clear_collection()
            st.rerun()

    st.markdown("---")
    st.markdown("##### Prompt Style")
    prompt_version = st.selectbox("prompt", ["v2_cited", "v1_simple"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("<div style='text-align:center;opacity:0.3;font-size:0.65rem;padding:8px 0;font-family:JetBrains Mono,monospace;'>BUILT BY AJAY KUMAR REDDY<br><a href='https://github.com/ajay-automates/ai-support-agent' style='color:#5b5bd6!important;'>GITHUB</a> \u00b7 CLAUDE + LANGSMITH</div>", unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
if doc_count == 0:
    status_html = '<div class="hero-status empty"><span class="dot"></span>AWAITING DOCUMENTS</div>'
else:
    status_html = f'<div class="hero-status ready"><span class="dot"></span>KNOWLEDGE BASE ACTIVE \u00b7 {doc_count} CHUNKS</div>'

st.markdown(f"""
<div class="hero">
    <div class="hero-eyebrow">AI-POWERED SUPPORT</div>
    <h1 class="hero-title">Support Agent</h1>
    <p class="hero-desc">Upload your business documents. Get an AI assistant that answers customer questions instantly \u2014 with source citations, guardrails, and full observability.</p>
    {status_html}
</div>
""", unsafe_allow_html=True)

if doc_count == 0:
    st.info("\ud83d\udc48 Upload documents or paste text in the sidebar to get started.")

# ============================================================
# CHAT
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            pills = "".join([f'<span class="src-pill">\ud83d\udcc4 {s}</span>' for s in message["sources"]])
            st.markdown(pills, unsafe_allow_html=True)
        if message.get("metrics") and not message["metrics"].get("blocked"):
            m = message["metrics"]
            st.markdown(f'<div class="m-strip"><span class="m-item">\u23f1 {m.get("latency_ms",0):.0f}ms</span><span class="m-item">\u25c6 {m.get("input_tokens",0)+m.get("output_tokens",0)} tok</span><span class="m-item">$ {m.get("cost_usd",0):.4f}</span></div>', unsafe_allow_html=True)

if prompt := st.chat_input("Ask a question about your documents..."):
    if doc_count == 0:
        st.warning("Upload documents first.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Searching..."):
                result = safe_ask(question=prompt, chat_history=st.session_state.chat_history, prompt_version=prompt_version)
            st.markdown(result["answer"])
            if result.get("sources"):
                pills = "".join([f'<span class="src-pill">\ud83d\udcc4 {s}</span>' for s in result["sources"]])
                st.markdown(pills, unsafe_allow_html=True)
            if not result.get("blocked"):
                st.markdown(f'<div class="m-strip"><span class="m-item">\u23f1 {result.get("latency_ms",0):.0f}ms</span><span class="m-item">\u25c6 {result.get("input_tokens",0)+result.get("output_tokens",0)} tok</span><span class="m-item">$ {result.get("cost_usd",0):.4f}</span></div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": result["answer"], "sources": result.get("sources", []), "metrics": result})
        st.session_state.chat_history.append((prompt, result["answer"]))

if len(st.session_state.messages) > 0:
    st.markdown('<div class="app-footer">POWERED BY <a href="https://github.com/ajay-automates/ai-support-agent">AI SUPPORT AGENT</a> \u00b7 LANGCHAIN \u00b7 CLAUDE \u00b7 LANGSMITH</div>', unsafe_allow_html=True)
