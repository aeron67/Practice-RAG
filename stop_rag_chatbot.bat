@echo off
echo Stopping RAG Chatbot Application...
echo.

REM Navigate to the project directory
cd /d "C:\Users\Aeron\Documents\Perso Files\Python\DocuChatAI"

echo Checking if Docker is running...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running or not installed!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo ✅ Docker is running!

echo.
echo Stopping all services...
echo.

REM Stop all services
docker-compose down

if %errorlevel% neq 0 (
    echo ❌ Failed to stop services!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ All services have been stopped!
echo.

REM Show final status
docker-compose ps

echo.
echo 🎉 RAG Chatbot has been stopped successfully!
echo.
echo To start again, run: start_rag_chatbot.bat
echo.
pause


