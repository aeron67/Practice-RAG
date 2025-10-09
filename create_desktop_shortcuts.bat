@echo off
echo Creating Desktop Shortcuts for RAG Chatbot...

REM Get the current directory (where the scripts are located)
set "SCRIPT_DIR=%~dp0"

REM Get the desktop path
set "DESKTOP=%USERPROFILE%\Desktop"

REM Create shortcut for the main startup script
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\RAG Chatbot.lnk'); $Shortcut.TargetPath = '%SCRIPT_DIR%start_rag_chatbot.bat'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Description = 'Start RAG Chatbot Application'; $Shortcut.Save()"

REM Create shortcut for backend only
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\RAG Backend.lnk'); $Shortcut.TargetPath = '%SCRIPT_DIR%start_backend.bat'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Description = 'Start RAG Backend Server'; $Shortcut.Save()"

REM Create shortcut for frontend only
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\RAG Frontend.lnk'); $Shortcut.TargetPath = '%SCRIPT_DIR%start_frontend.bat'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Description = 'Start RAG Frontend Server'; $Shortcut.Save()"

echo.
echo ✅ Desktop shortcuts created successfully!
echo.
echo You now have these shortcuts on your desktop:
echo - RAG Chatbot (starts both services)
echo - RAG Backend (starts backend only)
echo - RAG Frontend (starts frontend only)
echo.
pause

