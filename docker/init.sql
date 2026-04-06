--docker/init.sql

--PostgreSQL
--turn on pgvector extension (before using vector type)
CREATE EXTENSION IF NOT EXISTS vector;

-- saved_chunk from document
CREATE TABLE IF NOT EXISTS document_chunks(
    id BIGSERIAL ,
    source_file TEXT NOT NULL,              -- name of  origianl PDF file
    page_number INTEGER NOT NULL,           
    chunk_type TEXT NOT NULL,               --  'text' or 'image'
    content TEXT NOT NULL,                  -- general content of the chunk
    embedding vector(1536),                 -- OpenAI text_embedding-3-small = 1536 dimensions
    created_at TIMESTAMPTZ DEFAULT now(),   -- timestamp with timezone
    PRIMARY KEY(id)
);

-- Index for vector similarity search using hsnw
-- HSNW (Hierarchical Navigable Small World): a high-performance indexing algorithm used for vector similarity search, primarily through the pgvector extension
CREATE INDEX IF NOT EXISTS idx_embedding_hsnw
    ON document_chunks
    USING hsnw (embedding vector_cosine_ops);

-- Index for filter base on file
CREATE INDEX IF NOT EXISTS idx_source_file
    ON document_chunks (source_file)

-- chat memory
CREATE TABLE IF NOT EXISTS chat_history(
    id BIGSERIAL,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,             --'human' or 'ai'
    content TEXT NOT NULL, 
    created_at TIMESTAMPTZ DEFAULT now()
);

--creatte index base on session_id
CREATE INDEX IF NOT EXISTS idx_session_id
    ON chat_history(session_id);