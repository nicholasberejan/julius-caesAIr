# julius-caesAIr

A backend-first MVP for a retrieval-augmented chatbot that answers in the voice of Julius Caesar, grounded in Caesar's writings.

This first pass focuses on:

- Flask API scaffold
- PDF ingestion and chunking
- Embeddings + FAISS indexing
- Retrieval
- A heuristic "could Caesar plausibly answer this?" classifier
- A basic chat pipeline with graceful fallback behavior

The frontend, persistent sessions, LangGraph orchestration, and LangSmith evaluation hooks can layer on top of this structure without a rewrite.

## Initial Project Tree

```text
julius-caesAIr/
├── README.md
├── requirements.txt
├── .env.example
├── data/
│   ├── raw/
│   │   └── .gitkeep
│   └── indexes/
│       └── .gitkeep
├── scripts/
│   └── ingest_corpus.py
└── backend/
    ├── __init__.py
    ├── app.py
    ├── config.py
    ├── api/
    │   ├── __init__.py
    │   └── chat.py
    ├── services/
    │   ├── __init__.py
    │   └── chat_service.py
    └── rag/
        ├── __init__.py
        ├── classifier.py
        ├── chunking.py
        ├── embeddings.py
        ├── graph.py
        ├── ingest.py
        ├── prompts.py
        ├── retriever.py
        └── types.py
```

## Setup

1. Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Copy the environment template.

```bash
cp .env.example .env
```

4. Add your source PDF(s) to `data/raw/`.

Suggested example:

- `data/raw/caesar_collected_works.pdf`

5. If you want real embeddings and LLM answers, set `OPENAI_API_KEY` in `.env`.

Without an API key:

- the Flask app still runs
- the classifier still works
- ingestion will fail if embeddings are requested
- chat will return a retrieval-based fallback message if an index already exists

## Local Run Order

Run the project in this order:

1. Install dependencies and configure `.env`
2. Put PDF files in `data/raw/`
3. Build the FAISS index:

```bash
python scripts/ingest_corpus.py
```

Optional throttling/limits for ingestion:

```bash
python scripts/ingest_corpus.py \
  --batch-size 32 \
  --sleep-seconds 0.5 \
  --max-pages-per-pdf 50 \
  --max-chunks 500
```

4. Start the Flask API:

```bash
python -m backend.app
```

5. Test the API:

```bash
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What does Caesar say about the Helvetii?"}'
```

## Notes On MVP Decisions

- The classifier is intentionally heuristic for now so we can move quickly and keep the structure easy to replace with a model-based guardrail later.
- The current chat pipeline lives in `backend/rag/graph.py` as a lightweight stand-in for a future LangGraph implementation.
- Retrieval uses FAISS locally for MVP speed and simplicity.
- The app keeps interfaces modular so we can later add:
  - LangGraph nodes/edges
  - LangSmith tracing
  - persistent chat sessions
  - richer citation rendering
  - production vector stores

## Environment Variables

See `.env.example` for defaults. Important values:

- `OPENAI_API_KEY`: required for OpenAI embeddings and generation
- `OPENAI_CHAT_MODEL`: default chat model
- `OPENAI_EMBEDDING_MODEL`: default embedding model
- `EMBEDDING_COST_PER_1M_TOKENS`: used for dry-run cost estimates
- `VECTOR_INDEX_DIR`: location of the FAISS index
- `SOURCE_DOCS_DIR`: location of raw PDF documents
- `INGEST_BATCH_SIZE`: embedding batch size for ingestion
- `INGEST_SLEEP_SECONDS`: pause between embedding batches
- `INGEST_MAX_PAGES_PER_PDF`: limit pages per PDF (0 = no limit)
- `INGEST_MAX_CHUNKS`: limit total chunks (0 = no limit)

## Next Recommended Steps

After this MVP is working end-to-end, the next build order should be:

1. Add session persistence
2. Convert the pipeline into a real LangGraph graph
3. Add LangSmith tracing/evaluation hooks
4. Build the Next.js frontend and session sidebar
5. Add stronger source citation formatting
