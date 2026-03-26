# copom-streamlit

[Streamlit](https://streamlit.io) web interface for the **COPOM RAG** system — ask questions in natural language about Minutes and Communications from Brazil's Monetary Policy Committee (Comitê de Política Monetária do Banco Central do Brasil), with LLM-generated answers and inline citations to the original documents.

Demo: [copom-rag.streamlit.app](https://copom-rag.streamlit.app)

---

## Features

- **Natural language Q&A** over COPOM minutes and communications
- **Filters by document type** (Minutes / Communications) and **date range**
- **Inline citations** `[1][2]` linked to the original source excerpts
- **Detailed references**: title, date, type, excerpt, and link to the PDF
- **Admin page** with document list, ingestion form, and database stats
- **Home page** with live metrics and system architecture overview

---

## Architecture

This project is the interface layer of the COPOM RAG ecosystem:

```
Banco Central (PDFs)
        │
        ▼
copom-vector-pipeline   ← ingestion, chunking, embeddings
        │
        ▼
PostgreSQL + pgvector   ← vector storage (Neon)
        │
        ▼
copom-rag-api           ← semantic search + generation via Gemini (Render)
        │
        ▼
copom-streamlit         ← web interface (Streamlit Cloud)  ← you are here
```

---

## Pages

### Home
- Live metrics: total documents, minutes, communications, and date range covered
- RAG pipeline description in 3 steps
- Tech stack details and architecture diagram

### Questions
- Question input with sidebar filters (document type, start/end date)
- Markdown answer with numbered citations
- Reference list with links to the original PDFs
- Metadata: processing time and number of chunks used

### Admin
- **Documents**: table of all indexed documents with links to their PDFs
- **Ingest**: form to trigger ingestion locally with real-time log streaming
- **Database**: stats (total, date range, distribution by type)

---

## Stack

| Component | Technology |
|-----------|-----------|
| Interface | Streamlit >= 1.35 |
| HTTP client | httpx >= 0.27 |
| Configuration | python-dotenv |
| Data | pandas |
| Python | >= 3.11 |

---

## Running locally

### Prerequisites

- Python 3.11+
- [`copom-rag-api`](https://github.com/mateusfg7/copom-rag-api) running (local or remote)

### Setup

```bash
git clone https://github.com/mateusfg7/copom-streamlit.git
cd copom-streamlit

pip install -r requirements.txt

cp .env.example .env
# edit .env with the API URL
```

### Environment variables (`.env`)

```env
COPOM_API_URL=http://localhost:8001          # copom-rag-api base URL
COPOM_API_KEY=                               # API key (leave empty to disable auth)
COPOM_PIPELINE_DIR=../copom-vector-pipeline  # path to the pipeline (local ingestion)
```

### Run

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

---

## Deployment (Streamlit Cloud)

The app auto-deploys on [Streamlit Community Cloud](https://streamlit.io/cloud) on every push to `main`.

Configure secrets in the Streamlit Cloud dashboard:

```toml
COPOM_API_URL = "https://copom-rag-api.onrender.com"
COPOM_API_KEY = ""
```

> Streamlit Cloud reads secrets in TOML format, not `.env`.

See [DEPLOYMENT.md](DEPLOYMENT.md) for the full guide.

---

## Related projects

- [copom-rag-api](https://github.com/mateusfg7/copom-rag-api) — RAG API with FastAPI + Gemini + pgvector
- [copom-vector-pipeline](https://github.com/mateusfg7/copom-vector-pipeline) — COPOM PDF ingestion pipeline (part of this ecosystem)

> The **Admin** page can trigger `copom-vector-pipeline` locally via subprocess with real-time log streaming. In production, the pipeline must be run manually in a local environment with access to the Neon database.
