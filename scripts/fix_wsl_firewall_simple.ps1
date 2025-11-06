# WSL Flask Server Firewall Setup (Simple Version)
# Run as Administrator in PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "WSL Flask Server Access Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check admin privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Administrator privileges required" -ForegroundColor Red
    Write-Host "Please run PowerShell as administrator" -ForegroundColor Yellow
    exit 1
}

Write-Host "OK: Administrator privileges confirmed" -ForegroundColor Green
Write-Host ""

# Get WSL IP address (alternative method)
Write-Host "Getting WSL IP address..." -ForegroundColor Yellow
try {
    $wslIP = (wsl bash -c "ip addr show eth0 | grep 'inet ' | awk '{print `$2}' | cut -d/ -f1").Trim()
    if (-not $wslIP) {
        $wslIP = (wsl bash -c "hostname -i").Trim()
    }
    if (-not $wslIP -or $wslIP -eq "") {
        throw "Cannot get IP"
    }
    Write-Host "OK: WSL IP: $wslIP" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Cannot auto-detect WSL IP" -ForegroundColor Yellow
    Write-Host "Please enter your WSL IP address (or press Enter to use default 172.27.98.13):" -ForegroundColor Yellow
    $inputIP = Read-Host
    if ($inputIP -and $inputIP -ne "") {
        $wslIP = $inputIP
    } else {
        $wslIP = "172.27.98.13"
    }
    Write-Host "Using WSL IP: $wslIP" -ForegroundColor Green
}
Write-Host ""

# Port forwarding
Write-Host "Setting up port forwarding..." -ForegroundColor Yellow
try {
    netsh interface portproxy delete v4tov4 listenport=5000 listenaddress=0.0.0.0 2>$null
    netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=$wslIP
    Write-Host "OK: Port forwarding configured" -ForegroundColor Green
    Write-Host "   localhost:5000 -> $wslIP:5000" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Port forwarding failed: $_" -ForegroundColor Red
}
Write-Host ""

# Firewall rule
Write-Host "Adding firewall rule..." -ForegroundColor Yellow
try {
    Remove-NetFirewallRule -DisplayName "WSL Flask Server" -ErrorAction SilentlyContinue
    New-NetFirewallRule -DisplayName "WSL Flask Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
    Write-Host "OK: Firewall rule added" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Firewall rule failed: $_" -ForegroundColor Red
}
Write-Host ""

# Show settings
Write-Host "Port forwarding settings:" -ForegroundColor Yellow
netsh interface portproxy show all
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Green
Write-Host "  http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html" -ForegroundColor Cyan
Write-Host "  http://$wslIP:5000/static/dashboard-components/esp32-realtime-monitor.html" -ForegroundColor Cyan
Write-Host ""

