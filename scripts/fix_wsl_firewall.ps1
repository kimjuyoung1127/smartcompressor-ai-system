# WSL Flask 서버 방화벽 및 포트 포워딩 설정 스크립트
# Windows PowerShell (관리자 권한)에서 실행하세요

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "WSL Flask Server Access Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 관리자 권한 확인
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script requires administrator privileges." -ForegroundColor Red
    Write-Host "Please run PowerShell as administrator and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host "OK: Administrator privileges confirmed" -ForegroundColor Green
Write-Host ""

# WSL IP 주소 확인
Write-Host "Checking WSL IP address..." -ForegroundColor Yellow
try {
    $wslIP = (wsl ip addr show eth0 | Select-String -Pattern 'inet\s+(\d+\.\d+\.\d+\.\d+)' | ForEach-Object { $_.Matches.Groups[1].Value })
    if (-not $wslIP) {
        $wslIP = (wsl bash -c "hostname -I | awk '{print `$1}'" 2>$null).Trim()
    }
    if (-not $wslIP -or $wslIP -eq "") {
        Write-Host "WARNING: Cannot auto-detect WSL IP address." -ForegroundColor Yellow
        Write-Host "Using default: 172.27.98.13" -ForegroundColor Yellow
        $wslIP = "172.27.98.13"
    } else {
        Write-Host "OK: WSL IP address: $wslIP" -ForegroundColor Green
    }
} catch {
    Write-Host "WARNING: Cannot auto-detect WSL IP address." -ForegroundColor Yellow
    Write-Host "Using default: 172.27.98.13" -ForegroundColor Yellow
    $wslIP = "172.27.98.13"
}
Write-Host ""

# 포트 포워딩 설정
Write-Host "Setting up port forwarding..." -ForegroundColor Yellow
try {
    # 기존 규칙 삭제 (이미 있으면)
    netsh interface portproxy delete v4tov4 listenport=5000 listenaddress=0.0.0.0 2>$null
    
    # 새 규칙 추가
    netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=$wslIP
    
    Write-Host "OK: Port forwarding configured" -ForegroundColor Green
    Write-Host "   localhost:5000 -> $wslIP:5000" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Port forwarding setup failed: $_" -ForegroundColor Red
}
Write-Host ""

# 방화벽 규칙 추가
Write-Host "Adding firewall rule..." -ForegroundColor Yellow
try {
    # 기존 규칙 삭제 (이미 있으면)
    Remove-NetFirewallRule -DisplayName "WSL Flask Server" -ErrorAction SilentlyContinue
    
    # 새 규칙 추가
    New-NetFirewallRule -DisplayName "WSL Flask Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
    
    Write-Host "OK: Firewall rule added" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Firewall rule addition failed: $_" -ForegroundColor Red
}
Write-Host ""

# 설정 확인
Write-Host "Current port forwarding settings:" -ForegroundColor Yellow
netsh interface portproxy show all
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now access the server from your browser:" -ForegroundColor Green
$url1 = 'http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html'
Write-Host "  $url1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or access directly using WSL IP:" -ForegroundColor Green
$url2 = "http://${wslIP}:5000/static/dashboard-components/esp32-realtime-monitor.html"
Write-Host "  $url2" -ForegroundColor Cyan
Write-Host ""
