# RAG Chatbot Startup Script
Write-Host "Starting RAG Chatbot Application..." -ForegroundColor Green
Write-Host ""

# Set the OpenAI API Key
$env:OPENAI_API_KEY = "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"

# Navigate to the project directory
$projectPath = "C:\Users\Aeron\Documents\Perso Files\Python\DocuChatAI"
Set-Location $projectPath

Write-Host "Starting Backend Server..." -ForegroundColor Yellow
# Start backend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath\backend'; `$env:OPENAI_API_KEY='$env:OPENAI_API_KEY'; python -m app.main"

# Wait for backend to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
# Start frontend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; streamlit run 'frontend/app.py' --server.port 8508"

Write-Host ""
Write-Host "✅ RAG Chatbot is starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend will be available at: http://localhost:8508" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening frontend in your browser..." -ForegroundColor Yellow

# Wait a moment then open the frontend
Start-Sleep -Seconds 3
Start-Process "http://localhost:8508"

Write-Host ""
Write-Host "🎉 RAG Chatbot is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "To stop the application, close the PowerShell windows that opened." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit this startup script"

