import io
import logging
from typing import List, Optional
from pypdf import PdfReader
from pypdf.errors import PdfReadError, FileNotDecryptedError
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFLoader:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        self.min_text_length = 50  # Minimum text length to consider valid
    
    def _validate_pdf_content(self, pdf_content: bytes, filename: str) -> None:
        """Validate PDF content before processing"""
        if not pdf_content:
            raise ValueError(f"Empty PDF content for file: {filename}")
        
        if len(pdf_content) < 100:  # PDFs are typically much larger
            raise ValueError(f"PDF file appears to be too small or corrupted: {filename}")
        
        # Check for PDF header
        if not pdf_content.startswith(b'%PDF-'):
            raise ValueError(f"Invalid PDF format - missing PDF header: {filename}")
    
    def _extract_page_text_robust(self, page, page_num: int) -> Optional[str]:
        """Robustly extract text from a single page with multiple fallback methods"""
        try:
            # Primary extraction method
            text = page.extract_text()
            
            # Handle None or empty text
            if text is None:
                logger.warning(f"Page {page_num + 1}: extract_text() returned None, trying alternative extraction")
                text = ""
            
            # Clean up the text
            text = text.strip() if text else ""
            
            # Try alternative extraction if primary method failed
            if not text:
                try:
                    # Try extracting with different parameters
                    text = page.extract_text(extraction_mode="layout")
                    if text:
                        text = text.strip()
                        logger.info(f"Page {page_num + 1}: Successfully extracted text using layout mode")
                except Exception:
                    logger.warning(f"Page {page_num + 1}: Layout mode extraction also failed")
                    text = ""
            
            # If still no text, try to get text from annotations or forms
            if not text:
                try:
                    if '/Annots' in page:
                        logger.info(f"Page {page_num + 1}: Attempting to extract text from annotations")
                        # This is a basic attempt - more complex annotation parsing could be added
                        text = "[Page contains annotations or forms but text extraction failed]"
                except Exception:
                    pass
            
            return text if text else None
            
        except Exception as e:
            logger.error(f"Error extracting text from page {page_num + 1}: {str(e)}")
            return None
    
    def extract_text_from_pdf(self, pdf_content: bytes, filename: str) -> List[dict]:
        """Extract text from PDF and split into chunks with robust error handling"""
        try:
            # Validate PDF content
            self._validate_pdf_content(pdf_content, filename)
            
            # Create a file-like object from bytes
            pdf_file = io.BytesIO(pdf_content)
            
            # Read PDF using pypdf with error handling
            try:
                reader = PdfReader(pdf_file)
            except FileNotDecryptedError:
                raise ValueError(f"PDF is password-protected and cannot be read: {filename}")
            except PdfReadError as e:
                raise ValueError(f"PDF is corrupted or invalid: {filename}. Error: {str(e)}")
            
            # Check if PDF has pages
            if not reader.pages:
                raise ValueError(f"PDF has no readable pages: {filename}")
            
            logger.info(f"Processing PDF '{filename}' with {len(reader.pages)} pages")
            
            # Extract text from all pages with robust handling
            full_text = ""
            successful_pages = 0
            failed_pages = 0
            
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = self._extract_page_text_robust(page, page_num)
                    
                    if page_text is not None:
                        # Only add page separator if we have text
                        if page_text.strip():
                            full_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                            successful_pages += 1
                        else:
                            logger.warning(f"Page {page_num + 1}: Contains only whitespace")
                    else:
                        failed_pages += 1
                        logger.warning(f"Page {page_num + 1}: Failed to extract any text")
                        # Add a placeholder for failed pages
                        full_text += f"\n--- Page {page_num + 1} ---\n[Text extraction failed for this page]"
                        
                except Exception as e:
                    failed_pages += 1
                    logger.error(f"Error processing page {page_num + 1}: {str(e)}")
                    full_text += f"\n--- Page {page_num + 1} ---\n[Error processing this page: {str(e)}]"
            
            logger.info(f"PDF processing complete: {successful_pages} successful, {failed_pages} failed pages")
            
            # Validate that we extracted some meaningful text
            clean_text = full_text.strip()
            if not clean_text or len(clean_text) < self.min_text_length:
                if failed_pages == len(reader.pages):
                    raise ValueError(f"Could not extract any readable text from PDF: {filename}")
                else:
                    logger.warning(f"Extracted text is very short ({len(clean_text)} chars) from PDF: {filename}")
            
            # Split text into chunks
            try:
                chunks = self.text_splitter.split_text(full_text)
            except Exception as e:
                logger.error(f"Error splitting text into chunks: {str(e)}")
                # Fallback: create a single chunk
                chunks = [full_text]
            
            # Filter out empty chunks
            valid_chunks = [chunk for chunk in chunks if chunk.strip()]
            
            if not valid_chunks:
                raise ValueError(f"No valid text chunks could be created from PDF: {filename}")
            
            # Create chunk objects with metadata
            text_chunks = []
            for i, chunk in enumerate(valid_chunks):
                text_chunks.append({
                    "content": chunk,
                    "metadata": {
                        "filename": filename,
                        "chunk_id": i,
                        "total_chunks": len(valid_chunks),
                        "successful_pages": successful_pages,
                        "failed_pages": failed_pages,
                        "total_pages": len(reader.pages)
                    }
                })
            
            logger.info(f"Successfully created {len(text_chunks)} text chunks from PDF: {filename}")
            return text_chunks
            
        except ValueError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            error_msg = f"Unexpected error extracting text from PDF '{filename}': {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)