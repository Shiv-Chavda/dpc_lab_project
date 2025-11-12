@echo off
REM Quick launcher for Distributed Chat Application
REM This script helps you start server and clients easily

echo ============================================================
echo   DISTRIBUTED CHAT APPLICATION - LAUNCHER
echo ============================================================
echo.
echo What would you like to do?
echo.
echo   1. Start Server
echo   2. Start Console Client
echo   3. Start GUI Client
echo   4. Run Tests
echo   5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto server
if "%choice%"=="2" goto console
if "%choice%"=="3" goto gui
if "%choice%"=="4" goto tests
if "%choice%"=="5" goto end

echo Invalid choice!
pause
goto end

:server
echo.
echo Starting server...
echo ============================================================
python server.py
goto end

:console
echo.
echo Starting console client...
echo ============================================================
python client_console.py
goto end

:gui
echo.
echo Starting GUI client...
echo ============================================================
python client_gui.py
goto end

:tests
echo.
echo Running test suite...
echo ============================================================
python test_suite.py
echo.
pause
goto end

:end
