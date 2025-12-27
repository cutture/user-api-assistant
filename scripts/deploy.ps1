
<#
.SYNOPSIS
    Simple Deployment Helper for Windows
.DESCRIPTION
    Usage: .\deploy.ps1 -Env prod
#>

param (
    [string]$Env = "dev"
)

Write-Host "🚀 Deploying to Environment: $Env" -ForegroundColor Cyan

if ($Env -eq "prod") {
    $env:NEXT_PUBLIC_API_URL = "https://api.yourdomain.com"
}
elseif ($Env -eq "qa") {
    $env:NEXT_PUBLIC_API_URL = "http://your-qa-ip:8000"
}
else {
    # Dev
    $env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
}

Write-Host "   API URL: $env:NEXT_PUBLIC_API_URL"

# Build and Run
Write-Host "📦 Building containers..." -ForegroundColor Yellow
docker-compose up -d --build --remove-orphans

# Health Check
Write-Host "🩺 Waiting for service..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Get -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Deployment Successful! Backend is healthy." -ForegroundColor Green
    }
}
catch {
    Write-Host "⚠️ Deployment completed, but Health Check failed. Please check logs." -ForegroundColor Red
    Write-Host $_.Exception.Message
}
