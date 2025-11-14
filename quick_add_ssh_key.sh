#!/bin/bash
# 김주영님 SSH 키 빠른 추가 스크립트 (WSL/Git Bash용)
# 사용법: ./quick_add_ssh_key.sh /path/to/your-key.pem

if [ -z "$1" ]; then
    echo "❌ 오류: SSH 키 파일 경로를 제공해야 합니다."
    echo "사용법: $0 /path/to/your-key.pem"
    exit 1
fi

SSH_KEY="$1"
SERVER_IP="3.39.124.0"
SERVER_USER="ubuntu"

# SSH 키 파일 존재 확인
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ 오류: SSH 키 파일을 찾을 수 없습니다: $SSH_KEY"
    exit 1
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
    # SSH 키 파일 권한 확인 (권장)
    chmod 600 "$SSH_KEY" 2>/dev/null
fi

PUBLIC_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCpAVjMIt8W7WZg8jhhu7xFqyMIZImoPqjA6L7LcVZJYCT1VA/JEg3U9jbbp5yh1ake8+/nrdJiATkP+f4/ffEx3H/kgvIzTwZVVzkiBpCEWpT8qE39LdQJzernn2t/FXa4nVl7SvgBUEi+yAL1JZ3Kae+gQGEUl/vb/dKSbKYXtkJlGVlVknajZZR0O4xPb/HKa0eQMAT64EveAThEtI03pVDLdktMW0jB1zTMD4QS1CmqQXh04W5PfooERx0CkseoNd6Op9jMnjPdGPwgSsVcXddjfUU/Hl88dIqfpkGPUiOBYDzNDYP2moTsgfkOpGONydzBbEVAGbVfUVYMs6t2KZr40L+4aVeIRxxAlffVqsYh0uAufMtUa1b8ZKXx6d8kGO+jSK+KxwY+sMuoBB8neJI30zYmT9Czf8JGddAa9O7fOvrKZKecIcsSo+YNHMA9ohF3K7J4mqrS83kySiEyp7c2lnyYOGciySME+681OjCD9Xdoxyo2lks9hiOyiFdy1LAD0XaPFI96wCIzd5eIdRMJZLx68jFllciWsOpcFHDTYS9vH6MmOo5WE8M1mgiWVLDRkamixHSKdFdX/WA7miYMtXSuN8ZAFRr4po/9UxRW6ENncoyjps8G0L7CmgEDhC+n9dre85Fv/bwJ9aJ9bnXh1qrheaEEti0dY0d4Nw== juyoung@signalcraft"

echo "🔑 김주영님(juyoung@signalcraft)의 SSH 공개키 추가 중..."
echo "📡 서버: $SERVER_USER@$SERVER_IP"
echo "🔐 키 파일: $SSH_KEY"
echo ""

# EOF heredoc 대신 단계별 명령어 실행 (WSL 붙여넣기 문제 해결)

echo "📁 .ssh 디렉토리 설정 중..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "mkdir -p ~/.ssh && chmod 700 ~/.ssh" || {
    echo "❌ .ssh 디렉토리 생성 실패"
    exit 1
}

echo "📄 authorized_keys 파일 준비 중..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "[ -f ~/.ssh/authorized_keys ] || (touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys)" || {
    echo "❌ authorized_keys 파일 생성 실패"
    exit 1
}

echo "🔍 기존 키 확인 중..."
KEY_EXISTS=$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "grep -Fxq '$PUBLIC_KEY' ~/.ssh/authorized_keys 2>/dev/null && echo 'yes' || echo 'no'")

if [ "$KEY_EXISTS" = "yes" ]; then
    echo "⚠️  경고: 해당 SSH 공개키가 이미 authorized_keys에 존재합니다."
    KEY_COUNT=$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "wc -l < ~/.ssh/authorized_keys")
    echo "📊 총 등록된 키 수: $KEY_COUNT"
    EXIT_CODE=0
else
    echo "🔐 SSH 공개키 추가 중..."
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys" || {
        echo "❌ 키 추가 실패"
        exit 1
    }
    
    echo "✅ 확인 중..."
    VERIFY=$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "grep -Fxq '$PUBLIC_KEY' ~/.ssh/authorized_keys 2>/dev/null && echo 'yes' || echo 'no'")
    
    if [ "$VERIFY" = "yes" ]; then
        echo "✅ SSH 공개키가 성공적으로 추가되었습니다!"
        echo ""
        echo "📋 추가된 키 정보:"
        echo "   사용자: juyoung@signalcraft"
        echo "   키 타입: ssh-rsa"
        KEY_COUNT=$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "wc -l < ~/.ssh/authorized_keys")
        echo "   총 등록된 키 수: $KEY_COUNT"
        echo ""
        echo "✨ 김주영님의 SSH 접속 권한이 활성화되었습니다!"
        EXIT_CODE=0
    else
        echo "❌ 오류: SSH 공개키 추가에 실패했습니다."
        EXIT_CODE=1
    fi
fi

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 완료! 김주영님이 다음 명령어로 서버에 접속할 수 있습니다:"
    echo "   ssh ubuntu@$SERVER_IP"
    echo ""
    echo "✅ SSH 키 추가 작업이 성공적으로 완료되었습니다!"
else
    echo ""
    echo "❌ 오류: SSH 키 추가에 실패했습니다. (종료 코드: $EXIT_CODE)"
    echo ""
    echo "💡 문제 해결 방법:"
    echo "   1. SSH 키 파일 경로가 올바른지 확인"
    echo "   2. SSH 키 파일 권한 확인: chmod 600 $SSH_KEY"
    echo "   3. 서버 접속 가능 여부 확인: ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP"
    exit 1
fi

