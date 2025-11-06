#!/bin/bash
# GitHub CLI 인터랙티브 PR 리뷰 도구

PR_NUMBER="${1:-4}"

echo "🔍 GitHub CLI 인터랙티브 PR 리뷰"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 인증 확인
if ! gh auth status &>/dev/null; then
    echo "❌ GitHub CLI 인증 필요"
    echo ""
    echo "인증 실행:"
    read -p "지금 인증하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh auth login
    else
        exit 1
    fi
fi

# PR 정보 표시
echo "📋 PR #$PR_NUMBER 정보"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr view $PR_NUMBER --json title,author,state,url --jq '
  "제목: \(.title)",
  "작성자: \(.author.login)",
  "상태: \(.state)",
  "URL: \(.url)"
'
echo ""

# 메뉴
while true; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "선택하세요:"
    echo "  1) 변경된 파일 목록 보기"
    echo "  2) 전체 diff 보기"
    echo "  3) 특정 파일 diff 보기"
    echo "  4) 자동 코드 분석 실행"
    echo "  5) 리뷰 코멘트 작성"
    echo "  6) PR 승인"
    echo "  7) 변경 요청"
    echo "  8) 종료"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    read -p "선택 (1-8): " choice
    
    case $choice in
        1)
            echo ""
            echo "📁 변경된 파일 목록:"
            gh pr view $PR_NUMBER --json files --jq '.files[] | "  \(.path) (+\(.additions) -\(.deletions))"'
            echo ""
            ;;
        2)
            echo ""
            echo "📊 전체 diff 표시 중... (q를 눌러 종료)"
            sleep 2
            gh pr diff $PR_NUMBER | less
            ;;
        3)
            echo ""
            gh pr view $PR_NUMBER --json files --jq '.files[].path' | nl
            read -p "파일 번호 선택: " file_num
            file_path=$(gh pr view $PR_NUMBER --json files --jq '.files[].path' | sed -n "${file_num}p")
            if [ -n "$file_path" ]; then
                echo ""
                echo "📄 $file_path diff:"
                gh pr diff $PR_NUMBER -- "$file_path" | less
            else
                echo "❌ 잘못된 번호"
            fi
            ;;
        4)
            echo ""
            echo "🤖 자동 분석 실행 중..."
            DIFF_FILE="pr_${PR_NUMBER}_diff.txt"
            gh pr diff $PR_NUMBER > "$DIFF_FILE"
            if [ -f "analyze_pr_changes.py" ]; then
                python3 analyze_pr_changes.py "$DIFF_FILE"
            else
                echo "❌ analyze_pr_changes.py 파일이 없습니다"
            fi
            echo ""
            ;;
        5)
            echo ""
            read -p "리뷰 코멘트 내용: " comment
            if [ -n "$comment" ]; then
                gh pr comment $PR_NUMBER --body "$comment"
                echo "✅ 코멘트 작성 완료"
            fi
            echo ""
            ;;
        6)
            echo ""
            read -p "정말 승인하시겠습니까? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                read -p "승인 메시지 (선택사항): " message
                if [ -n "$message" ]; then
                    gh pr review $PR_NUMBER --approve --body "$message"
                else
                    gh pr review $PR_NUMBER --approve
                fi
                echo "✅ PR 승인 완료"
            fi
            echo ""
            ;;
        7)
            echo ""
            read -p "변경 요청 내용: " comment
            if [ -n "$comment" ]; then
                gh pr review $PR_NUMBER --request-changes --body "$comment"
                echo "✅ 변경 요청 완료"
            fi
            echo ""
            ;;
        8)
            echo "👋 종료합니다"
            exit 0
            ;;
        *)
            echo "❌ 잘못된 선택"
            echo ""
            ;;
    esac
done

