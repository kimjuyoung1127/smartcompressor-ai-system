#!/bin/bash
# HTTPS 설정 스크립트 (EC2 서버에서 실행)

echo "🔒 SIGNALCRAFT HTTPS 설정 시작..."

# 1. Nginx 설정 파일 백업
echo "📁 기존 설정 백업 중..."
sudo cp /etc/nginx/sites-available/signalcraft /etc/nginx/sites-available/signalcraft.backup

# 2. 새로운 HTTPS 설정 적용
echo "🔧 HTTPS 설정 적용 중..."
sudo cp nginx_https_config.conf /etc/nginx/sites-available/signalcraft

# 3. Nginx 설정 테스트
echo "🧪 Nginx 설정 테스트 중..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx 설정 테스트 성공"
    
    # 4. Nginx 재시작
    echo "🔄 Nginx 재시작 중..."
    sudo systemctl restart nginx
    
    # 5. Nginx 상태 확인
    echo "📊 Nginx 상태 확인 중..."
    sudo systemctl status nginx --no-pager
    
    # 6. 포트 확인
    echo "🌐 포트 사용 상태:"
    sudo netstat -tlnp | grep -E ":(80|443)"
    
    echo "🎉 HTTPS 설정 완료!"
    echo "🌐 HTTP: http://signalcraft.kr → https://signalcraft.kr로 리다이렉트"
    echo "🔒 HTTPS: https://signalcraft.kr → 정상 접속"
    
else
    echo "❌ Nginx 설정 테스트 실패"
    echo "🔄 백업 설정으로 복원 중..."
    sudo cp /etc/nginx/sites-available/signalcraft.backup /etc/nginx/sites-available/signalcraft
    sudo systemctl restart nginx
    exit 1
fi
