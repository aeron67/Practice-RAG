@echo off
setlocal EnableDelayedExpansion
echo Starting RAG Backend Server with Docker...

REM Load environment variables from .env file
if exist .env (
    for /f "usebackq tokens=1,* delims==" %%a in (.env) do (
        set "key=%%a"
        if not "!key!"=="" if not "!key:~0,1!"=="#" (
            set "!key!=%%b"
        )
    )
)

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
echo Starting backend service...
echo.

REM Start only the backend service
docker compose up backend

pause

