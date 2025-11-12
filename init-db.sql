-- Initialize the database with pgvector extension
-- This script runs when the PostgreSQL container starts for the first time

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    chunk_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-small has 1536 dimensions
    metadata JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_filename 
ON documents(filename);

-- Create vector similarity index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_documents_embedding 
ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create a function to get database info
CREATE OR REPLACE FUNCTION get_database_info()
RETURNS TABLE(
    total_documents BIGINT,
    total_chunks BIGINT,
    database_size TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT filename) as total_documents,
        COUNT(*) as total_chunks,
        pg_size_pretty(pg_database_size(current_database())) as database_size;
END;
$$ LANGUAGE plpgsql;

