# Problem 1 — Local RAG on Wyrd Company Wiki

## Overview

The goal of this task was to build a **fully local Retrieval-Augmented Generation (RAG) system** that can answer questions about the Wyrd Media Labs company wiki.

The system should:

- Run completely **locally**
- Avoid **per-query API costs**
- Retrieve answers from the **company documentation**
- Generate responses using a **local LLM**

The final system processes exported documentation, converts it into structured knowledge, stores it in a vector database, and answers questions using retrieved context.

---

# System Architecture

The final pipeline looks like this:

```

Notion Wiki
↓
Export to Markdown
↓
Custom Markdown Parser
↓
Structured Sections (Page → Section → Subsection)
↓
Semantic Chunking
↓
Embeddings (mxbai-embed-large)
↓
Chroma Vector Database
↓
Retriever (k=15)
↓
Llama3 (Ollama)
↓
Generated Answer

```

---

# Data Extraction

The company wiki was initially provided as a **Notion link**.

### First Attempt

The first approach was:

- Export Notion pages as **HTML**
- Parse the HTML to extract headings and text

However this caused problems:

- Content was inside **expandable blocks**
- HTML structure was inconsistent
- Sections like **Mission, Vision, Chapters** were difficult to detect

### Final Approach

The wiki was duplicated and exported as **Markdown**, which preserved structure more reliably.

Markdown allowed extraction of:

```

Page Title
├── Section
│      └── Subsection
│              └── Content

```

---

# Custom Markdown Parser

A custom parser was created to convert markdown files into structured chunks.

The parser handles:

- Page titles
- Section headings
- Subsections
- Nested bullet structures
- Content blocks

Example extracted structure:

```

Title: The Core Stuff
Sub Page: Why Wyrd
Section: Mission
Content:
Making stuff wyrd enough to matter tomorrow.

```

---

# Chunking Strategy

Initially a simple **character-based splitter** was used:

```

chunk_size = 500
overlap = 100

```

However this caused problems because unrelated content sometimes appeared in the same chunk.

To improve retrieval quality, **semantic chunking** was introduced.

Semantic chunking groups sentences based on meaning rather than length.

This improved retrieval accuracy significantly.

---

# Embeddings

Two embedding models were tested.

### Initial Model

```

nomic-embed-text

```

This worked but retrieval accuracy was inconsistent.

### Final Model

```

mxbai-embed-large

```

Advantages:

- Better semantic understanding
- Improved retrieval quality
- Works locally with Ollama

---

# Vector Database

The vector database used in this system is:

```

ChromaDB

```

Reasons for choosing Chroma:

- Runs locally
- Simple Python integration
- Lightweight and easy to set up

All document chunks are embedded and stored in Chroma for retrieval.

---

# LLM for Answer Generation

The system uses **Ollama** to run a local LLM.

Model used:

```

llama3

```

The LLM receives:

- The user question
- Retrieved documentation chunks

It then generates an answer based on the retrieved context.

---

# Prompt Strategy

A structured prompt ensures the model answers only using retrieved information.

Example prompt:

```

You are answering questions about the Wyrd company wiki.

Use only the provided context to answer the question.
If the answer cannot be found in the context, say that it was not found.

Context:
{retrieved_documents}

Question:
{user_query}

Answer:

```

---

# Example Queries

## Query 1

**Question**

```

What is Wyrd's mission?

```

**Result**

![Mission Query](results/mission_query.png)

---

## Query 2

**Question**

```

What are the character profiles mentioned in "How We Speak"?

```

**Result**

![Character Profiles](results/character_profile_query.png)

---

## Query 3

**Question**

```

What happens in Chapter 1 of The Journey?

```

**Result**

![Chapter Query](results/chapter_query.png)

---

# Performance

Current retriever configuration:

```

k = 15

```

This improves answer accuracy but increases response time.

Average response time:

```

240–280 seconds

```

Possible reasons:

- Large embedding model
- Local inference
- Hardware limitations

Using a **better GPU** would significantly reduce latency.

---

# Limitations

The system works well but has some limitations:

- Slow responses due to local inference
- Retrieval depth increases response time
- Some answers require larger context windows

---

# Possible Improvements

Future improvements could include:

- Hybrid retrieval (BM25 + vector search)
- Faster embedding models
- Query caching
- GPU acceleration
- Better ranking of retrieved documents

---

# Technologies Used

- Python
- LangChain
- Ollama
- ChromaDB
- Streamlit
- Custom Markdown Parser


---

# Author

Mohd Rushan

