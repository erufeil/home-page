$env:FLASK_PORT=5000
cd backend
Start-Job -ScriptBlock {
    python app.py
} | Out-Null
Start-Sleep -Seconds 3
Write-Host "Flask server started on port 5000"
Write-Host "Open http://localhost:5000/ in your browser"