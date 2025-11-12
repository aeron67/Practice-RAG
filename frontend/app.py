import streamlit as st
import requests
import os

# Configure Streamlit page
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="📚",
    layout="wide"
)

# Get backend URL from environment or use default
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# Add debug info
st.sidebar.write(f"🔗 Backend URL: {BACKEND_URL}")

def upload_pdf(file):
    """Upload PDF to backend"""
    files = {"file": (file.name, file, "application/pdf")}
    response = requests.post(f"{BACKEND_URL}/upload-pdf", files=files)
    return response

def send_chat_message(message):
    """Send chat message to backend"""
    response = requests.post(
        f"{BACKEND_URL}/chat",
        json={"message": message}
    )
    return response

def get_documents():
    """Get list of uploaded documents"""
    try:
        response = requests.get(f"{BACKEND_URL}/documents")
        if response.status_code == 200:
            return response.json().get("documents", [])
    except:
        pass
    return []

def delete_document(filename):
    """Delete a specific document"""
    try:
        response = requests.delete(f"{BACKEND_URL}/documents/{filename}")
        return response
    except Exception as e:
        return None

def delete_all_documents():
    """Delete all documents"""
    try:
        response = requests.delete(f"{BACKEND_URL}/documents")
        return response
    except Exception as e:
        return None

# Main app
def main():
    st.title("📚 RAG Chatbot")
    st.subheader("Upload PDFs and chat with your documents")
    
    # Sidebar for file upload and document management
    with st.sidebar:
        st.header("📄 Document Management")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload a PDF file",
            type="pdf",
            help="Select a PDF file to upload and process"
        )
        
        if uploaded_file is not None:
            if st.button("Process PDF", type="primary"):
                with st.spinner("Processing PDF..."):
                    try:
                        response = upload_pdf(uploaded_file)
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ {result['message']}")
                            st.info(f"Processed {result['chunks_processed']} text chunks")
                            st.rerun()  # Refresh to update document list
                        else:
                            st.error(f"❌ Error: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Error uploading file: {str(e)}")
        
        # Document list
        st.subheader("📋 Uploaded Documents")
        documents = get_documents()
        if documents:
            # Delete All button
            if st.button("🗑️ Delete All Documents", type="secondary", help="Delete all uploaded documents and their embeddings"):
                if st.session_state.get("confirm_delete_all", False):
                    with st.spinner("Deleting all documents..."):
                        response = delete_all_documents()
                        if response and response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ {result['message']}")
                            st.info(f"Deleted {result.get('deleted_chunks', 0)} chunks")
                            st.session_state.confirm_delete_all = False
                            st.rerun()
                        else:
                            st.error("❌ Error deleting documents")
                else:
                    st.session_state.confirm_delete_all = True
                    st.warning("⚠️ Click again to confirm deletion of ALL documents")
                    st.rerun()
            
            # Individual document delete buttons
            for doc in documents:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"📄 {doc}")
                with col2:
                    if st.button("🗑️", key=f"delete_{doc}", help=f"Delete {doc}"):
                        if st.session_state.get(f"confirm_delete_{doc}", False):
                            with st.spinner(f"Deleting {doc}..."):
                                response = delete_document(doc)
                                if response and response.status_code == 200:
                                    result = response.json()
                                    st.success(f"✅ {result['message']}")
                                    st.session_state[f"confirm_delete_{doc}"] = False
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error deleting {doc}")
                        else:
                            st.session_state[f"confirm_delete_{doc}"] = True
                            st.warning(f"⚠️ Click again to confirm deletion of {doc}")
                            st.rerun()
        else:
            st.write("No documents uploaded yet")
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("💬 Chat Interface")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your documents..."):
            # Check if any documents are uploaded
            if not get_documents():
                st.warning("⚠️ Please upload a PDF document first before asking questions.")
            else:
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Get AI response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            response = send_chat_message(prompt)
                            if response.status_code == 200:
                                ai_response = response.json()["response"]
                                st.markdown(ai_response)
                                # Add assistant response to chat history
                                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                            else:
                                error_msg = f"Error: {response.text}"
                                st.error(error_msg)
                                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        except Exception as e:
                            error_msg = f"Error connecting to backend: {str(e)}"
                            st.error(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    with col2:
        st.header("ℹ️ How to Use")
        st.markdown("""
        1. **Upload PDF**: Use the sidebar to upload a PDF document
        2. **Process**: Click 'Process PDF' to extract and index the content
        3. **Chat**: Ask questions about your document in the chat interface
        4. **Get Answers**: The AI will provide answers based on your document content
        """)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()  