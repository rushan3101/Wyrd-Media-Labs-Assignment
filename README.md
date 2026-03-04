# Wyrd Media Labs AI/ML Internship Assignment

This repository contains solutions for two AI system design problems.

## Problem 1 — Local RAG on Real Documents

Build a **fully local Retrieval-Augmented Generation system** that can answer questions from Wyrd's company wiki.

Key requirements:
- Runs locally
- No per-query cost
- Uses embeddings + vector database
- Uses an open-source LLM

Solution highlights:
- Custom markdown parser for Notion export
- Structured document extraction
- Semantic chunking
- Local embeddings with Ollama
- Vector search with ChromaDB
- Local LLM responses with Llama3

📁 See: `Problem-1-Local-RAG/`

---

## Problem 2 — The Useless Support Inbox

Design a system that automatically answers support emails using existing documentation.

Key idea:
- Use Retrieval-Augmented Generation (RAG)
- Retrieve documentation
- Generate automated responses
- Escalate uncertain cases to human agents

📁 See: `Problem-2-Support-Inbox-Solution/`

---

## Tech Stack

- Python
- LangChain
- Ollama
- ChromaDB
- Streamlit
- Local LLMs

---

## Author

Mohd Rushan
