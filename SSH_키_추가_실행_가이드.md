# 🔑 김주영님 SSH 키 추가 실행 가이드

## 📋 제공된 SSH 공개키
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCpAVjMIt8W7WZg8jhhu7xFqyMIZImoPqjA6L7LcVZJYCT1VA/JEg3U9jbbp5yh1ake8+/nrdJiATkP+f4/ffEx3H/kgvIzTwZVVzkiBpCEWpT8qE39LdQJzernn2t/FXa4nVl7SvgBUEi+yAL1JZ3Kae+gQGEUl/vb/dKSbKYXtkJlGVlVknajZZR0O4xPb/HKa0eQMAT64EveAThEtI03pVDLdktMW0jB1zTMD4QS1CmqQXh04W5PfooERx0CkseoNd6Op9jMnjPdGPwgSsVcXddjfUU/Hl88dIqfpkGPUiOBYDzNDYP2moTsgfkOpGONydzBbEVAGbVfUVYMs6t2KZr40L+4aVeIRxxAlffVqsYh0uAufMtUa1b8ZKXx6d8kGO+jSK+KxwY+sMuoBB8neJI30zYmT9Czf8JGddAa9O7fOvrKZKecIcsSo+YNHMA9ohF3K7J4mqrS83kySiEyp7c2lnyYOGciySME+681OjCD9Xdoxyo2lks9hiOyiFdy1LAD0XaPFI96wCIzd5eIdRMJZLx68jFllciWsOpcFHDTYS9vH6MmOo5WE8M1mgiWVLDRkamixHSKdFdX/WA7miYMtXSuN8ZAFRr4po/9UxRW6ENncoyjps8G0L7CmgEDhC+n9dre85Fv/bwJ9aJ9bnXh1qrheaEEti0dY0d4Nw== juyoung@signalcraft
```

## 🚀 방법 1: WSL/Git Bash 스크립트 사용 (가장 간단, 권장)

### 준비사항
- WSL 또는 Git Bash 설치
- EC2 접속용 SSH 키 파일 (.pem)

### 실행 방법
```bash
# WSL 또는 Git Bash에서
./quick_add_ssh_key.sh /path/to/your-key.pem

# 또는 Windows 경로를 WSL 경로로 변환하여 사용
# 예: C:\Users\YourName\keys\key.pem → /mnt/c/Users/YourName/keys/key.pem
./quick_add_ssh_key.sh /mnt/c/Users/YourName/keys/key.pem
```

## 🚀 방법 2: PowerShell 스크립트 사용 (Windows)

### 준비사항
- EC2 접속용 SSH 키 파일 (.pem) 경로 확인

### 실행 방법
```powershell
# 기본 사용법
.\add_juyoung_ssh_key_simple.ps1 -SshKeyPath "C:\path\to\your-key.pem"

# 또는 상세 버전
.\add_juyoung_ssh_key.ps1 -SshKeyPath "C:\path\to\your-key.pem"
```

### 실행 권한 허용 (처음 한 번만)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🔧 방법 2: WSL 또는 Git Bash 사용 (권장)

### WSL 사용
```bash
# WSL 터미널에서 실행
cd /mnt/c/Users/YourName/path/to/project
ssh -i your-key.pem ubuntu@3.39.124.0 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && if [ ! -f ~/.ssh/authorized_keys ]; then touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys; fi && grep -Fxq "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCpAVjMIt8W7WZg8jhhu7xFqyMIZImoPqjA6L7LcVZJYCT1VA/JEg3U9jbbp5yh1ake8+/nrdJiATkP+f4/ffEx3H/kgvIzTwZVVzkiBpCEWpT8qE39LdQJzernn2t/FXa4nVl7SvgBUEi+yAL1JZ3Kae+gQGEUl/vb/dKSbKYXtkJlGVlVknajZZR0O4xPb/HKa0eQMAT64EveAThEtI03pVDLdktMW0jB1zTMD4QS1CmqQXh04W5PfooERx0CkseoNd6Op9jMnjPdGPwgSsVcXddjfUU/Hl88dIqfpkGPUiOBYDzNDYP2moTsgfkOpGONydzBbEVAGbVfUVYMs6t2KZr40L+4aVeIRxxAlffVqsYh0uAufMtUa1b8ZKXx6d8kGO+jSK+KxwY+sMuoBB8neJI30zYmT9Czf8JGddAa9O7fOvrKZKecIcsSo+YNHMA9ohF3K7J4mqrS83kySiEyp7c2lnyYOGciySME+681OjCD9Xdoxyo2lks9hiOyiFdy1LAD0XaPFI96wCIzd5eIdRMJZLx68jFllciWsOpcFHDTYS9vH6MmOo5WE8M1mgiWVLDRkamixHSKdFdX/WA7miYMtXSuN8ZAFRr4po/9UxRW6ENncoyjps8G0L7CmgEDhC+n9dre85Fv/bwJ9aJ9bnXh1qrheaEEti0dY0d4Nw== juyoung@signalcraft" ~/.ssh/authorized_keys || echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCpAVjMIt8W7WZg8jhhu7xFqyMIZImoPqjA6L7LcVZJYCT1VA/JEg3U9jbbp5yh1ake8+/nrdJiATkP+f4/ffEx3H/kgvIzTwZVVzkiBpCEWpT8qE39LdQJzernn2t/FXa4nVl7SvgBUEi+yAL1JZ3Kae+gQGEUl/vb/dKSbKYXtkJlGVlVknajZZR0O4xPb/HKa0eQMAT64EveAThEtI03pVDLdktMW0jB1zTMD4QS1CmqQXh04W5PfooERx0CkseoNd6Op9jMnjPdGPwgSsVcXddjfUU/Hl88dIqfpkGPUiOBYDzNDYP2moTsgfkOpGONydzBbEVAGbVfUVYMs6t2KZr40L+4aVeIRxxAlffVqsYh0uAufMtUa1b8ZKXx6d8kGO+jSK+KxwY+sMuoBB8neJI30zYmT9Czf8JGddAa9O7fOvrKZKecIcsSo+YNHMA9ohF3K7J4mqrS83kySiEyp7c2lnyYOGciySME+681OjCD9Xdoxyo2lks9hiOyiFdy1LAD0XaPFI96wCIzd5eIdRMJZLx68jFllciWsOpcFHDTYS9vH6MmOo5WE8M1mgiWVLDRkamixHSKdFdX/WA7miYMtXSuN8ZAFRr4po/9UxRW6ENncoyjps8G0L7CmgEDhC+n9dre85Fv/bwJ9aJ9bnXh1qrheaEEti0dY0d4Nw== juyoung@signalcraft" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo "✅ SSH 키 추가 완료!"'
```

### Git Bash 사용
위와 동일한 명령어를 Git Bash에서 실행하면 됩니다.

## 📝 방법 3: 서버에 직접 접속 후 스크립트 실행

### 1단계: 서버 접속
```bash
ssh -i your-key.pem ubuntu@3.39.124.0
```

### 2단계: 스크립트 복사 (로컬에서 실행)
```bash
# Windows PowerShell에서
scp -i your-key.pem scripts/add_juyoung_ssh_key.sh ubuntu@3.39.124.0:/home/ubuntu/

# 또는 WSL/Git Bash에서
scp -i your-key.pem scripts/add_juyoung_ssh_key.sh ubuntu@3.39.124.0:/home/ubuntu/
```

### 3단계: 서버에서 스크립트 실행
```bash
chmod +x add_juyoung_ssh_key.sh
./add_juyoung_ssh_key.sh
```

## ✅ 확인 방법

### 서버에서 확인
```bash
# authorized_keys 파일 내용 확인
cat ~/.ssh/authorized_keys

# 키 개수 확인
wc -l ~/.ssh/authorized_keys

# 특정 키 확인
grep "juyoung@signalcraft" ~/.ssh/authorized_keys
```

### 클라이언트에서 테스트 (김주영님)
```bash
ssh ubuntu@3.39.124.0
```

## 🚨 문제 해결

### SSH 명령어가 없는 경우 (Windows)
1. **WSL 설치**: `wsl --install`
2. **Git Bash 사용**: https://git-scm.com/downloads
3. **OpenSSH 설치**: Windows 설정 > 앱 > 선택적 기능 > OpenSSH 클라이언트

### 권한 오류
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 키가 추가되지 않는 경우
- 키가 한 줄로 작성되었는지 확인
- 줄바꿈 문자 제거 확인
- 서버의 디스크 공간 확인

## 📞 완료 확인

스크립트 실행 후 다음과 같은 메시지가 표시되면 성공입니다:
```
✅ SSH 공개키가 성공적으로 추가되었습니다!
✨ 김주영님의 SSH 접속 권한이 활성화되었습니다!
```

