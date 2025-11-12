import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
import numpy as np
from pgvector.psycopg2 import register_vector

class EmbeddingManager:
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            api_key=self.openai_api_key,
            model="text-embedding-3-small"  # Latest embedding model
        )
        
        # PostgreSQL connection parameters
        self.db_params = {
            'host': os.environ.get('POSTGRES_HOST', 'localhost'),
            'port': os.environ.get('POSTGRES_PORT', '5432'),
            'database': os.environ.get('POSTGRES_DB', 'docuchatai'),
            'user': os.environ.get('POSTGRES_USER', 'postgres'),
            'password': os.environ.get('POSTGRES_PASSWORD', 'password')
        }
        
        self._setup_database()
    
    def _get_connection(self):
        """Get PostgreSQL connection with pgvector support"""
        conn = psycopg2.connect(**self.db_params)
        register_vector(conn)
        return conn
    
    def _setup_database(self):
        """Setup PostgreSQL database and tables with pgvector extension"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Enable pgvector extension
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
                
                # Create documents table with vector column
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id SERIAL PRIMARY KEY,
                        filename TEXT NOT NULL,
                        chunk_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        embedding vector(1536),  -- OpenAI text-embedding-3-small has 1536 dimensions
                        metadata JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create index for filename lookups
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_documents_filename 
                    ON documents(filename)
                """)
                
                # Create vector similarity index for fast similarity search
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_documents_embedding 
                    ON documents USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100)
                """)
                
                conn.commit()
                
        except Exception as e:
            raise Exception(f"Error setting up database: {str(e)}")
    
    def store_document_embeddings(self, text_chunks: List[Dict[str, Any]], filename: str):
        """Generate embeddings for text chunks and store in PostgreSQL database"""
        try:
            # First, delete existing chunks for this document
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM documents WHERE filename = %s", (filename,))
                conn.commit()
            
            # Process chunks in batches
            batch_size = 10
            for i in range(0, len(text_chunks), batch_size):
                batch = text_chunks[i:i + batch_size]
                
                # Generate embeddings for batch
                texts = [chunk["content"] for chunk in batch]
                embedding_vectors = self.embeddings.embed_documents(texts)
                
                # Store in database
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    for j, chunk in enumerate(batch):
                        embedding_vector = embedding_vectors[j]
                        
                        # Convert metadata to JSONB
                        metadata = chunk["metadata"]
                        
                        cursor.execute("""
                            INSERT INTO documents (filename, chunk_id, content, embedding, metadata)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            filename,
                            chunk["metadata"]["chunk_id"],
                            chunk["content"],
                            embedding_vector,  # pgvector handles the conversion
                            json.dumps(metadata)
                        ))
                    conn.commit()
                    
        except Exception as e:
            raise Exception(f"Error storing embeddings: {str(e)}")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar document chunks using vector similarity"""
        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query)
            
            # Convert list to numpy array and then to vector format
            query_vector = np.array(query_embedding).tolist()
            
            # Use pgvector's cosine similarity operator with explicit cast
            with self._get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT content, metadata, filename, 
                           1 - (embedding <=> %s::vector) as similarity
                    FROM documents
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (query_vector, query_vector, k))
                
                results = cursor.fetchall()
                
                # Convert results to list of dictionaries
                similarities = []
                for row in results:
                    similarities.append({
                        "content": row["content"],
                        "metadata": row["metadata"],
                        "filename": row["filename"],
                        "similarity": float(row["similarity"])
                    })
                
                return similarities
                
        except Exception as e:
            raise Exception(f"Error during similarity search: {str(e)}")
    
    def get_document_list(self) -> List[str]:
        """Get list of all processed documents"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT filename FROM documents ORDER BY filename")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            raise Exception(f"Error retrieving document list: {str(e)}")
    
    def delete_document(self, filename: str) -> bool:
        """Delete a document and all its embeddings from the database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if document exists
                cursor.execute("SELECT COUNT(*) FROM documents WHERE filename = %s", (filename,))
                count = cursor.fetchone()[0]
                
                if count == 0:
                    return False  # Document not found
                
                # Delete all chunks for this document
                cursor.execute("DELETE FROM documents WHERE filename = %s", (filename,))
                conn.commit()
                
                # Check if any rows were deleted
                if cursor.rowcount > 0:
                    print(f"Successfully deleted {cursor.rowcount} chunks for document: {filename}")
                    return True
                else:
                    return False
                    
        except Exception as e:
            raise Exception(f"Error deleting document '{filename}': {str(e)}")
    
    def delete_all_documents(self) -> int:
        """Delete all documents and embeddings from the database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Count documents before deletion
                cursor.execute("SELECT COUNT(*) FROM documents")
                count_before = cursor.fetchone()[0]
                
                # Delete all documents
                cursor.execute("DELETE FROM documents")
                conn.commit()
                
                print(f"Successfully deleted all documents ({count_before} chunks removed)")
                return count_before
                
        except Exception as e:
            raise Exception(f"Error deleting all documents: {str(e)}")
