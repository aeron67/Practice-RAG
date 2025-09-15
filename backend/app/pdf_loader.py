import io
from typing import List
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFLoader:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_content: bytes, filename: str) -> List[dict]:
        """Extract text from PDF and split into chunks"""
        try:
            # Create a file-like object from bytes
            pdf_file = io.BytesIO(pdf_content)
            
            # Read PDF using pypdf
            reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            full_text = ""
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                full_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(full_text)
            
            # Create chunk objects with metadata
            text_chunks = []
            for i, chunk in enumerate(chunks):
                text_chunks.append({
                    "content": chunk,
                    "metadata": {
                        "filename": filename,
                        "chunk_id": i,
                        "total_chunks": len(chunks)
                    }
                })
            
            return text_chunks
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")