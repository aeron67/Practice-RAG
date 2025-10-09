@echo off
echo Starting RAG Backend Server...

REM Set the OpenAI API Key
set OPENAI_API_KEY=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

REM Navigate to the project directory
cd /d "C:\Users\Aeron\Documents\Perso Files\Python\DocuChatAI"

REM Start the backend
cd backend
python -m app.main

pause

