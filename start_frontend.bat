@echo off
echo Starting RAG Frontend Server with Docker...

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
echo Starting frontend service...
echo.

REM Start only the frontend service
docker compose up frontend

pause

