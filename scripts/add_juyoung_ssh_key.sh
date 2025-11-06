#!/bin/bash
# 김주영님의 SSH 공개키를 EC2 서버에 추가하는 스크립트
# EC2 서버에서 실행해야 합니다.

echo "🔑 김주영님(juyoung@signalcraft)의 SSH 공개키 추가 중..."
echo ""

# 홈 디렉토리의 .ssh 디렉토리 확인 및 생성
SSH_DIR="$HOME/.ssh"
AUTHORIZED_KEYS="$SSH_DIR/authorized_keys"

if [ ! -d "$SSH_DIR" ]; then
    echo "📁 .ssh 디렉토리 생성 중..."
    mkdir -p "$SSH_DIR"
    chmod 700 "$SSH_DIR"
    echo "✅ .ssh 디렉토리 생성 완료"
fi

# authorized_keys 파일이 없으면 생성
if [ ! -f "$AUTHORIZED_KEYS" ]; then
    echo "📄 authorized_keys 파일 생성 중..."
    touch "$AUTHORIZED_KEYS"
    chmod 600 "$AUTHORIZED_KEYS"
    echo "✅ authorized_keys 파일 생성 완료"
fi

# 김주영님의 SSH 공개키
PUBLIC_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCpAVjMIt8W7WZg8jhhu7xFqyMIZImoPqjA6L7LcVZJYCT1VA/JEg3U9jbbp5yh1ake8+/nrdJiATkP+f4/ffEx3H/kgvIzTwZVVzkiBpCEWpT8qE39LdQJzernn2t/FXa4nVl7SvgBUEi+yAL1JZ3Kae+gQGEUl/vb/dKSbKYXtkJlGVlVknajZZR0O4xPb/HKa0eQMAT64EveAThEtI03pVDLdktMW0jB1zTMD4QS1CmqQXh04W5PfooERx0CkseoNd6Op9jMnjPdGPwgSsVcXddjfUU/Hl88dIqfpkGPUiOBYDzNDYP2moTsgfkOpGONydzBbEVAGbVfUVYMs6t2KZr40L+4aVeIRxxAlffVqsYh0uAufMtUa1b8ZKXx6d8kGO+jSK+KxwY+sMuoBB8neJI30zYmT9Czf8JGddAa9O7fOvrKZKecIcsSo+YNHMA9ohF3K7J4mqrS83kySiEyp7c2lnyYOGciySME+681OjCD9Xdoxyo2lks9hiOyiFdy1LAD0XaPFI96wCIzd5eIdRMJZLx68jFllciWsOpcFHDTYS9vH6MmOo5WE8M1mgiWVLDRkamixHSKdFdX/WA7miYMtXSuN8ZAFRr4po/9UxRW6ENncoyjps8G0L7CmgEDhC+n9dre85Fv/bwJ9aJ9bnXh1qrheaEEti0dY0d4Nw== juyoung@signalcraft"

# 키가 이미 존재하는지 확인
if grep -Fxq "$PUBLIC_KEY" "$AUTHORIZED_KEYS" 2>/dev/null; then
    echo "⚠️  경고: 해당 SSH 공개키가 이미 authorized_keys에 존재합니다."
    echo "추가 작업을 건너뜁니다."
    exit 0
fi

# 키 추가
echo "🔐 SSH 공개키 추가 중..."
echo "$PUBLIC_KEY" >> "$AUTHORIZED_KEYS"

# 권한 확인 및 수정
chmod 600 "$AUTHORIZED_KEYS"
chmod 700 "$SSH_DIR"

# 추가 확인
if grep -Fxq "$PUBLIC_KEY" "$AUTHORIZED_KEYS" 2>/dev/null; then
    echo "✅ SSH 공개키가 성공적으로 추가되었습니다!"
    echo ""
    echo "📋 추가된 키 정보:"
    echo "   사용자: juyoung@signalcraft"
    echo "   키 타입: ssh-rsa"
    echo ""
    echo "🔍 authorized_keys 파일 상태:"
    KEY_COUNT=$(wc -l < "$AUTHORIZED_KEYS")
    echo "   총 등록된 키 수: $KEY_COUNT"
    echo ""
    echo "✨ 김주영님의 SSH 접속 권한이 활성화되었습니다!"
    echo ""
    echo "📝 다음 단계:"
    echo "   김주영님이 다음 명령어로 서버에 접속할 수 있습니다:"
    echo "   ssh ubuntu@3.39.124.0"
else
    echo "❌ 오류: SSH 공개키 추가에 실패했습니다."
    exit 1
fi

