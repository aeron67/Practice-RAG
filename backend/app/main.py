import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from .pdf_loader import PDFLoader
from .embeddings_sqlite import EmbeddingManager
from .chat import ChatManager

app = FastAPI(title="RAG Chatbot API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
pdf_loader = PDFLoader()
embedding_manager = EmbeddingManager()
chat_manager = ChatManager(embedding_manager)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "RAG Chatbot API is running"}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Read file content
        content = await file.read()
        
        # Extract text from PDF
        text_chunks = pdf_loader.extract_text_from_pdf(content, file.filename)
        
        # Generate and store embeddings
        embedding_manager.store_document_embeddings(text_chunks, file.filename)
        
        return {
            "message": f"PDF '{file.filename}' processed successfully",
            "chunks_processed": len(text_chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat with the RAG system"""
    try:
        response = chat_manager.get_response(request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/documents")
async def list_documents():
    """List all processed documents"""
    try:
        documents = embedding_manager.get_document_list()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a specific document and its embeddings"""
    try:
        success = embedding_manager.delete_document(filename)
        if success:
            return {"message": f"Document '{filename}' deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Document '{filename}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@app.delete("/documents")
async def delete_all_documents():
    """Delete all documents and their embeddings"""
    try:
        deleted_count = embedding_manager.delete_all_documents()
        return {"message": f"All documents deleted successfully", "deleted_chunks": deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting all documents: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)