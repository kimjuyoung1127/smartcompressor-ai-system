# SSH 공개키 추가 가이드

## 📋 개요
김주영님(juyoung@signalcraft)의 SSH 공개키를 EC2 서버에 추가하여 접속 권한을 부여합니다.

## 🔑 제공된 SSH 공개키
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCpAVjMIt8W7WZg8jhhu7xFqyMIZImoPqjA6L7LcVZJYCT1VA/JEg3U9jbbp5yh1ake8+/nrdJiATkP+f4/ffEx3H/kgvIzTwZVVzkiBpCEWpT8qE39LdQJzernn2t/FXa4nVl7SvgBUEi+yAL1JZ3Kae+gQGEUl/vb/dKSbKYXtkJlGVlVknajZZR0O4xPb/HKa0eQMAT64EveAThEtI03pVDLdktMW0jB1zTMD4QS1CmqQXh04W5PfooERx0CkseoNd6Op9jMnjPdGPwgSsVcXddjfUU/Hl88dIqfpkGPUiOBYDzNDYP2moTsgfkOpGONydzBbEVAGbVfUVYMs6t2KZr40L+4aVeIRxxAlffVqsYh0uAufMtUa1b8ZKXx6d8kGO+jSK+KxwY+sMuoBB8neJI30zYmT9Czf8JGddAa9O7fOvrKZKecIcsSo+YNHMA9ohF3K7J4mqrS83kySiEyp7c2lnyYOGciySME+681OjCD9Xdoxyo2lks9hiOyiFdy1LAD0XaPFI96wCIzd5eIdRMJZLx68jFllciWsOpcFHDTYS9vH6MmOo5WE8M1mgiWVLDRkamixHSKdFdX/WA7miYMtXSuN8ZAFRr4po/9UxRW6ENncoyjps8G0L7CmgEDhC+n9dre85Fv/bwJ9aJ9bnXh1qrheaEEti0dY0d4Nw== juyoung@signalcraft
```

## 🚀 방법 1: 자동 스크립트 사용 (권장)

### 1단계: EC2 서버에 접속
```bash
ssh -i your-key.pem ubuntu@3.39.124.0
```

### 2단계: 스크립트를 서버로 복사 (로컬에서 실행)
```bash
# 스크립트를 서버로 복사
scp -i your-key.pem scripts/add_juyoung_ssh_key.sh ubuntu@3.39.124.0:/home/ubuntu/
```

### 3단계: 서버에서 스크립트 실행
```bash
# 서버에서 실행
chmod +x add_juyoung_ssh_key.sh
./add_juyoung_ssh_key.sh
```

## 🔧 방법 2: 수동 추가

### 1단계: EC2 서버에 접속
```bash
ssh -i your-key.pem ubuntu@3.39.124.0
```

### 2단계: .ssh 디렉토리 확인 및 생성
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
```

### 3단계: authorized_keys 파일에 키 추가
```bash
# authorized_keys 파일 편집
nano ~/.ssh/authorized_keys

# 또는 echo 명령어로 직접 추가
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCpAVjMIt8W7WZg8jhhu7xFqyMIZImoPqjA6L7LcVZJYCT1VA/JEg3U9jbbp5yh1ake8+/nrdJiATkP+f4/ffEx3H/kgvIzTwZVVzkiBpCEWpT8qE39LdQJzernn2t/FXa4nVl7SvgBUEi+yAL1JZ3Kae+gQGEUl/vb/dKSbKYXtkJlGVlVknajZZR0O4xPb/HKa0eQMAT64EveAThEtI03pVDLdktMW0jB1zTMD4QS1CmqQXh04W5PfooERx0CkseoNd6Op9jMnjPdGPwgSsVcXddjfUU/Hl88dIqfpkGPUiOBYDzNDYP2moTsgfkOpGONydzBbEVAGbVfUVYMs6t2KZr40L+4aVeIRxxAlffVqsYh0uAufMtUa1b8ZKXx6d8kGO+jSK+KxwY+sMuoBB8neJI30zYmT9Czf8JGddAa9O7fOvrKZKecIcsSo+YNHMA9ohF3K7J4mqrS83kySiEyp7c2lnyYOGciySME+681OjCD9Xdoxyo2lks9hiOyiFdy1LAD0XaPFI96wCIzd5eIdRMJZLx68jFllciWsOpcFHDTYS9vH6MmOo5WE8M1mgiWVLDRkamixHSKdFdX/WA7miYMtXSuN8ZAFRr4po/9UxRW6ENncoyjps8G0L7CmgEDhC+n9dre85Fv/bwJ9aJ9bnXh1qrheaEEti0dY0d4Nw== juyoung@signalcraft" >> ~/.ssh/authorized_keys
```

### 4단계: 파일 권한 설정
```bash
chmod 600 ~/.ssh/authorized_keys
```

## ✅ 확인 방법

### 서버에서 확인
```bash
# authorized_keys 파일 내용 확인
cat ~/.ssh/authorized_keys

# 키 개수 확인
wc -l ~/.ssh/authorized_keys

# 특정 키가 있는지 확인
grep "juyoung@signalcraft" ~/.ssh/authorized_keys
```

### 클라이언트에서 테스트 (김주영님)
```bash
# SSH 접속 테스트
ssh ubuntu@3.39.124.0

# 또는 키 파일을 지정하여 접속
ssh -i ~/.ssh/juyoung_private_key ubuntu@3.39.124.0
```

## 🔒 보안 권장사항

1. **파일 권한 확인**
   - `~/.ssh` 디렉토리: 700 (drwx------)
   - `~/.ssh/authorized_keys` 파일: 600 (-rw-------)

2. **키 관리**
   - 각 사용자별로 고유한 SSH 키 사용
   - 정기적으로 사용하지 않는 키 제거

3. **접속 로그 확인**
   ```bash
   # SSH 접속 로그 확인
   sudo tail -f /var/log/auth.log
   ```

## 🚨 문제 해결

### 권한 오류가 발생하는 경우
```bash
# 권한 재설정
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 키가 추가되지 않는 경우
- 키 형식 확인 (ssh-rsa로 시작해야 함)
- 줄바꿈 문자 확인 (한 줄로 작성)
- 파일 인코딩 확인 (UTF-8)

### 접속이 안 되는 경우
- EC2 보안 그룹에서 SSH 포트(22) 허용 확인
- 방화벽 설정 확인
- 서버에서 SSH 서비스 상태 확인: `sudo systemctl status ssh`

## 📞 문의
추가 지원이 필요한 경우 시스템 관리자에게 문의하세요.

