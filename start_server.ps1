$env:FLASK_PORT=5001
cd backend
$process = Start-Process python -ArgumentList "app.py" -PassThru -NoNewWindow -RedirectStandardOutput "server.log" -RedirectStandardError "server.log"
$process.Id | Out-File "flask.pid" -Encoding ASCII
Write-Host "Flask server started with PID $($process.Id) on port 5001"
Write-Host "Logs: backend/server.log"
Start-Sleep -Seconds 2
try {
    $html = Invoke-WebRequest "http://localhost:5001/" -UseBasicParsing | Select-Object -ExpandProperty Content
    if ($html -match "card-euro") {
        Write-Host "SUCCESS: Euro card found in frontend" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Euro card not found in HTML" -ForegroundColor Yellow
    }
    if ($html -match "euroCompra") {
        Write-Host "SUCCESS: euroCompra element found" -ForegroundColor Green
    }
    if ($html -match "euroVenta") {
        Write-Host "SUCCESS: euroVenta element found" -ForegroundColor Green
    }
    Write-Host "Frontend served successfully"
} catch {
    Write-Host "Error fetching frontend: $_" -ForegroundColor Red
}
Write-Host "Server is running. To stop: Stop-Process -Id $($process.Id) -Force"