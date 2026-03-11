$env:FLASK_PORT=5001
cd backend
$process = Start-Process python -ArgumentList "app.py" -PassThru -NoNewWindow
Start-Sleep -Seconds 3
try {
    $response = Invoke-RestMethod "http://localhost:5001/api/data" -ErrorAction Stop
    Write-Host "API Response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
    Write-Host "Test passed!" -ForegroundColor Green
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
} finally {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
}