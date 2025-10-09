import os
import json
from typing import List, Dict, Any
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from langchain_openai import OpenAIEmbeddings
import numpy as np
from urllib.parse import urlparse, urlunparse, parse_qs

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
        
        # Initialize database connection with conditional SSL for local development
        prepared_url = self._prepare_database_url(self.database_url)
        parsed = urlparse(prepared_url)
        is_local = parsed.hostname in ("localhost", "127.0.0.1")

        connect_args = {"connect_timeout": 30}
        if not is_local:
            connect_args["sslmode"] = "require"
        else:
            # Disable SSL when talking to local Docker/Postgres
            connect_args["sslmode"] = "disable"

        self.engine = create_engine(
            prepared_url,
            pool_pre_ping=True,  # Enable connection health checks
            pool_recycle=3600,   # Recycle connections every hour
            connect_args=connect_args
        )
        self._setup_database()
    
    def _prepare_database_url(self, url: str) -> str:
        """Convert postgres:// scheme to postgresql+psycopg2:// and ensure SSL settings"""
        try:
            parsed = urlparse(url)
            
            # Convert postgres:// scheme to postgresql+psycopg2://
            if parsed.scheme == "postgres":
                # Replace scheme
                new_scheme = "postgresql+psycopg2"
                new_url = urlunparse((
                    new_scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
                return new_url
            elif parsed.scheme == "postgresql":
                # Add psycopg2 dialect if not present
                new_scheme = "postgresql+psycopg2"
                new_url = urlunparse((
                    new_scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
                return new_url
            else:
                # Return as is if already properly formatted
                return url
        except Exception as e:
            # If URL parsing fails, return original URL and let SQLAlchemy handle it
            print(f"Warning: Could not parse DATABASE_URL: {str(e)}")
            return url
    
    def _setup_database(self):
        """Setup database tables and pgvector extension"""
        with self.engine.connect() as conn:
            # Enable pgvector extension (with error handling for managed databases)
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            except Exception as e:
                # If extension creation fails, check if it already exists
                try:
                    result = conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'"))
                    if not result.fetchone():
                        raise Exception(f"pgvector extension is not available: {str(e)}")
                except Exception:
                    raise Exception(f"pgvector extension is required but not available: {str(e)}")
            
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
            
            conn.commit()
            
            # Create index for vector similarity search (after ensuring data exists)
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS documents_embedding_idx 
                    ON documents USING ivfflat (embedding vector_cosine_ops)
                """))
                conn.commit()
            except Exception as e:
                # Index creation might fail if there's no data yet, that's okay
                print(f"Note: Vector index creation deferred: {str(e)}")
    
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
                        
                        # Convert embedding vector to proper PostgreSQL vector format
                        embedding_str = '[' + ','.join(map(str, embedding_vector)) + ']'
                        metadata_str = json.dumps(chunk["metadata"])
                        
                        # Use raw SQL with proper parameter binding
                        conn.execute(
                            text("""
                                INSERT INTO documents (filename, chunk_id, content, embedding, metadata)
                                VALUES (:filename, :chunk_id, :content, CAST(:embedding AS vector), CAST(:metadata AS jsonb))
                            """),
                            {
                                "filename": filename,
                                "chunk_id": chunk["metadata"]["chunk_id"],
                                "content": chunk["content"],
                                "embedding": embedding_str,
                                "metadata": metadata_str
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
            
            # Convert query embedding to proper PostgreSQL vector format
            query_embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            # Search for similar vectors
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT content, metadata, filename, 
                               1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
                        FROM documents
                        ORDER BY embedding <=> CAST(:query_embedding AS vector)
                        LIMIT :k
                    """),
                    {
                        "query_embedding": query_embedding_str,
                        "k": k
                    }
                )
                
                chunks = []
                for row in result:
                    # Handle metadata parsing
                    metadata = row.metadata
                    if isinstance(metadata, str):
                        try:
                            metadata = json.loads(metadata)
                        except json.JSONDecodeError:
                            metadata = {}
                    
                    chunks.append({
                        "content": row.content,
                        "metadata": metadata,
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