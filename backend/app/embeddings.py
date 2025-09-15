import os
from typing import List, Dict, Any
import psycopg2
from sqlalchemy import create_engine, text
from langchain_openai import OpenAIEmbeddings
import numpy as np

class EmbeddingManager:
    def __init__(self):
        self.database_url = os.environ.get("DATABASE_URL")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            api_key=self.openai_api_key,
            model="text-embedding-3-small"  # Latest embedding model
        )
        
        # Initialize database connection
        self.engine = create_engine(self.database_url)
        self._setup_database()
    
    def _setup_database(self):
        """Setup database tables and pgvector extension"""
        with self.engine.connect() as conn:
            # Enable pgvector extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            
            # Create documents table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    chunk_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(1536),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create index for vector similarity search
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS documents_embedding_idx 
                ON documents USING ivfflat (embedding vector_cosine_ops)
            """))
            
            conn.commit()
    
    def store_document_embeddings(self, text_chunks: List[Dict[str, Any]], filename: str):
        """Generate embeddings for text chunks and store in database"""
        try:
            # First, delete existing chunks for this document
            with self.engine.connect() as conn:
                conn.execute(
                    text("DELETE FROM documents WHERE filename = :filename"),
                    {"filename": filename}
                )
                conn.commit()
            
            # Process chunks in batches
            batch_size = 10
            for i in range(0, len(text_chunks), batch_size):
                batch = text_chunks[i:i + batch_size]
                
                # Generate embeddings for batch
                texts = [chunk["content"] for chunk in batch]
                embedding_vectors = self.embeddings.embed_documents(texts)
                
                # Store in database
                with self.engine.connect() as conn:
                    for j, chunk in enumerate(batch):
                        embedding_vector = embedding_vectors[j]
                        
                        conn.execute(
                            text("""
                                INSERT INTO documents (filename, chunk_id, content, embedding, metadata)
                                VALUES (:filename, :chunk_id, :content, :embedding, :metadata)
                            """),
                            {
                                "filename": filename,
                                "chunk_id": chunk["metadata"]["chunk_id"],
                                "content": chunk["content"],
                                "embedding": str(embedding_vector),
                                "metadata": chunk["metadata"]
                            }
                        )
                    conn.commit()
                    
        except Exception as e:
            raise Exception(f"Error storing embeddings: {str(e)}")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar document chunks using vector similarity"""
        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query)
            
            # Search for similar vectors
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT content, metadata, filename, 
                               1 - (embedding <=> :query_embedding) as similarity
                        FROM documents
                        ORDER BY embedding <=> :query_embedding
                        LIMIT :k
                    """),
                    {
                        "query_embedding": str(query_embedding),
                        "k": k
                    }
                )
                
                chunks = []
                for row in result:
                    chunks.append({
                        "content": row.content,
                        "metadata": row.metadata,
                        "filename": row.filename,
                        "similarity": float(row.similarity)
                    })
                
                return chunks
                
        except Exception as e:
            raise Exception(f"Error during similarity search: {str(e)}")
    
    def get_document_list(self) -> List[str]:
        """Get list of all processed documents"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT DISTINCT filename FROM documents ORDER BY filename")
                )
                return [row.filename for row in result]
        except Exception as e:
            raise Exception(f"Error retrieving document list: {str(e)}")