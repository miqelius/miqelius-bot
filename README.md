# Telegram PDF Q&A Bot (RAG Prototype)

A Python Telegram bot project intended to answer questions about PDF documents using retrieval-augmented generation (RAG).

> **Status: experimental / not verified production-ready.** The README describes the intended architecture and code dependencies. End-to-end PDF upload, indexing, retrieval and answer generation have **not** been independently verified here.

## What the repository contains

- Telegram bot entry point using **aiogram 3** (`main.py`).
- Async SQLAlchemy database initialization.
- Configuration for an LLM provider, embeddings, Chroma persistence and PDF limits (`app/core/config.py`).
- Dependencies for PDF extraction, OCR, vector search and LLM integration (`requirements.txt`).

## Stack

Python · aiogram · SQLAlchemy / asyncpg · ChromaDB · sentence-transformers · pdfplumber · pytesseract · Gemini / Groq libraries

## Local setup (developer preview)

Use **Python 3.11** as a starting point; compatibility with other versions and a complete installation have not been validated.

```bash
git clone https://github.com/miqelius/miqelius-bot.git
cd miqelius-bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You will need PostgreSQL, external credentials and possibly OCR system packages. Configure environment variables in a local **.env** file, never in Git. The settings module currently expects:

```dotenv
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
LLM_API_KEY=<your-provider-api-key>
LLM_PROVIDER=gemini
DATABASE_URL=<your-async-sqlalchemy-postgresql-url>
```

Then, **after configuration and dependency review**, try:

```bash
python main.py
```

Do **not** publish real tokens, API keys, DB passwords or users' documents.

## Known limitations / next engineering tasks

- Validate the complete workflow: upload → extract → chunk → index → retrieve → grounded answer.
- Add isolated tests for document parsing, retrieval and bot handlers.
- Verify supported Python and third-party dependency versions before deployment.
- Add file validation, resource limits, document retention and access-control checks.
- Document system-level OCR requirements and deployment configuration.

This repository is presented as a **learning / work-in-progress project**, not a deployed SaaS or a security-reviewed production bot.
