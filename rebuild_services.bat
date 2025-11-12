@echo off
echo Rebuilding RAG Chatbot Services...
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
echo Stopping existing services...
docker-compose down

echo.
echo Rebuilding and starting services...
echo This may take a few minutes...
echo.

REM Rebuild and start all services
docker-compose up --build -d

if %errorlevel% neq 0 (
    echo ❌ Failed to rebuild services!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ Services have been rebuilt and started!
echo.

REM Wait for services to be healthy
echo Waiting for services to be ready...
timeout /t 10 /nobreak > nul

REM Check if services are running
docker-compose ps

echo.
echo 🎉 RAG Chatbot has been rebuilt and is running!
echo.
echo 📍 Access your application:
echo   • Frontend: http://localhost:8501
echo   • Backend API: http://localhost:8000
echo   • PostgreSQL: localhost:5432
echo.
pause


