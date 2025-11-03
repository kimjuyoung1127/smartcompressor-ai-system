# 🔧 GitHub Actions 배포 오류 해결 가이드

## 🚨 발생한 오류

```
ssh: handshake failed: ssh: unable to authenticate, attempted methods [none publickey], no supported methods remain
```

**원인**: SSH 키 인증 실패

---

## ✅ 해결 방법

### 방법 1: GitHub Secrets 확인 및 수정

#### 1. GitHub Secrets 확인
1. **GitHub 저장소** → **Settings** → **Secrets and variables** → **Actions**
2. 다음 Secrets 확인:
   - `EC2_HOST`
   - `EC2_USER`
   - `EC2_SSH_KEY`

#### 2. EC2_SSH_KEY 설정
SSH 키를 올바르게 설정해야 합니다:

```bash
# 로컬에서 SSH 키 확인
cat ~/.ssh/id_rsa  # 또는 해당 개인키

# 이 내용을 GitHub Secrets의 EC2_SSH_KEY에 저장
```

**주의**: 전체 개인키 내용을 복사해야 합니다 (줄바꿈 포함)

#### 3. Secrets 업데이트
1. Settings → Secrets → EC2_SSH_KEY 선택
2. **Update** 클릭
3. 키 파일 전체 내용 붙여넣기
4. **Update secret** 클릭

---

### 방법 2: 수동 배포 (빠른 해결)

GitHub Actions가 계속 실패하면 수동 배포를 추천합니다:

#### 1. 프로덕션 서버 접속
```bash
ssh ubuntu@signalcraft.kr
# 또는
ssh -i /path/to/key.pem ubuntu@signalcraft.kr
```

#### 2. 배포 스크립트 실행
```bash
# 프로젝트 디렉토리로 이동
cd /home/ubuntu/smartcompressor-ai-system

# 최신 코드 가져오기
git pull origin main

# Python 의존성 확인
pip install -r requirements.txt

# 서비스 재시작
pm2 restart signalcraft-python
pm2 restart signalcraft-nodejs

# 상태 확인
pm2 status
pm2 logs --lines 50
```

#### 3. 테스트
```bash
# 로컬 테스트
curl http://localhost:8000/dashboard
curl http://localhost:8000/static/css/dashboard_v3.css

# Nginx 재시작 (필요시)
sudo systemctl restart nginx
```

---

### 방법 3: SSH 키 새로 생성 및 등록

#### 1. 새로운 SSH 키 생성
```bash
# 로컬에서 실행
ssh-keygen -t rsa -b 4096 -C "your_email@example.com" -f ~/.ssh/github_actions_key

# 개인키 확인
cat ~/.ssh/github_actions_key
```

#### 2. 공개키를 서버에 등록
```bash
# 서버에 접속
ssh ubuntu@signalcraft.kr

# authorized_keys에 추가
cat >> ~/.ssh/authorized_keys << EOF
# 공개키 내용 (github_actions_key.pub)
EOF

# 권한 설정
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

#### 3. GitHub Secrets 업데이트
```bash
# 개인키 내용 복사
cat ~/.ssh/github_actions_key
```

1. GitHub → Settings → Secrets
2. EC2_SSH_KEY 업데이트
3. 개인키 내용 붙여넣기

---

## 🎯 즉시 해결을 위한 임시 스크립트

제가 수동 배포 스크립트를 만들었습니다:

```bash
#!/bin/bash
# deploy_to_server.sh

echo "🚀 프로덕션 서버 배포 시작..."

# 서버에 SSH 접속하여 배포
ssh ubuntu@signalcraft.kr << 'ENDSSH'
cd /home/ubuntu/smartcompressor-ai-system

echo "📥 최신 코드 가져오기..."
git pull origin main

echo "📦 Python 의존성 설치..."
pip install -r requirements.txt

echo "🔄 서비스 재시작..."
pm2 restart signalcraft-python
pm2 restart signalcraft-nodejs

echo "📊 서비스 상태 확인..."
pm2 status

echo "✅ 배포 완료!"
ENDSSH

echo "🎉 배포 스크립트 실행 완료!"
```

---

## 🔍 문제 진단

### SSH 키 문제인지 확인

```bash
# 로컬에서 테스트
ssh -v ubuntu@signalcraft.kr

# 또는
ssh -i ~/.ssh/id_rsa -v ubuntu@signalcraft.kr
```

**예상되는 출력**:
```
debug1: Offering public key: /Users/username/.ssh/id_rsa RSA SHA256:...
debug1: Server accepts key: pkalg rsa-sha2-512 blen ...
Authenticated to signalcraft.kr
```

---

## ✅ 권장 작업 순서

### 즉시 (수동 배포)
1. ✅ 프로덕션 서버에 SSH 접속
2. ✅ `git pull origin main` 실행
3. ✅ `pm2 restart` 실행
4. ✅ https://signalcraft.kr/dashboard 테스트

### 장기 (GitHub Actions 수정)
1. ⏳ GitHub Secrets 확인 및 수정
2. ⏳ SSH 키 새로 생성 (필요시)
3. ⏳ GitHub Actions 테스트

---

## 📋 체크리스트

### 수동 배포
- [ ] SSH 접속 성공
- [ ] git pull 성공
- [ ] pm2 restart 성공
- [ ] 서비스 정상 동작 확인

### GitHub Actions 수정
- [ ] EC2_SSH_KEY 확인
- [ ] SSH 키 형식 확인 (전체 개인키)
- [ ] Secrets 재설정
- [ ] Actions 테스트 실행

---

## 🚀 빠른 수동 배포 명령어

프로덕션 서버에서 직접 실행:

```bash
cd /home/ubuntu/smartcompressor-ai-system && \
git pull origin main && \
pip install -r requirements.txt && \
pm2 restart signalcraft-python && \
pm2 restart signalcraft-nodejs && \
pm2 logs --lines 50
```

---

**다음 단계**: SSH 접속 후 위 명령어를 실행하세요!

