# PDF Document Question-Answering Bot

PDF დოკუმენტების მიხედვით კითხვებზე პასუხის Telegram ბოტის პროტოტიპი.

## Implemented flow

Upload a PDF → extract embedded text with pdfplumber → split into overlapping character chunks → store document metadata in PostgreSQL and embeddings in Chroma → retrieve user-scoped chunks → filter relevance → ask Gemini or Groq for an answer.

Commands: `/start`, `/documents`, `/delete`; other text is treated as a question. Deletion checks document ownership before removing database/vector records. Search covers the user's documents; clicking a document does not set an active-document filter.

## Setup

```bash
git clone https://github.com/miqelius/miqelius-bot.git
cd miqelius-bot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

```bash
cp .env.example .env
# Configure token, database, LLM provider, key and an available model.
python main.py
```

Python 3.12 is used by the Dockerfile. A reachable PostgreSQL database and internet access for the embedding model/provider are needed.

| Variable | Purpose |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Required Telegram credential |
| `LLM_PROVIDER` | `gemini` or `groq` |
| `LLM_API_KEY`, `LLM_MODEL` | Provider credential and available model ID |
| `DATABASE_URL` | Async SQLAlchemy URL using `postgresql+asyncpg://` |
| `CHROMA_PERSIST_DIRECTORY` | Persistent vector directory; default `data/chroma` |
| `EMBEDDING_MODEL` | Default `all-MiniLM-L6-v2`; downloads model weights |
| `MAX_UPLOAD_SIZE_MB` | Default 20 |

Docker alternative: after resolving the dependency issues below, `docker compose up --build` starts PostgreSQL and the bot. Compose overrides `DATABASE_URL` to use its internal database. Persist both PostgreSQL and the Chroma directory.

## Known startup and accuracy gaps

- `requirements.txt` selects the PyTorch CPU index globally; unrelated packages may not resolve there. Dependency installation needs correction before a reproducible fresh install can be claimed.
- `app/services/llm_client.py` imports `google.genai`, while requirements declare `google-generativeai`; these are different SDKs. The Gemini dependency needs alignment. Select a model currently available in your own provider account.
- The active ingestion service uses text extraction only. OCR-related dependencies and a separate processor do not prove scanned PDFs work through the Telegram flow.
- Source labels call chunk indexes “Page”; they are not original PDF page numbers.
- SQL/vector writes are separate; failed ingestion can leave partial records. No end-to-end live-provider verification was performed.

## Manual acceptance flow

Upload a short text PDF, ask a question answered in it, inspect cited snippets, list and delete the document, then confirm it is unavailable to another Telegram user. `test_pipeline.py` is an existing pipeline script; inspect its settings before running it because it is not a proven offline test suite.

## Source map

`main.py`: startup. `app/bot/handlers.py`: Telegram flow. `app/services/document_service.py`: active ingestion. `app/storage/`: SQL/vector persistence. `app/services/chat_service.py`, `app/llm/answer_generator.py`: retrieval and answers.

## Verification scope

Documentation was checked against the default-branch source on 2026-11-08. Source inspection and Python syntax checks do not establish a working deployment. External services, credentials, and live data were not exercised.
