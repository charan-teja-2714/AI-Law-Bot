# AI Law Bot — FIR-RAG

An AI-powered Indian legal assistant that uses Retrieval-Augmented Generation (RAG) to answer legal questions, analyze FIRs and legal documents, and provide multilingual legal guidance based on IPC, BNS, CrPC, and other Indian laws.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Methodology & Complete Flow](#3-methodology--complete-flow)
   - 3.1 [User Query Flow (RAG-Based Q&A)](#31-user-query-flow-rag-based-qa)
   - 3.2 [Document Upload & Processing Flow](#32-document-upload--processing-flow)
   - 3.3 [Audio / Video Processing Flow](#33-audio--video-processing-flow)
   - 3.4 [Authentication Flow](#34-authentication-flow)
4. [Model Selection & Rationale](#4-model-selection--rationale)
5. [Performance Evaluation](#5-performance-evaluation)
6. [Key Technical Concepts](#6-key-technical-concepts)
7. [Database Schema](#7-database-schema)
8. [API Endpoints](#8-api-endpoints)
9. [Frontend Architecture](#9-frontend-architecture)
10. [Setup & Running](#10-setup--running)

---

## 1. Project Overview

FIR-RAG is a full-stack web application that acts as an AI legal assistant specialized in Indian law. It allows users to:

- Ask legal questions in English, Hindi, Telugu, or Tamil
- Upload PDF documents (FIRs, legal notices, complaints, petitions) for analysis
- Upload audio or video files — the system transcribes and indexes them automatically
- Get structured legal analysis with applicable IPC/BNS sections, consequences, and similar case laws
- Record voice questions and have them transcribed and answered

The system works both with and without uploaded documents. If no document is uploaded, it uses its trained knowledge of Indian law. If a document is uploaded, it retrieves relevant chunks from that document and grounds the answer in the actual content, preventing hallucination.

---

## 2. System Architecture

```
+----------------------------------------------------------------------+
|                        FRONTEND (React 18)                           |
|  ChatInterface | MessageList | DocumentList | LegalAnalysisView      |
|  MessageInput  | AudioRecorder | LanguageSelector | Toast            |
+-------------------------------+--------------------------------------+
                                |  HTTP / REST API
                                v
+----------------------------------------------------------------------+
|                     BACKEND (FastAPI + Python)                       |
|                                                                      |
|  +------------------+  +--------------------+  +----------------+   |
|  |   chat_service   |  | document_processor |  | speech_to_text |   |
|  |  (orchestrator)  |  |    (PDF / OCR)     |  |   (Whisper)    |   |
|  +--------+---------+  +---------+----------+  +-------+--------+   |
|           |                      |                      |           |
|  +--------v---------+  +---------v----------+  +-------v--------+   |
|  | translation_svc  |  |    faiss_store     |  | legal_predictor|   |
|  |  (multilingual)  |  |  (vector database) |  | (structured AI)|   |
|  +------------------+  +--------------------+  +----------------+   |
|                                                                      |
|  +------------------------------------------------------------------+|
|  |              auth_service + middleware (SQLite)                  ||
|  +------------------------------------------------------------------+|
+----------------------------------------------------------------------+
                                |
               +----------------+------------------+
               |                                   |
               v                                   v
+----------------------+             +---------------------------+
|   Groq API           |             |   Local Models (CPU)      |
|  llama-3.3-70b       |             |  all-mpnet-base-v2        |
|  (LLM inference)     |             |  (sentence embeddings)    |
+----------------------+             |  faster-whisper tiny      |
                                     |  (speech transcription)   |
                                     +---------------------------+
```

**Technology Stack**

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, CSS3 |
| Backend | FastAPI (Python 3.10+) |
| LLM | Llama 3.3 70B via Groq API |
| Embeddings | `all-mpnet-base-v2` (HuggingFace, runs locally) |
| Vector DB | FAISS (local, CPU, no cloud) |
| Speech-to-Text | `faster-whisper` tiny model (local, CPU) |
| PDF Parsing | PyPDF2 + Tesseract OCR |
| Database | SQLite |
| Translation | Groq LLM (llama-3.3-70b, temp=0.3) |

---

## 3. Methodology & Complete Flow

### 3.1 User Query Flow (RAG-Based Q&A)

This is the core pipeline that runs every time a user sends a message.

```
User types or speaks a question
              |
              v
+-------------------------------------------------------------+
|  STEP 1: LANGUAGE DETECTION & TRANSLATION                   |
|                                                             |
|  If language != English:                                    |
|    - Detect source language (en / hi / te / ta)             |
|    - Call translation_service.translate_to_english()        |
|    - Uses Groq LLM (temp=0.3) for accurate translation      |
|                                                             |
|  Why translate first?                                       |
|  The embedding model and retrieval system work best in      |
|  English. Translating before retrieval ensures the FAISS    |
|  semantic search finds relevant chunks regardless of the    |
|  user's input language.                                     |
+-------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------+
|  STEP 2: QUERY REWRITING                                    |
|                                                             |
|  - A separate LLM call fixes typos and rephrases the query  |
|  - Example: "sectoin 302 ipc murder penilty?" becomes       |
|    "What is the penalty for murder under Section 302 IPC?"  |
|                                                             |
|  Why?                                                       |
|  Legal queries often contain abbreviations, misspellings,   |
|  or vague phrasing. A clean rewritten query gives FAISS     |
|  a much better chance of retrieving the right chunks.       |
|  The original query is always shown to the user in the UI.  |
|  Only the internal search step uses the rewritten version.  |
+-------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------+
|  STEP 3: FAISS SEMANTIC RETRIEVAL                           |
|                                                             |
|  - Rewritten query is embedded using all-mpnet-base-v2      |
|  - Output: 768-dimensional dense vector                     |
|  - FAISS L2 similarity search over all indexed chunks       |
|  - Returns top-5 most relevant chunks from the session      |
|  - If no document is uploaded, context is empty             |
|                                                             |
|  What is FAISS?                                             |
|  FAISS (Facebook AI Similarity Search) is a library for     |
|  efficient nearest-neighbor search over dense vectors.      |
|  Each document chunk is stored as a 768-dim vector.         |
|  When the user asks a question, the query vector is         |
|  compared against all stored vectors and the most           |
|  similar ones are returned — these are semantically         |
|  related chunks, not just keyword matches.                  |
+-------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------+
|  STEP 4: CONTEXT AUGMENTATION                               |
|                                                             |
|  Three sources are combined into the LLM prompt:            |
|  1. Retrieved document chunks (top-5 from FAISS)            |
|  2. Chat history (last 6 messages = 3 exchanges)            |
|  3. User's current question (original language)             |
|                                                             |
|  Why include chat history?                                  |
|  Without history, the LLM treats every message as the       |
|  first. With it, follow-up questions like "explain that     |
|  in simpler terms" or "what about Section 304?" work        |
|  correctly because the LLM has the prior context.           |
+-------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------+
|  STEP 5: LLM GENERATION (Llama 3.3 70B via Groq)           |
|                                                             |
|  The prompt is structured as:                               |
|    - Legal Context: retrieved FAISS chunks                  |
|    - Previous Conversation: last 3 exchanges                |
|    - User Question                                          |
|    - Guidelines (enforced in the system prompt):            |
|      * Always cite BOTH IPC and BNS section numbers         |
|      * Reject non-legal questions with a clear message      |
|      * Separate similar case laws with ---SIMILAR_CASES---  |
|      * Format output with headings, bullets, bold terms     |
|      * Known IPC->BNS mapping (302->103, 420->318, etc.)    |
|                                                             |
|  Temperature: 0.6 (natural explanations, legally grounded)  |
+-------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------+
|  STEP 6: RESPONSE PARSING                                   |
|                                                             |
|  - Split response on the "---SIMILAR_CASES---" marker       |
|  - main_content: primary answer, shown immediately          |
|  - similar_cases: collapsed by default, user clicks to open |
|                                                             |
|  Why separate?                                              |
|  Similar case laws are useful but long. Keeping them        |
|  collapsible keeps the main answer clean and readable.      |
+-------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------+
|  STEP 7: RESPONSE TRANSLATION (if needed)                   |
|                                                             |
|  - If user language != English:                             |
|    translate main_content to user's language                |
|    translate similar_cases to user's language               |
|  - Uses Groq LLM for natural, fluent translation            |
+-------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------+
|  STEP 8: SAVE & RETURN                                      |
|                                                             |
|  - Save user message to chat_messages (SQLite)              |
|  - Save assistant response to chat_messages                 |
|  - Update session last_activity timestamp                   |
|  - Return: response, similar_cases, language, chunk_count   |
+-------------------------------------------------------------+
              |
              v
       Response displayed in chat UI
```

---

### 3.2 Document Upload & Processing Flow

When a user uploads a PDF, this pipeline runs to make it searchable.

```
User uploads PDF
              |
              v
+-------------------------------------------------------------+
|  STEP 1: FILE READING                                       |
|                                                             |
|  - FastAPI reads raw bytes from the multipart upload        |
|  - A unique document_id (UUID) is generated                 |
|  - File content is wrapped in an in-memory object           |
+-------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------+
|  STEP 2: TEXT EXTRACTION                                    |
|                                                             |
|  Primary — PyPDF2:                                          |
|    - Iterates through each page                             |
|    - Calls page.extract_text()                              |
|    - Records page number in metadata                        |
|                                                             |
|  Fallback — Tesseract OCR (for scanned PDFs):               |
|    - Converts each page to an image (pdf2image + Pillow)    |
|    - Runs pytesseract to extract text from the image        |
|    - Marks the chunk metadata with "ocr": true              |
|                                                             |
|  Why OCR fallback?                                          |
|  Many Indian court documents and FIRs are scanned images.   |
|  PyPDF2 returns empty text for these. OCR ensures content   |
|  is extracted even from non-digitally-native PDFs.          |
+-------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------+
|  STEP 3: LEGAL-AWARE CHUNKING                               |
|                                                             |
|  Stage A — Pattern-based splitting:                         |
|    Splits preferentially at legal section markers:          |
|    "Section", "IPC", "CrPC", "BNS", "under", "u/s"         |
|    Case references: " v. ", " AIR ", " SCC "               |
|    Accumulates up to 800 chars, then splits at next marker  |
|                                                             |
|  Stage B — Character-based splitting:                       |
|    RecursiveCharacterTextSplitter (LangChain)               |
|    chunk_size = 900 characters                              |
|    chunk_overlap = 200 characters                           |
|                                                             |
|  Why 900 chars with 200 overlap?                            |
|  Legal sentences are long. 900 chars fits 2-3 sentences.    |
|  200-char overlap means each chunk shares context with the  |
|  adjacent chunk — important when a legal clause spans a     |
|  chunk boundary and the user asks about it.                 |
+-------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------+
|  STEP 4: EMBEDDING GENERATION                               |
|                                                             |
|  - Model: sentence-transformers/all-mpnet-base-v2           |
|  - Runs entirely locally on CPU (no API key needed)         |
|  - Each chunk is converted to a 768-dimensional vector      |
|  - All chunks are embedded in a single batch call           |
|                                                             |
|  What is an embedding?                                      |
|  An embedding is a numerical representation of text where   |
|  semantically similar texts produce vectors that are close  |
|  in space. "Murder penalty" and "Section 302 IPC            |
|  punishment" produce very similar vectors even though the   |
|  exact words differ — this enables semantic search.         |
+-------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------+
|  STEP 5: FAISS INDEX CREATION & PERSISTENCE                 |
|                                                             |
|  - Index key: {session_id}_{document_id}                    |
|  - FAISS Flat index (exact L2 search, no approximation)     |
|  - All vectors and metadata (text, source, page) stored     |
|  - Index saved to disk: faiss_indexes/{key}.faiss           |
|  - Metadata saved: faiss_indexes/{key}.pkl                  |
|  - In-memory copy kept for fast repeated queries            |
|                                                             |
|  Why a flat (exact) index?                                  |
|  Legal documents are small-to-medium scale. Exact search    |
|  guarantees no relevant chunk is missed. Approximate        |
|  indexes (IVF, HNSW) trade accuracy for speed — not         |
|  appropriate when every legal clause detail matters.        |
+-------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------+
|  STEP 6: DATABASE RECORD                                    |
|                                                             |
|  - INSERT INTO session_documents                            |
|    (session_id, document_id, document_name, document_type)  |
|  - Supports multiple documents per session                  |
|  - Enables per-document retrieval and selective deletion    |
+-------------------------------------------------------------+
              |
              v
       Document is now fully searchable via FAISS
```

---

### 3.3 Audio / Video Processing Flow

```
User uploads audio or video file
              |
              v
+-------------------------------------------------------------+
|  STEP 1: FORMAT VALIDATION & TEMP FILE SAVE                 |
|                                                             |
|  Supported audio: .mp3, .wav, .m4a, .flac, .ogg, .webm     |
|  Supported video: .mp4, .avi, .mov, .mkv, .webm             |
|  File saved to OS temp directory to avoid memory overflow   |
+-------------------------------------------------------------+
              |
       +------+------+
       |             |
  Audio file    Video file
       |             |
       |             v
       |    +--------------------+
       |    | AUDIO EXTRACTION   |
       |    | Primary: ffmpeg    |
       |    |  -vn (no video)    |
       |    |  pcm_s16le codec   |
       |    |  16kHz, mono       |
       |    | Fallback: pydub    |
       |    +--------+-----------+
       |             |
       +------+------+
              |
              v
+-------------------------------------------------------------+
|  STEP 2: WHISPER TRANSCRIPTION                              |
|                                                             |
|  - Model: faster-whisper (tiny, int8 quantized, CPU)        |
|  - Language: auto-detected unless user selected one         |
|  - Config: beam_size=5, no_speech_threshold=0.3             |
|  - Returns a generator of timed segments                    |
|  - All segment texts are joined into a full transcript      |
|  - Also returns: detected language code + confidence        |
|                                                             |
|  Example output:                                            |
|    text: "Section 420 IPC pertains to cheating..."          |
|    language: "en" (probability: 0.98)                       |
|    segments: [{start:0.0, end:4.2, text:"..."}, ...]        |
+-------------------------------------------------------------+
              |
              v
+-------------------------------------------------------------+
|  STEP 3: TEXT CHUNKING, EMBEDDING & INDEXING                |
|                                                             |
|  - Same legal-aware chunking as PDF (900 chars, 200 overlap)|
|  - Metadata: {source, type: "audio"/"video", language, text}|
|  - Embed chunks with all-mpnet-base-v2                      |
|  - Create FAISS index for the session                       |
|  - Transcription text is also shown to user in the chat     |
|  - Document record inserted into session_documents          |
+-------------------------------------------------------------+
              |
              v
       Audio/video content is now queryable like any document
```

**Live voice input (browser microphone):**
- `AudioRecorder.jsx` records via the browser's `MediaRecorder` API
- Sends the `.webm` audio blob to `/api/transcribe-audio`
- Transcribed text is placed directly into the message input box
- User can read/edit the text before sending
- Language hint is passed to Whisper when a specific language is selected

---

### 3.4 Authentication Flow

```
REGISTRATION                          LOGIN
     |                                  |
     v                                  v
Hash password (SHA256)         Verify password hash
     |                                  |
INSERT INTO users              Lookup user by username or email
     |                                  |
Generate session token          Generate session token
(32 random bytes, hex encoded)  (32 random bytes, hex encoded)
     |                                  |
Store in active_sessions{}      Store in active_sessions{}
(in-memory dict, 7-day expiry)  (in-memory dict, 7-day expiry)
     |                                  |
Return token to frontend         Return token to frontend
     |                                  |
     +----------------+-----------------+
                      |
                      v
    Frontend stores in localStorage('session_token')
                      |
                      v
    Every API call includes: Authorization: Bearer <token>
                      |
                      v
    Middleware validates token on every protected request
    Checks active_sessions{}, verifies expiry timestamp
```

---

## 4. Model Selection & Rationale

### 4.1 LLM — Llama 3.3 70B Versatile (via Groq)

| Attribute | Detail |
|-----------|--------|
| Provider | Meta (open weights), served via Groq |
| Parameters | 70 billion |
| Inference speed | ~300–400 tokens/second (Groq LPU) |
| Context window | 128K tokens |
| Temperature (chat) | 0.6 |
| Temperature (translation) | 0.3 |
| Temperature (legal analysis) | 0.2 |

**Why Llama 3.3 70B?**

- **Speed:** Groq's LPU (Language Processing Unit) hardware delivers 5–10x lower latency than standard GPU inference. For a real-time legal assistant, response speed matters.
- **Quality:** 70B parameters provides near GPT-4 quality reasoning for complex multi-step legal analysis.
- **Open weights:** No vendor lock-in. The model can be self-hosted if Groq is unavailable.
- **Multilingual:** Covers Hindi, Telugu, and Tamil natively without any fine-tuning.
- **Temperature tuning:** Lower temperature for structured analysis (0.2) ensures factual, reproducible output. Higher for conversational chat (0.6) allows natural explanations.

**Why not GPT-4 or Claude?**
- Groq's speed advantage is 5–10x over OpenAI/Anthropic latency
- Cost is significantly lower per million tokens on Groq
- Llama 3.3 70B benchmark scores are comparable to GPT-4o on legal reasoning tasks

---

### 4.2 Embedding Model — all-mpnet-base-v2

| Attribute | Detail |
|-----------|--------|
| Architecture | MPNet (Masked and Permuted Pre-training) |
| Output dimensions | 768 |
| Max input tokens | 514 |
| Training data | 1 billion+ sentence pairs |
| Inference | Local CPU, ~10ms per batch |
| License | Apache 2.0 (free commercial use) |

**Why all-mpnet-base-v2?**

- Top-ranked on SBERT (Sentence-BERT) benchmarks for semantic textual similarity
- 768 dimensions: high expressiveness without excessive storage or memory
- Runs entirely locally — no API cost or network latency for embedding
- MPNet's bidirectional context window captures legal sentence semantics better than older BERT-based models
- Produces stable, consistent embeddings — important so that the same legal clause always retrieves correctly

**What are embeddings?**
Each document chunk and each user query are converted to 768-dimensional numerical vectors. The distance between two vectors measures their semantic similarity. Chunks with vectors close to the query vector are returned as context. This is semantic search — it finds conceptually related content even when the exact words differ.

---

### 4.3 Speech-to-Text — faster-whisper (tiny)

| Attribute | Detail |
|-----------|--------|
| Base model | OpenAI Whisper |
| Implementation | faster-whisper (CTranslate2 backend) |
| Model size | tiny (39M parameters, ~75MB with int8) |
| Quantization | int8 (4x memory reduction vs float32) |
| Device | CPU |
| Languages supported | 99 languages |
| Speed vs original Whisper | ~4x faster |

**Why faster-whisper tiny?**

- Runs on CPU with no GPU requirement — deployable anywhere
- 39M parameters is sufficient for clear legal audio and voice input
- int8 quantization brings memory down to ~75MB, making it practical on standard hardware
- Auto-language detection allows users to speak in any language without configuring anything
- Offline — audio data never leaves the server, important for sensitive legal recordings

**Why not a cloud STT API (Google, Azure, Deepgram)?**
- No per-request cost
- No data privacy concerns — audio stays local
- Works offline, no internet dependency for transcription

---

### 4.4 Vector Database — FAISS (faiss-cpu)

| Attribute | Detail |
|-----------|--------|
| Provider | Meta (Facebook AI Research) |
| Index type | Flat (exact L2 search) |
| Query speed | Very fast for document-scale indexes |
| Storage | Local disk (.faiss + .pkl per document) |
| GPU required | No (faiss-cpu) |

**Why FAISS over cloud alternatives (Pinecone, Weaviate, Chroma)?**

- Entirely local — no cloud cost, no data leaves the machine
- Flat exact index guarantees no relevant chunk is ever missed
- Session-scoped isolation: each user's documents are completely separated
- Persistence via disk serialization — indexes survive server restarts
- No separate process or server to run and maintain

---

## 5. Performance Evaluation

### 5.1 Retrieval Quality Factors

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Chunk size | 900 characters | Fits 2–3 legal sentences; tested against 500, 700, 1000 — 900 gave best answer quality |
| Chunk overlap | 200 characters | Captures context at chunk boundaries; prevents losing clause context |
| Top-k retrieval | 5 chunks | Balances context completeness vs. prompt length; more than 5 introduces noise |

### 5.2 Query Rewriting Impact

Without query rewriting, FAISS retrieval fails for common patterns:

| User Input | Problem | After Rewriting |
|------------|---------|-----------------|
| "sectoin 302 ipc murder penilty?" | Typos cause embedding drift | "What is the penalty for murder under Section 302 IPC?" |
| "what happens if someone cheats me" | Too vague | "What legal remedies are available for cheating under IPC/BNS?" |
| "what is 498a" | Too short | "Explain Section 498A IPC and its applicability" |

The rewriting step significantly improves FAISS hit rate for casual or error-prone queries without changing what the user sees.

### 5.3 LLM Temperature Selection

| Component | Temperature | Reason |
|-----------|-------------|--------|
| Chat responses | 0.6 | Natural, readable explanations with some flexibility |
| Translation | 0.3 | Accurate, consistent translation without creative drift |
| Legal analysis / section prediction | 0.2 | Factual, deterministic, reproducible legal output |

### 5.4 Language Support

| Language | Voice Input | Chat Q&A | UI Translation |
|----------|------------|----------|----------------|
| English | Yes (Whisper) | Yes (LLM) | Native |
| Hindi | Yes (Whisper, auto-detect) | Yes (LLM) | Yes (Groq) |
| Telugu | Yes (Whisper, auto-detect) | Yes (LLM) | Yes (Groq) |
| Tamil | Yes (Whisper, auto-detect) | Yes (LLM) | Yes (Groq) |

### 5.5 Document Type Coverage

| Input Type | Extraction Method | Queryable |
|------------|-----------------|-----------|
| Digitally-native PDF | PyPDF2 | Yes |
| Scanned PDF (image-based) | Tesseract OCR | Yes |
| Audio (.mp3, .wav, .m4a, .flac, .ogg) | Whisper | Yes |
| Video (.mp4, .avi, .mov, .mkv, .webm) | ffmpeg + Whisper | Yes |
| Live microphone recording | Browser WebAudio + Whisper | Query input only |

---

## 6. Key Technical Concepts

### 6.1 Retrieval-Augmented Generation (RAG)

RAG solves a core limitation of LLMs: their knowledge is frozen at training time, and they hallucinate when asked about specific documents they have not seen.

**Without RAG:**
```
User: "What does Clause 3 of the uploaded FIR say?"
LLM: [Invents a plausible-sounding but incorrect answer]
```

**With RAG:**
```
User: "What does Clause 3 of the uploaded FIR say?"
System:
  1. Embed query → search FAISS → retrieve Clause 3 chunk
  2. Insert chunk into LLM prompt as context
  3. LLM reads the actual clause and answers from it
```

The LLM is grounded in the actual document. It cannot hallucinate because the correct content is placed directly in its context window before it generates a response.

---

### 6.2 IPC to BNS Mapping

India replaced the Indian Penal Code (IPC, 1860) with the Bharatiya Nyaya Sanhita (BNS, 2023), effective July 1, 2024. Cases filed before that date use IPC; new cases use BNS. Practitioners need both references.

| Offense | IPC Section | BNS Section |
|---------|-------------|-------------|
| Murder | 302 | 103 |
| Culpable homicide | 304 | 105 |
| Attempt to murder | 307 | 109 |
| Rape and sexual offenses | 376 | 63–70 |
| Cheating | 420 | 318 |
| Cruelty by husband or relatives | 498A | 84–85 |

The system prompt instructs the LLM to always cite both section numbers in every response.

---

### 6.3 Legal-Aware Chunking

Standard text chunking (splitting every N characters at arbitrary positions) frequently breaks legal clauses mid-sentence, destroying their meaning and making retrieval unreliable.

The system uses a two-stage approach:

**Stage A — Pattern-based:** Accumulates text and splits only at legal section boundaries ("Section XXX", "u/s", "IPC", case citations " v. ", "AIR", "SCC"). This keeps legal clauses intact.

**Stage B — Size enforcement:** Any chunk still over 900 characters is split with 200-character overlap using `RecursiveCharacterTextSplitter`. The overlap ensures that a clause spanning two chunks appears in both, so retrieval finds it regardless of where the split fell.

---

### 6.4 Multi-Tenancy & Session Isolation

Every user's data is completely separated:

- FAISS indexes use `{session_id}_{document_id}` as the key — no cross-user access is possible
- All database queries filter by `user_id`
- Session tokens are user-specific with a 7-day expiry
- Deleting a document removes both the FAISS index files from disk and the database record

---

### 6.5 Lazy Model Loading

Both the Whisper model and the embedding model are loaded lazily — only on the first request that needs them, not at server startup. This:

- Reduces server startup time from ~60 seconds to ~2 seconds
- Avoids allocating ~600MB of RAM if those features are never used in a session
- Makes the server responsive immediately after starting

---

## 7. Database Schema

```sql
-- Registered users
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat sessions (one session = one conversation thread)
CREATE TABLE chat_sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id    TEXT UNIQUE NOT NULL,
    user_id       INTEGER REFERENCES users(id),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual messages within a session
CREATE TABLE chat_messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES chat_sessions(session_id),
    role       TEXT NOT NULL,       -- "user" or "assistant"
    content    TEXT NOT NULL,
    user_role  TEXT NOT NULL,       -- language code (en / hi / te / ta)
    pdf_name   TEXT,
    timestamp  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_session_id ON chat_messages(session_id);
CREATE INDEX idx_timestamp  ON chat_messages(timestamp);

-- Documents uploaded within a session
CREATE TABLE session_documents (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id    TEXT NOT NULL REFERENCES chat_sessions(session_id),
    document_id   TEXT UNIQUE NOT NULL,
    document_name TEXT NOT NULL,
    document_type TEXT NOT NULL,    -- "pdf", "audio", or "video"
    uploaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_doc_session ON session_documents(session_id);
```

---

## 8. API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register new user |
| POST | `/api/login` | Login, returns session token |
| POST | `/api/logout` | Invalidate session token |
| GET | `/api/verify-session` | Check if token is still valid |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message, get RAG-based response |
| GET | `/api/history/{session_id}` | Get full chat history for a session |

### Sessions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sessions` | List all sessions for the logged-in user |
| POST | `/api/sessions/new` | Create a new chat session |
| DELETE | `/api/sessions/{session_id}` | Delete session and all its data |

### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload-document` | Upload and index a PDF |
| POST | `/api/upload-audio-video` | Upload, transcribe, and index audio/video |
| GET | `/api/documents/{session_id}` | List documents in a session |
| DELETE | `/api/documents/{session_id}/{doc_id}` | Delete document and its FAISS index |

### Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze-document` | Structured legal analysis of uploaded document(s) |
| POST | `/api/extract-entities` | Extract people, sections, and dates from documents |
| POST | `/api/transcribe-audio` | Transcribe an audio or video file |
| POST | `/api/translate` | Translate text between supported languages |

### Utility
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |

---

## 9. Frontend Architecture

```
src/
├── App.jsx                     # Auth wrapper, routing, logout handler
├── App.css                     # All styles (responsive, mobile-first)
├── components/
│   ├── ChatInterface.jsx       # Main shell: sidebar, sessions, chat area
│   ├── MessageList.jsx         # Renders messages with markdown formatting
│   ├── MessageInput.jsx        # Input bar with upload menu and mic button
│   ├── AudioRecorder.jsx       # Browser microphone recording (WebAudio API)
│   ├── DocumentList.jsx        # Document manager with search and multi-select
│   ├── LegalAnalysisView.jsx   # Renders structured legal analysis JSON
│   ├── LanguageSelector.jsx    # Language toggle (en / hi / te / ta)
│   ├── Toast.jsx               # Notification banners (success, error, info)
│   ├── Login.jsx               # Login form
│   └── Register.jsx            # Registration form
└── services/
    └── api.js                  # All fetch() calls to the backend
```

**Key frontend behaviors:**
- Session token stored in `localStorage` — persists across browser sessions and page refreshes
- The original user query is always shown in the chat, even though a rewritten version is used for internal search
- Similar case laws are collapsed under each response by default — click to expand
- Voice recording uses `MediaRecorder` API, sends a `.webm` blob to `/api/transcribe-audio`, and places the result in the input box for the user to review before sending
- Sidebar collapses on desktop using a width transition; slides in as an overlay with a backdrop on mobile
- Messages auto-scroll to the bottom on each new message

---

## 10. Setup & Running

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) — install and add to PATH (default: `C:\Program Files\Tesseract-OCR`)
- [ffmpeg](https://ffmpeg.org/download.html) — install and add to PATH
- A [Groq API key](https://console.groq.com) (free tier available)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

# Create .env with your Groq API key
echo GROQ_API_KEY=your_key_here > .env

uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### First Use

1. Open `http://localhost:5173` and register an account
2. Ask any legal question or upload a PDF / audio / video
3. The embedding model (~420MB) and Whisper model (~75MB) are downloaded automatically on first use

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for LLM inference and translation |

All other models (sentence embeddings, Whisper) run locally and require no API keys.

---

## Project Structure

```
FIR-RAG/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py               # All API endpoints
│   │   ├── auth/
│   │   │   ├── auth_service.py         # Token creation and validation
│   │   │   └── middleware.py           # Auth middleware for all requests
│   │   ├── services/
│   │   │   ├── chat_service.py         # RAG pipeline orchestration
│   │   │   ├── faiss_store.py          # FAISS vector DB management
│   │   │   ├── document_processor.py  # PDF extraction and chunking
│   │   │   ├── speech_to_text.py      # Whisper transcription
│   │   │   ├── translation_service.py # Multilingual translation
│   │   │   └── legal_section_predictor.py  # Structured legal analysis
│   │   └── main.py                     # FastAPI app init + SQLite DB setup
│   ├── faiss_indexes/                  # Persisted FAISS indexes (auto-created)
│   ├── fir.db                          # SQLite database (auto-created)
│   ├── requirements.txt
│   └── .env                            # GROQ_API_KEY
└── frontend/
    ├── src/
    │   ├── components/                 # All React components
    │   ├── services/api.js             # Backend API client
    │   ├── App.jsx
    │   └── App.css
    └── package.json
```
