"""
AI Support Agent — RAG Pipeline with LangSmith Observability
Uses LangChain + ChromaDB + Claude for answering questions from documents.
Every call is traced through LangSmith for full observability.
"""

import os
import time
from typing import Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable
from app.ingest import get_vectorstore

# ============================================================
# LANGSMITH CONFIGURATION
# ============================================================
os.environ.setdefault("LANGSMITH_TRACING", "true")
os.environ.setdefault("LANGSMITH_PROJECT", "ai-support-agent")

# ============================================================
# MODEL CONFIGURATION
# ============================================================
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1024
TEMPERATURE = 0.1  # Low temperature for factual support answers
RETRIEVAL_K = 4  # Number of document chunks to retrieve


def load_prompt(version: str = "v2_cited") -> str:
    """Load a versioned prompt template."""
    prompt_dir = os.path.join(os.path.dirname(__file__), "prompts")
    prompt_file = os.path.join(prompt_dir, f"{version}.txt")

    if os.path.exists(prompt_file):
        with open(prompt_file, "r") as f:
            return f.read()

    # Default fallback
    return """You are a helpful customer support agent. Answer questions using ONLY the provided context. If the answer is not in the context, say "I don't have information about that in my knowledge base." Always cite which document your answer comes from."""


def get_llm():
    """Initialize Claude LLM."""
    return ChatAnthropic(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )


def get_retriever(collection_name: str = "default"):
    """Get a retriever from the vectorstore."""
    vectorstore = get_vectorstore(collection_name)
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": RETRIEVAL_K},
    )


@traceable(name="support_agent_query", run_type="chain")
def ask_question(
    question: str,
    collection_name: str = "default",
    chat_history: Optional[list] = None,
    prompt_version: str = "v2_cited",
) -> dict:
    """
    Ask a question to the support agent.
    """
    start_time = time.time()

    if chat_history is None:
        chat_history = []

    # Load components
    llm = get_llm()
    retriever = get_retriever(collection_name)
    system_prompt = load_prompt(prompt_version)

    # Retrieve relevant documents
    retrieved_docs = retriever.invoke(question)

    # Build context from retrieved documents
    context_parts = []
    sources = []
    for i, doc in enumerate(retrieved_docs):
        source = doc.metadata.get("source", f"Document {i+1}")
        context_parts.append(f"[Source: {source}]\n{doc.page_content}")
        sources.append(source)

    context = "\n\n---\n\n".join(context_parts)

    # Build the prompt
    messages = [
        ("system", system_prompt),
        ("human", """Context from knowledge base:
{context}

Chat history:
{history}

Customer question: {question}

Answer the question using ONLY the context above. If the context doesn't contain the answer, say "I don't have information about that in my knowledge base. Please contact our support team for further assistance." Always mention which source document your answer comes from."""),
    ]

    prompt = ChatPromptTemplate.from_messages(messages)

    # Format chat history
    history_text = ""
    for h_q, h_a in chat_history[-3:]:
        history_text += f"Customer: {h_q}\nAgent: {h_a}\n"

    # Call LLM
    chain = prompt | llm
    response = chain.invoke({
        "context": context,
        "history": history_text,
        "question": question,
    })

    latency_ms = (time.time() - start_time) * 1000
    answer = response.content

    # Calculate cost (Claude Sonnet pricing)
    input_tokens = response.usage_metadata.get("input_tokens", 0) if hasattr(response, "usage_metadata") and response.usage_metadata else 0
    output_tokens = response.usage_metadata.get("output_tokens", 0) if hasattr(response, "usage_metadata") and response.usage_metadata else 0
    cost = (input_tokens / 1000 * 0.003) + (output_tokens / 1000 * 0.015)

    result = {
        "answer": answer,
        "sources": list(set(sources)),
        "retrieved_chunks": len(retrieved_docs),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost, 6),
        "latency_ms": round(latency_ms, 1),
        "prompt_version": prompt_version,
        "collection": collection_name,
    }

    return result


@traceable(name="guardrail_check", run_type="tool")
def check_guardrails(question: str) -> dict:
    """
    Check if a question should be answered or blocked.
    """
    question_lower = question.lower().strip()

    if not question_lower or len(question_lower) < 3:
        return {"allowed": False, "reason": "Question too short"}

    injection_patterns = [
        "ignore previous", "ignore above", "forget your instructions",
        "you are now", "act as", "pretend you are",
        "system prompt", "reveal your prompt", "show me your instructions",
    ]
    for pattern in injection_patterns:
        if pattern in question_lower:
            return {"allowed": False, "reason": "Potential prompt injection detected"}

    harmful_patterns = [
        "how to hack", "how to steal", "illegal",
        "exploit vulnerability", "bypass security",
    ]
    for pattern in harmful_patterns:
        if pattern in question_lower:
            return {"allowed": False, "reason": "Harmful content request blocked"}

    return {"allowed": True, "reason": "OK"}


@traceable(name="safe_ask", run_type="chain")
def safe_ask(
    question: str,
    collection_name: str = "default",
    chat_history: Optional[list] = None,
    prompt_version: str = "v2_cited",
) -> dict:
    """
    Ask a question with guardrail checks.
    This is the main entry point for the chat interface.
    """
    guard_result = check_guardrails(question)
    if not guard_result["allowed"]:
        return {
            "answer": f"I'm sorry, I can't process that request. ({guard_result['reason']})",
            "sources": [],
            "blocked": True,
            "block_reason": guard_result["reason"],
            "cost_usd": 0,
            "latency_ms": 0,
        }

    result = ask_question(
        question=question,
        collection_name=collection_name,
        chat_history=chat_history,
        prompt_version=prompt_version,
    )
    result["blocked"] = False
    return result
