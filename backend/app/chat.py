import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from .embeddings import EmbeddingManager

class ChatManager:
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize OpenAI chat model
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        self.llm = ChatOpenAI(
            api_key=self.openai_api_key,
            model="gpt-5",
            temperature=0.7
        )
    
    def get_response(self, user_message: str) -> str:
        """Generate response using RAG approach"""
        try:
            # Retrieve relevant document chunks
            relevant_chunks = self.embedding_manager.similarity_search(user_message, k=5)
            
            if not relevant_chunks:
                return "I don't have any documents to reference. Please upload a PDF first."
            
            # Prepare context from retrieved chunks
            context = self._prepare_context(relevant_chunks)
            
            # Create system prompt with context
            system_prompt = f"""You are a helpful AI assistant that answers questions based on the provided document context. 
            Use the following context to answer the user's question. If the answer cannot be found in the context, 
            say so clearly and suggest uploading relevant documents.

            Context:
            {context}
            
            Instructions:
            - Answer based only on the provided context
            - Be specific and cite information from the documents when possible
            - If the context doesn't contain enough information, say so
            - Keep your response clear and helpful"""
            
            # Generate response
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
    
    def _prepare_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Prepare context string from retrieved chunks"""
        context_parts = []
        
        for i, chunk in enumerate(chunks):
            filename = chunk.get("filename", "Unknown")
            similarity = chunk.get("similarity", 0)
            content = chunk.get("content", "")
            
            context_part = f"""Document: {filename}
Relevance: {similarity:.3f}
Content: {content}
---"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)