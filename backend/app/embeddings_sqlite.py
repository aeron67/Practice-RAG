import os
import json
import sqlite3
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
import numpy as np
from pathlib import Path

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
        
        # Create local SQLite database
        self.db_path = Path("docuchatai.db")
        self._setup_database()
    
    def _setup_database(self):
        """Setup SQLite database and tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    chunk_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding TEXT NOT NULL,  -- Store as JSON string
                    metadata TEXT NOT NULL,   -- Store as JSON string
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for filename lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_filename 
                ON documents(filename)
            """)
            
            conn.commit()
    
    def store_document_embeddings(self, text_chunks: List[Dict[str, Any]], filename: str):
        """Generate embeddings for text chunks and store in SQLite database"""
        try:
            # First, delete existing chunks for this document
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM documents WHERE filename = ?", (filename,))
                conn.commit()
            
            # Process chunks in batches
            batch_size = 10
            for i in range(0, len(text_chunks), batch_size):
                batch = text_chunks[i:i + batch_size]
                
                # Generate embeddings for batch
                texts = [chunk["content"] for chunk in batch]
                embedding_vectors = self.embeddings.embed_documents(texts)
                
                # Store in database
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    for j, chunk in enumerate(batch):
                        embedding_vector = embedding_vectors[j]
                        
                        # Store embedding as JSON string
                        embedding_json = json.dumps(embedding_vector)
                        metadata_json = json.dumps(chunk["metadata"])
                        
                        cursor.execute("""
                            INSERT INTO documents (filename, chunk_id, content, embedding, metadata)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            filename,
                            chunk["metadata"]["chunk_id"],
                            chunk["content"],
                            embedding_json,
                            metadata_json
                        ))
                    conn.commit()
                    
        except Exception as e:
            raise Exception(f"Error storing embeddings: {str(e)}")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar document chunks using vector similarity"""
        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query)
            
            # Get all documents and calculate similarity
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT content, metadata, filename, embedding
                    FROM documents
                """)
                
                results = cursor.fetchall()
                
                # Calculate similarities
                similarities = []
                for row in results:
                    content, metadata_str, filename, embedding_str = row
                    
                    # Parse stored embedding
                    stored_embedding = json.loads(embedding_str)
                    
                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(query_embedding, stored_embedding)
                    
                    # Parse metadata
                    try:
                        metadata = json.loads(metadata_str)
                    except json.JSONDecodeError:
                        metadata = {}
                    
                    similarities.append({
                        "content": content,
                        "metadata": metadata,
                        "filename": filename,
                        "similarity": similarity
                    })
                
                # Sort by similarity and return top k
                similarities.sort(key=lambda x: x["similarity"], reverse=True)
                return similarities[:k]
                
        except Exception as e:
            raise Exception(f"Error during similarity search: {str(e)}")
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
        except Exception:
            return 0.0
    
    def get_document_list(self) -> List[str]:
        """Get list of all processed documents"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT filename FROM documents ORDER BY filename")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            raise Exception(f"Error retrieving document list: {str(e)}")
    
    def delete_document(self, filename: str) -> bool:
        """Delete a document and all its embeddings from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if document exists
                cursor.execute("SELECT COUNT(*) FROM documents WHERE filename = ?", (filename,))
                count = cursor.fetchone()[0]
                
                if count == 0:
                    return False  # Document not found
                
                # Delete all chunks for this document
                cursor.execute("DELETE FROM documents WHERE filename = ?", (filename,))
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
            with sqlite3.connect(self.db_path) as conn:
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