#!/bin/bash
# SSL 인증서 발급 스크립트 (EC2 서버에서 실행)

echo "🔐 SIGNALCRAFT SSL 인증서 발급 시작..."

# 1. Certbot 설치 확인
echo "📦 Certbot 설치 확인 중..."
if ! command -v certbot &> /dev/null; then
    echo "📥 Certbot 설치 중..."
    sudo apt update
    sudo apt install certbot python3-certbot-nginx -y
fi

# 2. SSL 인증서 발급
echo "🔑 SSL 인증서 발급 중..."
sudo certbot --nginx -d signalcraft.kr -d www.signalcraft.kr --non-interactive --agree-tos --email admin@signalcraft.kr

# 3. SSL 인증서 확인
echo "📋 SSL 인증서 확인 중..."
sudo certbot certificates

# 4. 자동 갱신 설정
echo "⏰ 자동 갱신 설정 중..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# 5. 방화벽 설정
echo "🔥 방화벽 설정 중..."
sudo ufw allow 443
sudo ufw status

echo "🎉 SSL 인증서 발급 완료!"
echo "🔒 HTTPS: https://signalcraft.kr"
echo "🌐 HTTP: http://signalcraft.kr → https://signalcraft.kr로 리다이렉트"
