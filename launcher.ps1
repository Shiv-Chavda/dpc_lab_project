# PowerShell launcher for Distributed Chat Application

function Show-Menu {
    Clear-Host
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "  DISTRIBUTED CHAT APPLICATION - LAUNCHER" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "What would you like to do?" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1. Start Server" -ForegroundColor Green
    Write-Host "  2. Start Console Client" -ForegroundColor Green
    Write-Host "  3. Start GUI Client" -ForegroundColor Green
    Write-Host "  4. Run Tests" -ForegroundColor Green
    Write-Host "  5. View Quick Start Guide" -ForegroundColor Green
    Write-Host "  6. Exit" -ForegroundColor Red
    Write-Host ""
}

function Start-Server {
    Write-Host ""
    Write-Host "Starting server..." -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    python server.py
}

function Start-ConsoleClient {
    Write-Host ""
    Write-Host "Starting console client..." -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    python client_console.py
}

function Start-GUIClient {
    Write-Host ""
    Write-Host "Starting GUI client..." -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    python client_gui.py
}

function Run-Tests {
    Write-Host ""
    Write-Host "Running test suite..." -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    python test_suite.py
    Write-Host ""
    Pause
}

function Show-QuickStart {
    Write-Host ""
    Write-Host "Opening Quick Start Guide..." -ForegroundColor Cyan
    Get-Content QUICKSTART.md | Write-Host
    Write-Host ""
    Pause
}

# Main loop
do {
    Show-Menu
    $choice = Read-Host "Enter your choice (1-6)"
    
    switch ($choice) {
        '1' { Start-Server }
        '2' { Start-ConsoleClient }
        '3' { Start-GUIClient }
        '4' { Run-Tests }
        '5' { Show-QuickStart }
        '6' { 
            Write-Host ""
            Write-Host "Goodbye!" -ForegroundColor Green
            break 
        }
        default {
            Write-Host ""
            Write-Host "Invalid choice! Please try again." -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
} while ($choice -ne '6')
