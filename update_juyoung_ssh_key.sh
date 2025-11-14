#!/bin/bash
# 김주영님 SSH 공개키 교체 스크립트
# 기존 키 제거 후 새 키 추가

# EC2 서버 정보
SERVER_IP="3.39.124.0"
SERVER_USER="ubuntu"
EC2_SERVER="$SERVER_USER@$SERVER_IP"

# SSH 키 파일 (기본 경로, 인자로 받을 수도 있음)
if [ -n "$1" ]; then
    SSH_KEY="$1"
else
    # 기본 키 경로들 시도
    if [ -f "/root/.ssh/signalcraft-new.pem" ]; then
        SSH_KEY="/root/.ssh/signalcraft-new.pem"
    elif [ -f "$HOME/.ssh/signalcraft-new.pem" ]; then
        SSH_KEY="$HOME/.ssh/signalcraft-new.pem"
    elif [ -f "/mnt/c/Signal_craft/음원라벨링도구/compressor-ai-diagnosis/src/signalcraft-new.pem" ]; then
        SSH_KEY="/mnt/c/Signal_craft/음원라벨링도구/compressor-ai-diagnosis/src/signalcraft-new.pem"
    else
        echo "❌ 오류: SSH 키 파일을 찾을 수 없습니다."
        echo "사용법: $0 /path/to/your-key.pem"
        exit 1
    fi
fi

# Windows 파일 시스템의 키 파일인 경우 WSL로 복사하여 권한 설정
if [[ "$SSH_KEY" == /mnt/* ]]; then
    echo "📋 Windows 파일 시스템의 키 파일 감지, WSL로 복사 중..."
    KEY_FILENAME=$(basename "$SSH_KEY")
    LOCAL_KEY_PATH="$HOME/.ssh/${KEY_FILENAME}"
    
    # .ssh 디렉토리 생성
    mkdir -p "$HOME/.ssh"
    chmod 700 "$HOME/.ssh"
    
    # 키 파일 복사
    cp "$SSH_KEY" "$LOCAL_KEY_PATH"
    chmod 600 "$LOCAL_KEY_PATH"
    
    echo "✅ 키 파일 복사 완료: $LOCAL_KEY_PATH"
    SSH_KEY="$LOCAL_KEY_PATH"
else
    # SSH 키 파일 권한 확인
    chmod 600 "$SSH_KEY" 2>/dev/null
fi

# SSH 키 파일 존재 확인
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ 오류: SSH 키 파일을 찾을 수 없습니다: $SSH_KEY"
    exit 1
fi

# 새로운 SSH 공개키
NEW_PUBLIC_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC2UdrEkhWjRmvJA4qykSMSq2J5/rhNml+g0PzrGWf9xLPzO5ykyKA8yj9KHwNIOMLNvaGuBgMT659/hZiIYysBHFHZ9bXn8uFz6oW7Z3Mo4ZSsTISpz6gjUerg4EaXwO9BljvcZiNf1Orcy7xZBq2bCFjwKczDBurewhy+1vazGRs3glyzxU2Dv8Mg8WEUbGKdVmPjVLImsFffMP9+kceDug5D1GL7MHt5MRlBcxofbSPsa+0YUtDaIgjzd49V8wMqCjND4vG44zSRO75Swfcgvc8yvM8uloWE73e4+bQrjER/wJE19RswMOLmn9HWUG8uI6eJNYEtAchmI/QH2K+tp3w8EJcqXlaYhyMIgOKk06UyJatO6adJjXz2lbACyIgG7DQL2fDSM754xa6BYaaWxzWkRyhmdJIsyX9jmj2hyLaBLuvc7xDc25zbv3C1q99Mp+IInhsHTyJ7W7+myvyLYEtAH5VPRHGm6axniKJgVfXQVWHvw4/2vHjbrASalrzxYlCAKPlu1ph0mm/yS372jcVt4O5vzsQzJj4Bjs1FLveQJkWQsSBhcQmU8lEi5UB6L4VB/+PS2F0QmBjDpkdIQHOj+Hwk3n1CqDB4b2m2J3pUm36GheIhkEi7Uzl16/pS4Kpg1ZWX2PQ9nkJo8WYnKCETXHQL7LmowFy51XqS9w== juyoung@signalcraft"

# 기존 키 (제거할 키 - 부분적으로만 매칭)
OLD_KEY_PATTERN="AAAAB3NzaC1yc2EAAAADAQABAAACAQCpAVjMIt8W7WZg8jhhu7xFqyMIZImoPqjA6L7LcVZJYCT1VA/JEg3U9jbbp5yh1ake8+/nrdJiATkP"

echo "🔑 김주영님 SSH 공개키 교체 작업 시작..."
echo "📡 서버: $EC2_SERVER"
echo "🔐 키 파일: $SSH_KEY"
echo ""
echo "⚠️  기존 키를 제거하고 새 키를 추가합니다."
echo ""

# .ssh 디렉토리 확인 및 생성
echo "📁 .ssh 디렉토리 확인 중..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_SERVER" "
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
"

if [ $? -ne 0 ]; then
    echo "❌ .ssh 디렉토리 설정 실패"
    exit 1
fi

# 기존 키 제거
echo "🗑️  기존 키 제거 중..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_SERVER" "
    if [ -f ~/.ssh/authorized_keys ]; then
        # 기존 authorized_keys 백업
        BACKUP_FILE=\"\$HOME/.ssh/authorized_keys.backup_\$(date +%Y%m%d_%H%M%S)\"
        cp ~/.ssh/authorized_keys \$BACKUP_FILE
        echo \"📦 백업 생성: \$BACKUP_FILE\"
        
        # juyoung@signalcraft로 끝나는 모든 키 제거 (안전하게)
        grep -v \"juyoung@signalcraft\" ~/.ssh/authorized_keys > ~/.ssh/authorized_keys.tmp
        
        # 빈 줄과 주석 제거 후 새 파일 생성
        grep -v '^#' ~/.ssh/authorized_keys.tmp | grep -v '^\$' > ~/.ssh/authorized_keys.new
        
        mv ~/.ssh/authorized_keys.new ~/.ssh/authorized_keys
        chmod 600 ~/.ssh/authorized_keys
        
        REMAINING_KEYS=\$(grep -v '^#' ~/.ssh/authorized_keys | grep -v '^\$' | wc -l)
        echo \"✅ 기존 키 제거 완료\"
        echo \"📊 현재 등록된 키 수: \$REMAINING_KEYS\"
    else
        echo \"⚠️  authorized_keys 파일이 없습니다. 새로 생성합니다.\"
        touch ~/.ssh/authorized_keys
        chmod 600 ~/.ssh/authorized_keys
    fi
"

if [ $? -ne 0 ]; then
    echo "❌ 기존 키 제거 실패"
    exit 1
fi

# 새 키 추가
echo ""
echo "➕ 새 SSH 공개키 추가 중..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_SERVER" "
    # authorized_keys 파일 확인
    if [ ! -f ~/.ssh/authorized_keys ]; then
        touch ~/.ssh/authorized_keys
        chmod 600 ~/.ssh/authorized_keys
    fi
    
    # 새 키가 이미 있는지 확인
    if ! grep -q \"$NEW_PUBLIC_KEY\" ~/.ssh/authorized_keys; then
        # 새 키 추가
        echo '$NEW_PUBLIC_KEY' >> ~/.ssh/authorized_keys
        chmod 600 ~/.ssh/authorized_keys
        echo \"✅ 새 키 추가 완료\"
    else
        echo \"⚠️  새 키가 이미 등록되어 있습니다.\"
    fi
    
    echo \"📊 최종 등록된 키 수: \$(grep -v '^#' ~/.ssh/authorized_keys | grep -v '^$' | wc -l)\"
    echo \"📋 등록된 키 목록:\"
    grep -v '^#' ~/.ssh/authorized_keys | grep -v '^$' | awk '{print \"  \" NR \": \" substr(\$0, 1, 50) \"...\"}'
"

if [ $? -ne 0 ]; then
    echo "❌ 새 키 추가 실패"
    exit 1
fi

# 최종 확인
echo ""
echo "🔍 최종 확인 중..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_SERVER" "
    if grep -q \"juyoung@signalcraft\" ~/.ssh/authorized_keys; then
        echo \"✅ 김주영님 키 확인: \$(grep 'juyoung@signalcraft' ~/.ssh/authorized_keys | wc -l)개\"
        echo \"📋 키 정보:\"
        grep 'juyoung@signalcraft' ~/.ssh/authorized_keys | head -1 | awk '{print \"   사용자: \" \$NF \" (\" substr(\$1, 1, 20) \"...)\"}'
    else
        echo \"❌ 김주영님 키가 등록되지 않았습니다!\"
        exit 1
    fi
"

if [ $? -eq 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ SSH 키 교체 작업 완료!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "✨ 김주영님이 다음 명령어로 서버에 접속할 수 있습니다:"
    echo "   ssh $EC2_SERVER"
    echo ""
    echo "📝 참고: 기존 키는 제거되었으며, 새 키만 등록되었습니다."
    echo "✅ SSH 키 교체 작업이 성공적으로 완료되었습니다!"
else
    echo ""
    echo "❌ 키 확인 실패"
    exit 1
fi

