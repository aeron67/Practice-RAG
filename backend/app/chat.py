import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .embeddings_postgres import EmbeddingManager

class ChatManager:
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize OpenAI chat model
        # Use configurable model with sensible default
        self.model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        
        try:
            self.llm = ChatOpenAI(
                api_key=self.openai_api_key,
                model=self.model_name,
                temperature=0.7
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI model '{self.model_name}': {str(e)}")
    
    def get_response(self, user_message: str) -> str:
        """Generate response using RAG approach"""
        try:
            # Input validation
            if not user_message or not user_message.strip():
                return "Please provide a valid question or message."
            
            # Retrieve relevant document chunks
            try:
                relevant_chunks = self.embedding_manager.similarity_search(user_message, k=5)
            except Exception as e:
                return f"Error retrieving relevant documents: {str(e)}"
            
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
            
            # Generate response with error handling
            try:
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_message)
                ]
                
                response = self.llm.invoke(messages)
                
                if hasattr(response, 'content') and response.content:
                    return response.content
                else:
                    return "I apologize, but I couldn't generate a proper response. Please try again."
                    
            except Exception as openai_error:
                error_msg = str(openai_error).lower()
                if "rate limit" in error_msg:
                    return "I'm currently experiencing high demand. Please try again in a moment."
                elif "insufficient_quota" in error_msg or "quota" in error_msg:
                    return "The OpenAI API quota has been exceeded. Please check your API credits."
                elif "invalid_api_key" in error_msg:
                    return "There's an issue with the API configuration. Please contact support."
                else:
                    return f"I encountered an error while processing your request: {str(openai_error)}"
            
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
    
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