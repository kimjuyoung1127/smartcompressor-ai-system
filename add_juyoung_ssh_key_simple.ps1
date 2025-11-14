# 간단한 원라인 명령어 버전
# 김주영님의 SSH 공개키를 EC2 서버에 추가

param(
    [Parameter(Mandatory=$true)]
    [string]$SshKeyPath,
    
    [Parameter(Mandatory=$false)]
    [string]$ServerIp = "3.39.124.0",
    
    [Parameter(Mandatory=$false)]
    [string]$ServerUser = "ubuntu"
)

$PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCpAVjMIt8W7WZg8jhhu7xFqyMIZImoPqjA6L7LcVZJYCT1VA/JEg3U9jbbp5yh1ake8+/nrdJiATkP+f4/ffEx3H/kgvIzTwZVVzkiBpCEWpT8qE39LdQJzernn2t/FXa4nVl7SvgBUEi+yAL1JZ3Kae+gQGEUl/vb/dKSbKYXtkJlGVlVknajZZR0O4xPb/HKa0eQMAT64EveAThEtI03pVDLdktMW0jB1zTMD4QS1CmqQXh04W5PfooERx0CkseoNd6Op9jMnjPdGPwgSsVcXddjfUU/Hl88dIqfpkGPUiOBYDzNDYP2moTsgfkOpGONydzBbEVAGbVfUVYMs6t2KZr40L+4aVeIRxxAlffVqsYh0uAufMtUa1b8ZKXx6d8kGO+jSK+KxwY+sMuoBB8neJI30zYmT9Czf8JGddAa9O7fOvrKZKecIcsSo+YNHMA9ohF3K7J4mqrS83kySiEyp7c2lnyYOGciySME+681OjCD9Xdoxyo2lks9hiOyiFdy1LAD0XaPFI96wCIzd5eIdRMJZLx68jFllciWsOpcFHDTYS9vH6MmOo5WE8M1mgiWVLDRkamixHSKdFdX/WA7miYMtXSuN8ZAFRr4po/9UxRW6ENncoyjps8G0L7CmgEDhC+n9dre85Fv/bwJ9aJ9bnXh1qrheaEEti0dY0d4Nw== juyoung@signalcraft"

Write-Host "🔑 SSH 키 추가 중..." -ForegroundColor Cyan

# 원격 실행할 스크립트 작성
$bashScript = @"
mkdir -p ~/.ssh && chmod 700 ~/.ssh
if [ ! -f ~/.ssh/authorized_keys ]; then touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys; fi
if ! grep -Fxq '$PUBLIC_KEY' ~/.ssh/authorized_keys 2>/dev/null; then
    echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    echo '✅ SSH 키 추가 완료!'
else
    echo '⚠️  키가 이미 존재합니다.'
fi
KEY_COUNT=$(wc -l < ~/.ssh/authorized_keys)
echo "📊 총 등록된 키 수: $KEY_COUNT"
"@

# SSH 명령 실행
Write-Host "📡 서버에 연결 중: $ServerUser@$ServerIp" -ForegroundColor Yellow

# WSL이나 bash를 통해 실행 시도
if (Get-Command bash -ErrorAction SilentlyContinue) {
    $result = bash -c "ssh -i `"$SshKeyPath`" -o StrictHostKeyChecking=no $ServerUser@$ServerIp `"$bashScript`""
    Write-Host $result
} else {
    # OpenSSH 사용 시도
    ssh -i $SshKeyPath -o StrictHostKeyChecking=no $ServerUser@$ServerIp $bashScript
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✨ 김주영님의 SSH 접속 권한이 활성화되었습니다!" -ForegroundColor Green
} else {
    Write-Host "❌ 오류가 발생했습니다." -ForegroundColor Red
}

