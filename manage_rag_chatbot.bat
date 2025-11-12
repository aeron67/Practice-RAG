@echo off
title RAG Chatbot Management
color 0A

:menu
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    RAG Chatbot Management                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Choose an option:
echo.
echo 1. 🚀 Start All Services
echo 2. 🛑 Stop All Services
echo 3. 🔄 Restart All Services
echo 4. 🔨 Rebuild All Services
echo 5. 📊 View Service Status
echo 6. 📋 View Logs
echo 7. 🗑️  Clean Up (Remove containers and volumes)
echo 8. 🌐 Open Frontend in Browser
echo 9. 🔧 Open Backend API Documentation
echo 0. ❌ Exit
echo.

set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" (
    call start_rag_chatbot.bat
    goto menu
) else if "%choice%"=="2" (
    call stop_rag_chatbot.bat
    goto menu
) else if "%choice%"=="3" (
    echo.
    echo Restarting all services...
    docker-compose restart
    echo.
    echo ✅ Services restarted!
    pause
    goto menu
) else if "%choice%"=="4" (
    call rebuild_services.bat
    goto menu
) else if "%choice%"=="5" (
    echo.
    echo Current service status:
    echo.
    docker-compose ps
    echo.
    pause
    goto menu
) else if "%choice%"=="6" (
    call view_logs.bat
    goto menu
) else if "%choice%"=="7" (
    echo.
    echo ⚠️  WARNING: This will remove all containers and data!
    echo Are you sure you want to continue? (y/N)
    set /p confirm=
    if /i "%confirm%"=="y" (
        echo.
        echo Cleaning up...
        docker-compose down -v
        docker system prune -f
        echo.
        echo ✅ Cleanup completed!
    ) else (
        echo Cleanup cancelled.
    )
    pause
    goto menu
) else if "%choice%"=="8" (
    echo.
    echo Opening frontend in browser...
    start http://localhost:8501
    echo.
    echo ✅ Frontend opened in browser!
    pause
    goto menu
) else if "%choice%"=="9" (
    echo.
    echo Opening backend API documentation...
    start http://localhost:8000/docs
    echo.
    echo ✅ API documentation opened in browser!
    pause
    goto menu
) else if "%choice%"=="0" (
    echo.
    echo Goodbye! 👋
    exit /b 0
) else (
    echo.
    echo ❌ Invalid choice! Please try again.
    pause
    goto menu
)


