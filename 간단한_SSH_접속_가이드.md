# 🔑 EC2 서버 접속 가이드

## 문제

로컬에서 SSH 접속 시 `Permission denied (publickey)` 오류가 발생합니다.

## 해결 방법

SSH 접속 시 키 파일을 지정해야 합니다:

```bash
ssh -i /root/.ssh/signalcraft-new.pem ubuntu@3.39.124.0
```

## 빠른 접속 명령어

### 현재 디렉토리에서:
```bash
ssh -i ~/.ssh/signalcraft-new.pem ubuntu@3.39.124.0
```

### 또는 alias 설정 (선택사항):
```bash
# ~/.bashrc에 추가
alias ec2='ssh -i ~/.ssh/signalcraft-new.pem ubuntu@3.39.124.0'
```

그 다음:
```bash
ec2
```

## PM2 실행 주의사항

⚠️ **중요**: PM2는 EC2 서버에서 실행해야 합니다!

**잘못된 방법:**
```bash
# 로컬에서 실행 (안 됨!)
pm2 restart all
```

**올바른 방법:**
```bash
# 방법 1: SSH로 접속 후 실행
ssh -i ~/.ssh/signalcraft-new.pem ubuntu@3.39.124.0
pm2 restart all

# 방법 2: 원격 명령 실행
ssh -i ~/.ssh/signalcraft-new.pem ubuntu@3.39.124.0 "pm2 restart all"

# 방법 3: 스크립트 사용 (권장)
./restart_server.sh
```

## 서버 재시작 스크립트 사용

```bash
chmod +x restart_server.sh
./restart_server.sh
```

이 스크립트가 자동으로:
1. EC2 서버에 접속
2. 현재 실행 중인 프로세스 확인
3. PM2로 재시작
4. 상태 확인

---

**위 스크립트를 실행하시면 자동으로 서버가 재시작됩니다!** 😊

