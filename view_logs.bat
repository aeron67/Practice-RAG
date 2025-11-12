@echo off
echo Viewing RAG Chatbot Logs...
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
echo Choose what logs to view:
echo 1. All services
echo 2. Backend only
echo 3. Frontend only
echo 4. PostgreSQL only
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Showing logs for all services...
    echo Press Ctrl+C to stop viewing logs
    echo.
    docker-compose logs -f
) else if "%choice%"=="2" (
    echo.
    echo Showing logs for backend service...
    echo Press Ctrl+C to stop viewing logs
    echo.
    docker-compose logs -f backend
) else if "%choice%"=="3" (
    echo.
    echo Showing logs for frontend service...
    echo Press Ctrl+C to stop viewing logs
    echo.
    docker-compose logs -f frontend
) else if "%choice%"=="4" (
    echo.
    echo Showing logs for PostgreSQL service...
    echo Press Ctrl+C to stop viewing logs
    echo.
    docker-compose logs -f postgres
) else if "%choice%"=="5" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice! Please run the script again.
    pause
    exit /b 1
)

echo.
echo Log viewing stopped.
pause


