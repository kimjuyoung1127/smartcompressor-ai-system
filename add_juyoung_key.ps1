# 김주영님 SSH 키 추가 - PowerShell 스크립트
$WindowsKeyPath = "C:\Signal_craft\음원라벨링도구\compressor-ai-diagnosis\src\signalcraft-new.pem"
$WslKeyPath = "/mnt/c/Signal_craft/음원라벨링도구/compressor-ai-diagnosis/src/signalcraft-new.pem"

Write-Host "🔍 SSH 키 파일 확인 중..." -ForegroundColor Cyan
Write-Host "   Windows 경로: $WindowsKeyPath" -ForegroundColor Gray
Write-Host "   WSL 경로: $WslKeyPath" -ForegroundColor Gray
Write-Host ""

# 키 파일 확인 (Windows 경로 우선, 없으면 WSL에서 확인)
$fileExists = Test-Path $WindowsKeyPath

if (-not $fileExists) {
    Write-Host "⚠️  Windows 경로에서 키 파일을 찾을 수 없습니다." -ForegroundColor Yellow
    Write-Host "   WSL에서 직접 실행합니다..." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "✅ 키 파일 확인 완료!" -ForegroundColor Green
    Write-Host ""
}
Write-Host ""
Write-Host "🚀 WSL에서 SSH 키 추가 스크립트 실행 중..." -ForegroundColor Cyan
Write-Host ""

# WSL에서 스크립트 실행 (경로를 따옴표로 감싸서 한글 경로 처리)
$wslCommand = "cd ~/smartcompressor-ai-system; chmod +x quick_add_ssh_key.sh 2>/dev/null; ./quick_add_ssh_key.sh '$WslKeyPath'"

Write-Host "📡 WSL에서 SSH 키 추가 스크립트 실행 중..." -ForegroundColor Cyan
Write-Host ""

wsl bash -c $wslCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 SSH 키 추가가 완료되었습니다!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✨ 김주영님은 이제 다음 명령어로 서버에 접속할 수 있습니다:" -ForegroundColor Cyan
    Write-Host "   ssh ubuntu@3.39.124.0" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ 오류가 발생했습니다. (종료 코드: $LASTEXITCODE)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 문제 해결 방법:" -ForegroundColor Yellow
    Write-Host "   1. WSL에서 직접 실행해보세요:" -ForegroundColor White
    Write-Host "      wsl" -ForegroundColor Gray
    Write-Host "      cd ~/smartcompressor-ai-system" -ForegroundColor Gray
    Write-Host "      ./quick_add_ssh_key.sh $WslKeyPath" -ForegroundColor Gray
}

