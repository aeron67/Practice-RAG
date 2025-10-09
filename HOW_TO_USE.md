# 🚀 RAG Chatbot - How to Use After Restart

Your RAG Chatbot is now set up to work regularly, even after restarting your PC! Here are all the ways you can start it:

## 🖥️ **Easy Ways to Start (Recommended)**

### **Option 1: Desktop Shortcuts** ⭐
- Look on your desktop for these shortcuts:
  - **"RAG Chatbot"** - Starts both backend and frontend automatically
  - **"RAG Backend"** - Starts only the backend server
  - **"RAG Frontend"** - Starts only the frontend server

### **Option 2: Batch Files**
- Double-click any of these files in your project folder:
  - `start_rag_chatbot.bat` - Starts both services
  - `start_backend.bat` - Starts backend only
  - `start_frontend.bat` - Starts frontend only

### **Option 3: PowerShell Script**
- Right-click `start_rag_chatbot.ps1` and select "Run with PowerShell"

## 🌐 **Access Your Application**

Once started, open your web browser and go to:
- **Frontend**: http://localhost:8508
- **Backend API**: http://localhost:8000

## 📋 **What Each Service Does**

- **Backend (Port 8000)**: Handles PDF processing, embeddings, and chat responses
- **Frontend (Port 8508)**: Web interface for uploading PDFs and chatting

## 🔧 **Troubleshooting**

### If services don't start:
1. Make sure Python is installed and accessible
2. Check that all dependencies are installed: `pip install -r requirements.txt`
3. Verify the OpenAI API key is set in the batch files

### If you get port errors:
- The scripts use ports 8000 (backend) and 8508 (frontend)
- If these ports are busy, close other applications using them

### If PDF upload fails:
- Make sure the backend is running first
- Check that the OpenAI API key is valid and has credits

## 🎯 **Quick Start Guide**

1. **Double-click "RAG Chatbot" on your desktop**
2. **Wait for both windows to open** (backend and frontend)
3. **Open your browser** and go to http://localhost:8508
4. **Upload a PDF** using the sidebar
5. **Click "Process PDF"** to index the content
6. **Start chatting** with your document!

## 🔄 **Stopping the Application**

- **Close both command windows** that opened
- **Or press Ctrl+C** in each window

## 📁 **File Locations**

All startup scripts are in your project folder:
```
C:\Users\Aeron\Documents\Perso Files\Python\DocuChatAI\
├── start_rag_chatbot.bat      (Main startup script)
├── start_backend.bat          (Backend only)
├── start_frontend.bat         (Frontend only)
├── start_rag_chatbot.ps1      (PowerShell version)
└── create_desktop_shortcuts.bat (Creates desktop shortcuts)
```

## ✨ **Pro Tips**

- The main `start_rag_chatbot.bat` will automatically open your browser
- You can run backend and frontend separately if needed
- The OpenAI API key is embedded in the scripts for convenience
- All scripts include error handling and helpful messages

**Happy chatting with your documents! 📚🤖**

