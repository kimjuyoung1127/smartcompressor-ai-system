# 김주영님의 SSH 공개키를 EC2 서버에 추가하는 PowerShell 스크립트
# 사용법: .\add_juyoung_ssh_key.ps1 -SshKeyPath "C:\path\to\your-key.pem"

param(
    [Parameter(Mandatory=$true)]
    [string]$SshKeyPath,
    
    [Parameter(Mandatory=$false)]
    [string]$ServerIp = "3.39.124.0",
    
    [Parameter(Mandatory=$false)]
    [string]$ServerUser = "ubuntu"
)

Write-Host "🔑 김주영님(juyoung@signalcraft)의 SSH 공개키 추가 중..." -ForegroundColor Cyan
Write-Host ""

# SSH 키 파일 존재 확인
if (-not (Test-Path $SshKeyPath)) {
    Write-Host "❌ 오류: SSH 키 파일을 찾을 수 없습니다: $SshKeyPath" -ForegroundColor Red
    exit 1
}

# 김주영님의 SSH 공개키
$PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCpAVjMIt8W7WZg8jhhu7xFqyMIZImoPqjA6L7LcVZJYCT1VA/JEg3U9jbbp5yh1ake8+/nrdJiATkP+f4/ffEx3H/kgvIzTwZVVzkiBpCEWpT8qE39LdQJzernn2t/FXa4nVl7SvgBUEi+yAL1JZ3Kae+gQGEUl/vb/dKSbKYXtkJlGVlVknajZZR0O4xPb/HKa0eQMAT64EveAThEtI03pVDLdktMW0jB1zTMD4QS1CmqQXh04W5PfooERx0CkseoNd6Op9jMnjPdGPwgSsVcXddjfUU/Hl88dIqfpkGPUiOBYDzNDYP2moTsgfkOpGONydzBbEVAGbVfUVYMs6t2KZr40L+4aVeIRxxAlffVqsYh0uAufMtUa1b8ZKXx6d8kGO+jSK+KxwY+sMuoBB8neJI30zYmT9Czf8JGddAa9O7fOvrKZKecIcsSo+YNHMA9ohF3K7J4mqrS83kySiEyp7c2lnyYOGciySME+681OjCD9Xdoxyo2lks9hiOyiFdy1LAD0XaPFI96wCIzd5eIdRMJZLx68jFllciWsOpcFHDTYS9vH6MmOo5WE8M1mgiWVLDRkamixHSKdFdX/WA7miYMtXSuN8ZAFRr4po/9UxRW6ENncoyjps8G0L7CmgEDhC+n9dre85Fv/bwJ9aJ9bnXh1qrheaEEti0dY0d4Nw== juyoung@signalcraft"

# 원격 실행할 스크립트 (Bash 명령어)
$bashScript = @"
# .ssh 디렉토리 확인 및 생성
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# authorized_keys 파일 생성 (없는 경우)
if [ ! -f ~/.ssh/authorized_keys ]; then
    touch ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
fi

# 키가 이미 존재하는지 확인
if grep -Fxq '$PUBLIC_KEY' ~/.ssh/authorized_keys 2>/dev/null; then
    echo '⚠️  경고: 해당 SSH 공개키가 이미 authorized_keys에 존재합니다.'
    exit 0
fi

# 키 추가
echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys

# 권한 설정
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh

# 확인
if grep -Fxq '$PUBLIC_KEY' ~/.ssh/authorized_keys 2>/dev/null; then
    echo '✅ SSH 공개키가 성공적으로 추가되었습니다!'
    echo ''
    echo '📋 추가된 키 정보:'
    echo '   사용자: juyoung@signalcraft'
    echo '   키 타입: ssh-rsa'
    echo ''
    KEY_COUNT=\$(wc -l < ~/.ssh/authorized_keys)
    echo "   총 등록된 키 수: \$KEY_COUNT"
    echo ''
    echo '✨ 김주영님의 SSH 접속 권한이 활성화되었습니다!'
else
    echo '❌ 오류: SSH 공개키 추가에 실패했습니다.'
    exit 1
fi
"@

# SSH를 통해 원격 실행
Write-Host "📡 EC2 서버에 연결 중: $ServerUser@$ServerIp" -ForegroundColor Yellow
Write-Host ""

try {
    # SSH 명령 실행
    $command = "ssh -i `"$SshKeyPath`" -o StrictHostKeyChecking=no $ServerUser@$ServerIp `"$bashScript`""
    
    # Bash 스크립트를 실행
    $result = bash -c "ssh -i `"$SshKeyPath`" -o StrictHostKeyChecking=no $ServerUser@$ServerIp `"$bashScript`""
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host $result -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 SSH 키 추가 완료!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 김주영님이 다음 명령어로 서버에 접속할 수 있습니다:" -ForegroundColor Cyan
        Write-Host "   ssh ubuntu@$ServerIp" -ForegroundColor White
    } else {
        Write-Host "❌ 오류: SSH 키 추가에 실패했습니다." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ 오류 발생: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 대안 방법:" -ForegroundColor Yellow
    Write-Host "1. WSL 또는 Git Bash에서 다음 명령어 실행:" -ForegroundColor White
    Write-Host ""
    $wslCommand = "ssh -i `"$SshKeyPath`" $ServerUser@$ServerIp `"$bashScript`""
    Write-Host $wslCommand -ForegroundColor Gray
    exit 1
}

