# Multimodal Document Intelligence Assistant

> RAG-powered chat system that understands **both text and visuals** (charts, tables, diagrams) inside PDF documents — built with LangChain, pgvector, and GPT-4o Vision.

---

## Results

| Metric | Value |
|--------|:---:|
| Answer accuracy (20-question eval set) | **100% (20/20)** |
| Supported chunk types | Text + Image (GPT-4o Vision) |
| Multi-document support | Yes — isolated sessions per file |
| Average latency per query | ~2.5s |
| Supported document types | PDF (reports, CVs, lecture slides) |

---

## Architecture

```
PDF input
    │
    ├─► Page-as-image (PyMuPDF) ──► GPT-4o Vision ──► Image description chunks
    │
    └─► Text extraction ──────────► Text splitter ──► Text chunks
                                                            │
                                                    OpenAI Embeddings
                                                    (text-embedding-3-small)
                                                            │
                                                       pgvector (PostgreSQL)
                                                            │
                                              LangChain Retriever + History-aware chain
                                                            │
                                                    GPT-4o (answer generation)
                                                            │
                                                  Streamlit chat UI
```

**Key design decision:** Each PDF page is rendered as an image *and* parsed as text. The retriever decides at query time which representation is more useful — text chunks for prose, image descriptions for charts, tables, and diagrams.

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Orchestration | LangChain 0.3 (LCEL) | Chains, retrievers, memory — production standard |
| Vision LLM | GPT-4o Vision | Understands charts, tables, diagrams |
| Embeddings | `text-embedding-3-small` (OpenAI) | Fast, cheap, high quality |
| Vector DB | PostgreSQL + pgvector | No extra infra — SQL you already know |
| PDF parsing | PyMuPDF (fitz) | Reliable page-to-image rendering |
| Chat memory | LangChain `RunnableWithMessageHistory` | Per-session conversation memory |
| UI | Streamlit | Fast to build, easy to demo |
| Infra | Docker Compose | One command to run everything |

---

## Project Structure

```
multimodal-doc-assistant/
│
├── app/
│   ├── main.py                  # Streamlit UI — upload PDF, chat, multi-doc support
│   ├── chat.py                  # LangChain LCEL chain + history-aware retriever
│   ├── ingestion/
│   │   ├── pdf_parser.py        # PyMuPDF: extract text + render pages as images
│   │   ├── image_describer.py   # GPT-4o Vision: describe each page image
│   │   └── chunker.py           # RecursiveCharacterTextSplitter + metadata tagging
│   ├── retrieval/
│   │   └── vectorstore.py       # pgvector setup + document ingestion
│   └── memory/
│       └── chat_history.py      # Chat history utilities
│
├── eval/
│   ├── questions.json           # 20 ground-truth Q&A pairs (factual, conceptual, visual)
│   └── evaluate.py              # Accuracy measurement by question type
│
├── docker/
│   ├── Dockerfile
│   └── init.sql                 # pgvector extension + schema
│
├── tests/
│   ├── test_parser.py
│   ├── test_vectorstore.py
│   ├── test_ingest.py
│   ├── test_ingest_slides.py
│   ├── test_multidoc.py
│   └── test_chat.py
│
├── sample_docs/                 # Example PDFs for demo
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites

- Docker + Docker Compose
- OpenAI API key (`platform.openai.com`)
- Python 3.11+

### 1. Clone and configure

```bash
git clone https://github.com/Ha-Khoa/multimodal-doc-assistant
cd multimodal-doc-assistant
cp .env.example .env
# Edit .env — add OPENAI_API_KEY and Postgres credentials
```

### 2. Start the database

```bash
docker compose up db -d
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app/main.py
```

Open `http://localhost:8501`, upload a PDF, and start chatting.

---

## How It Works

### Ingestion pipeline (one-time per document)

1. **PDF → pages**: PyMuPDF renders every page as a 150 DPI PNG image
2. **Vision description**: Each page image is sent to GPT-4o Vision with a detailed prompt asking it to transcribe text, describe charts, tables, and diagrams
3. **Text extraction**: Standard text layer is also extracted from the same page
4. **Chunking**: Text chunks use `RecursiveCharacterTextSplitter` (1000 chars, 150 overlap); lecture slides use smaller chunks (400 chars)
5. **Metadata tagging**: Every chunk stores `{source_file, page_number, chunk_type: "text"|"image"}`
6. **Embedding + storage**: `text-embedding-3-small` → pgvector with HNSW index

### Query pipeline

1. User sends a question
2. History-aware retriever rewrites follow-up questions as standalone queries
3. LangChain retriever fetches top-5 most relevant chunks (mixed text + image)
4. GPT-4o generates an answer citing `[filename, page X, chunk_type]`
5. Conversation stored per-session for multi-turn memory

---

## Evaluation

Run the built-in evaluation against the 20-question test set:

```bash
# Ingest sample documents first
python3 tests/test_ingest.py
python3 tests/test_ingest_slides.py

# Run evaluation
python3 eval/evaluate.py
```

Output:
```
Running 20 questions...
[PASS] Q1: What is Khoa's GPA?
[PASS] Q2: What internship did Khoa complete?
...
[PASS] Q20: According to the slide, what should you learn to become a better programmer?
──────────────────────────────────────────────────
Accuracy: 20/20 = 100.0%
```

The evaluation covers 3 question types: **factual** (specific data from text), **conceptual** (understanding of content), and **visual** (information from charts, tables, and diagrams only visible through GPT-4o Vision).

---

## Environment Variables

```bash
# .env.example
OPENAI_API_KEY=sk-...

POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=docassistant
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

---

## Roadmap

- [x] Docker + PostgreSQL + pgvector setup
- [x] PDF text extraction (PyMuPDF)
- [x] GPT-4o Vision integration for image understanding
- [x] Full ingestion pipeline (text + image chunks)
- [x] LangChain conversational chain with memory
- [x] Multi-document support with session isolation
- [x] Evaluation framework (20 questions, 3 types)
- [x] Streamlit UI with multi-file chat

---

## License

MIT
