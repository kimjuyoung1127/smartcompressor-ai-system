# 간단한 방화벽 설정 스크립트
# Windows PowerShell (관리자 권한)에서 실행하세요

Write-Host "Setting up WSL Flask Server firewall..." -ForegroundColor Cyan
Write-Host ""

# 방화벽 규칙 추가
Write-Host "Adding firewall rule..." -ForegroundColor Yellow
try {
    Remove-NetFirewallRule -DisplayName "WSL Flask Server" -ErrorAction SilentlyContinue
    New-NetFirewallRule -DisplayName "WSL Flask Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
    Write-Host "OK: Firewall rule added" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Yellow
Write-Host "  http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html" -ForegroundColor Cyan
Write-Host "  http://172.27.98.13:5000/static/dashboard-components/esp32-realtime-monitor.html" -ForegroundColor Cyan
Write-Host ""

