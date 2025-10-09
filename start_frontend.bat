@echo off
echo Starting RAG Frontend Server...

REM Navigate to the project directory
cd /d "C:\Users\Aeron\Documents\Perso Files\Python\DocuChatAI"

REM Start the frontend
streamlit run "frontend/app.py" --server.port 8508

pause

