# 🤖 AI Support Agent Platform

**Upload your docs. Get an AI-powered customer support chatbot in minutes.**

Built with LangChain, LangSmith, ChromaDB, and Claude API. Full LLMOps: tracing, evaluation, monitoring, and guardrails.

**Author:** Ajay Kumar Reddy Nelavetla | February 2026

---

## Live Demo

🔗 **[Try it live on Streamlit Cloud](https://ai-support-agent.streamlit.app)** *(link active after deployment)*

---

## What This Does

1. **Upload** your business documents (PDF, TXT, FAQ pages)
2. **AI indexes** everything into a vector database (ChromaDB)
3. **Customers ask questions** through a chat interface
4. **AI answers with citations** from YOUR documents only
5. **LangSmith tracks everything** — every question, every answer, latency, cost

The agent ONLY answers from your documents. If it doesn't know, it says so. No hallucination.

---

## Architecture

```
Customer asks question
        │
        ▼
  Streamlit Chat UI
        │
        ▼
  Guardrails Check (block injections, harmful requests)
        │
        ▼
  LangChain RAG Pipeline
        │
        ├──→ Embed question (HuggingFace all-MiniLM-L6-v2)
        ├──→ Search ChromaDB for relevant document chunks
        ├──→ Send context + question to Claude API
        └──→ Generate answer with source citations
        │
        ▼
  LangSmith traces entire pipeline
  (latency, tokens, cost, retrieval quality)
        │
        ▼
  Answer displayed with sources + metrics
```

---

## LLMOps Components

| Component | Implementation |
|-----------|---------------|
| **RAG Pipeline** | LangChain + ChromaDB + Claude |
| **Embeddings** | HuggingFace all-MiniLM-L6-v2 (free, local) |
| **Vector Store** | ChromaDB (persistent) |
| **LLM** | Anthropic Claude Sonnet |
| **Observability** | LangSmith (tracing, monitoring, evaluation) |
| **Prompt Management** | Versioned templates (v1_simple, v2_cited) |
| **Guardrails** | Prompt injection detection, harmful content blocking |
| **Frontend** | Streamlit with chat interface |
| **Cost Tracking** | Per-request token counting and USD calculation |

---

## Project Structure

```
ai-support-agent/
├── app/
│   ├── __init__.py
│   ├── agent.py              # RAG agent with LangSmith tracing
│   ├── ingest.py             # Document ingestion pipeline
│   └── prompts/
│       ├── v1_simple.txt     # Basic prompt
│       └── v2_cited.txt      # Detailed prompt with citations
├── vectorstore/              # ChromaDB storage (gitignored)
├── .streamlit/
│   └── secrets.toml.example  # Secrets template
├── streamlit_app.py          # Main chat interface
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Quick Start

### Deploy on Streamlit Cloud (Recommended)

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set secrets in Streamlit Cloud dashboard:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   LANGSMITH_API_KEY = "lsv2_pt_..."
   ```
5. Deploy — your app is live!

### Run Locally

```bash
git clone https://github.com/ajay-automates/ai-support-agent.git
cd ai-support-agent
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-key"
export LANGSMITH_API_KEY="your-key"
export LANGSMITH_TRACING=true
export LANGSMITH_PROJECT=ai-support-agent

# Run
streamlit run streamlit_app.py
```

---

## LangSmith Observability

Every request is automatically traced in LangSmith. You can see:

- **Full execution trace** — document retrieval → LLM call → response
- **Latency per step** — where time is spent
- **Token usage** — input and output tokens per request
- **Cost tracking** — USD cost per request
- **Guardrail triggers** — blocked requests and reasons
- **Retrieval quality** — which documents were retrieved

View your traces at [smith.langchain.com](https://smith.langchain.com)

---

## Features

- 📄 **Multi-format upload** — PDF, TXT, MD files
- 📋 **Paste text directly** — FAQ, policies, documentation
- 💬 **Chat interface** — conversational with history
- 📎 **Source citations** — every answer cites its source document
- 🛡️ **Guardrails** — blocks prompt injection and harmful requests
- 📊 **Per-message metrics** — latency, tokens, cost shown inline
- 🔄 **Prompt versioning** — switch between v1 (simple) and v2 (detailed)
- 🔍 **LangSmith tracing** — full observability on every request

---

## Cost

| Component | Cost |
|-----------|------|
| Streamlit Cloud hosting | Free |
| ChromaDB | Free (runs in app) |
| HuggingFace embeddings | Free (runs locally) |
| Claude API | ~$0.003-0.01 per question |
| LangSmith | Free tier (5K traces/month) |
| **Total for light usage** | **~$1-5/month** |

---

## For Businesses

Want an AI support agent for your business? I'll set it up for you.

1. Send me your FAQ / documentation / policies
2. I deploy a custom agent trained on YOUR data
3. Your customers get instant AI-powered answers 24/7

**Contact:** [LinkedIn](https://linkedin.com/in/ajaykumarreddynelavetla) | [GitHub](https://github.com/ajay-automates)

---

## Technologies

`LangChain` `LangSmith` `ChromaDB` `Anthropic Claude` `Streamlit` `HuggingFace Embeddings` `RAG` `Python` `Prompt Engineering` `LLMOps`

---

## Related Projects

- [Resume Analyzer (QLoRA Fine-Tuning)](https://github.com/ajay-automates/advanced-resume-analyzer-qlora)
- [AI Code Review Bot](https://github.com/ajay-automates/ai-code-review-bot)

---

*Built with 🔥 in February 2026*
