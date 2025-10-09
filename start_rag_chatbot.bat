@echo off
echo Starting RAG Chatbot Application...
echo.

REM Set the OpenAI API Key for this session
set OPENAI_API_KEY=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

REM Navigate to the project directory
cd /d "C:\Users\Aeron\Documents\Perso Files\Python\DocuChatAI"

echo Starting Backend Server...
start "RAG Backend" cmd /k "cd backend && python -m app.main"

REM Wait a few seconds for backend to start
timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
start "RAG Frontend" cmd /k "streamlit run frontend/app.py --server.port 8508"

echo.
echo ✅ RAG Chatbot is starting up!
echo.
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:8508
echo.
echo Press any key to open the frontend in your browser...
pause > nul

REM Open the frontend in the default browser
start http://localhost:8508

echo.
echo 🎉 RAG Chatbot is now running!
echo.
echo To stop the application:
echo 1. Close both command windows that opened
echo 2. Or press Ctrl+C in each window
echo.
pause

