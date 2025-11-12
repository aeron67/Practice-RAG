@echo off
echo Starting RAG Chatbot Application with Docker...
echo.

REM Load environment variables from .env file
if exist .env (
    for /f "usebackq tokens=1,2 delims==" %%a in (.env) do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" set "%%a=%%b"
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
echo Starting all services with Docker Compose...
echo This may take a few minutes on first run...
echo.

REM Start all services with Docker Compose
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start services!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ All services are starting up!
echo.

REM Wait for services to be healthy
echo Waiting for services to be ready...
timeout /t 10 /nobreak > nul

REM Check if services are running
docker-compose ps

echo.
echo 🎉 RAG Chatbot is now running!
echo.
echo 📍 Access your application:
echo   • Frontend: http://localhost:8501
echo   • Backend API: http://localhost:8000
echo   • PostgreSQL: localhost:5432
echo.
echo Press any key to open the frontend in your browser...
pause > nul

REM Open the frontend in the default browser
start http://localhost:8501

echo.
echo 📋 Useful commands:
echo   • View logs: docker-compose logs -f
echo   • Stop services: docker-compose down
echo   • Restart services: docker-compose restart
echo   • View status: docker-compose ps
echo.
echo Press any key to exit...
pause

