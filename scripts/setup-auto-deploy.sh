#!/bin/bash

# 자동 배포를 위한 설정 스크립트

echo "🚀 자동 배포 설정을 시작합니다..."

# 1. SSH 키 생성 (이미 있다면 건너뛰기)
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "📝 SSH 키를 생성합니다..."
    ssh-keygen -t rsa -b 4096 -C "deploy@signalcraft.kr" -f ~/.ssh/id_rsa -N ""
fi

# 2. 공개키를 authorized_keys에 추가
echo "🔑 공개키를 authorized_keys에 추가합니다..."
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# 3. PM2 설치 (없다면)
if ! command -v pm2 &> /dev/null; then
    echo "📦 PM2를 설치합니다..."
    npm install -g pm2
fi

# 4. PM2로 서버 등록
echo "⚙️ PM2로 서버를 등록합니다..."
pm2 start server.js --name signalcraft-nodejs --watch

# 5. PM2 자동 시작 설정
pm2 startup
pm2 save

# 6. GitHub Actions를 위한 웹훅 설정
echo "🔗 GitHub Actions를 위한 설정을 완료합니다..."

echo "✅ 자동 배포 설정이 완료되었습니다!"
echo ""
echo "📋 다음 단계:"
echo "1. GitHub 저장소 Settings → Secrets에 다음을 추가:"
echo "   - EC2_HOST: $(curl -s ifconfig.me)"
echo "   - EC2_USERNAME: ubuntu"
echo "   - EC2_SSH_KEY: $(cat ~/.ssh/id_rsa)"
echo "   - GITHUB_TOKEN: your_github_token"
echo ""
echo "2. 이제 GitHub에 푸시하면 자동으로 배포됩니다!"
