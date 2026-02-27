<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=8,12,20&height=170&section=header&text=AI%20Support%20Agent&fontSize=48&fontAlignY=35&animation=twinkling&fontColor=ffffff&desc=RAG%20Chatbot%20with%20LangSmith%20Observability%20%7C%20LLMOps&descAlignY=55&descSize=18" width="100%" />

[![Live Demo](https://img.shields.io/badge/Live-Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://ai-agent-support.streamlit.app)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](.)
[![LangSmith](https://img.shields.io/badge/LangSmith-Tracing-FF8C00?style=for-the-badge)](.)
[![Claude API](https://img.shields.io/badge/Claude-Sonnet-8B5CF6?style=for-the-badge&logo=anthropic&logoColor=white)](.)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-FF6B6B?style=for-the-badge)](.)
[![Streamlit](https://img.shields.io/badge/Streamlit-Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](.)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Upload your docs. Get an AI-powered customer support chatbot in minutes. Full LLMOps pipeline.**

[Live Demo](https://ai-agent-support.streamlit.app) · [Architecture](#architecture) · [LLMOps Components](#llmops-components) · [Quick Start](#quick-start)

</div>

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

export ANTHROPIC_API_KEY="your-key"
export LANGSMITH_API_KEY="your-key"
export LANGSMITH_TRACING=true
export LANGSMITH_PROJECT=ai-support-agent

streamlit run streamlit_app.py
```

---

## LangSmith Observability

Every request is automatically traced in LangSmith:

| Metric | Details |
|--------|---------|
| **Full execution trace** | Document retrieval → LLM call → response |
| **Latency per step** | Where time is spent in the pipeline |
| **Token usage** | Input and output tokens per request |
| **Cost tracking** | USD cost per request |
| **Guardrail triggers** | Blocked requests and reasons |
| **Retrieval quality** | Which documents were retrieved and why |

View your traces at [smith.langchain.com](https://smith.langchain.com)

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-format upload** | PDF, TXT, MD files |
| **Paste text directly** | FAQ, policies, documentation |
| **Chat interface** | Conversational with history |
| **Source citations** | Every answer cites its source document |
| **Guardrails** | Blocks prompt injection and harmful requests |
| **Per-message metrics** | Latency, tokens, cost shown inline |
| **Prompt versioning** | Switch between v1 (simple) and v2 (detailed) |
| **LangSmith tracing** | Full observability on every request |

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

## Tech Stack

`LangChain` `LangSmith` `ChromaDB` `Anthropic Claude` `Streamlit` `HuggingFace Embeddings` `RAG` `Python` `Prompt Engineering` `LLMOps`

---

## Related Projects

| Project | Description |
|---------|-------------|
| [Advanced Resume Analyzer (QLoRA)](https://github.com/ajay-automates/advanced-resume-analyzer-qlora) | Fine-tuned Gemma 3 4B with QLoRA |
| [AI Code Review Bot](https://github.com/ajay-automates/ai-code-review-bot) | Automated PR reviews via Claude + GitHub Actions |
| [AI Image Classifier API](https://github.com/ajay-automates/ai-image-classifier-api) | Self-hosted CLIP inference — $0/request |

---

<div align="center">

**Built by [Ajay Kumar Reddy Nelavetla](https://github.com/ajay-automates)** · February 2026

*Production RAG with full observability. Not a tutorial — a deployed system.*

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=8,12,20&height=100&section=footer" width="100%" />

</div>
