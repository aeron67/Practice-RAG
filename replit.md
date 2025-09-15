# RAG Chatbot

## Overview

This is a Retrieval-Augmented Generation (RAG) chatbot application that allows users to upload PDF documents and chat with their contents using natural language queries. The system extracts text from PDFs, creates embeddings for semantic search, and uses OpenAI's GPT models to generate contextually relevant responses based on the document content.

The application follows a microservices architecture with a clear separation between frontend and backend components, enabling scalable document processing and intelligent question-answering capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application providing an intuitive user interface
- **Design Pattern**: Single-page application with sidebar navigation
- **Communication**: RESTful API calls to backend services
- **Features**: PDF upload interface, chat interface, and document management

### Backend Architecture
- **Framework**: FastAPI for high-performance REST API endpoints
- **Design Pattern**: Modular component-based architecture with separation of concerns
- **Core Components**:
  - `PDFLoader`: Handles PDF text extraction with robust error handling and text chunking
  - `EmbeddingManager`: Manages vector embeddings storage and similarity search
  - `ChatManager`: Orchestrates RAG pipeline with OpenAI integration
- **Text Processing**: Uses LangChain's RecursiveCharacterTextSplitter for intelligent document chunking
- **Error Handling**: Comprehensive validation and fallback mechanisms for PDF processing

### Data Storage
- **Primary Database**: PostgreSQL with vector similarity search capabilities
- **Vector Storage**: Embeddings stored directly in PostgreSQL using psycopg2 driver
- **Connection Management**: SQLAlchemy engine with connection pooling and SSL requirements
- **Data Model**: Document chunks stored with embeddings, metadata, and source references

### AI/ML Pipeline
- **Embedding Model**: OpenAI's text-embedding-3-small for semantic vector representations
- **LLM**: Configurable OpenAI models (default: gpt-4o-mini) for response generation
- **RAG Implementation**: Similarity search retrieval combined with prompt engineering for contextual responses
- **Search Strategy**: Top-k similarity search (k=5) for relevant document chunk retrieval

## External Dependencies

### Core AI Services
- **OpenAI API**: Primary AI service for both embeddings and chat completions
  - Text embeddings via text-embedding-3-small model
  - Chat completions via configurable GPT models
  - Requires OPENAI_API_KEY environment variable

### Database Services
- **PostgreSQL**: Vector database for embeddings and document storage
  - Requires DATABASE_URL environment variable
  - SSL connection required for security
  - Vector similarity search capabilities

### Python Libraries
- **FastAPI**: Modern web framework for building APIs
- **Streamlit**: Frontend framework for rapid web app development
- **LangChain**: AI application framework for RAG implementation
- **pypdf**: PDF text extraction and processing
- **psycopg2**: PostgreSQL database adapter
- **SQLAlchemy**: Database ORM and connection management
- **requests**: HTTP client for frontend-backend communication

### Development and Deployment
- **uvicorn**: ASGI server for FastAPI application
- **CORS**: Cross-origin resource sharing for frontend-backend communication
- **Environment Variables**: Configuration management for API keys and database connections