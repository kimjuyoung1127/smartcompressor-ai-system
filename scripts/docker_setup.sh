#!/bin/bash
# Docker 설정 및 실행 스크립트

set -e

echo "=========================================="
echo "SmartCompressor AI System - Docker 설정"
echo "=========================================="
echo ""

# 환경 변수 파일 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다."
    if [ -f env.example ]; then
        echo "📋 env.example을 .env로 복사합니다..."
        cp env.example .env
        echo "✅ .env 파일 생성 완료"
        echo "⚠️  .env 파일을 편집하여 실제 값으로 변경하세요!"
    else
        echo "❌ env.example 파일도 없습니다."
        exit 1
    fi
else
    echo "✅ .env 파일 확인 완료"
fi

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되어 있지 않습니다."
    echo "   Docker 설치: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되어 있지 않습니다."
    echo "   Docker Compose 설치: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker 및 Docker Compose 확인 완료"
echo ""

# 모드 선택
echo "실행 모드를 선택하세요:"
echo "1) 프로덕션 모드 (docker-compose.yml)"
echo "2) 개발 모드 (docker-compose.dev.yml)"
read -p "선택 (1 또는 2, 기본: 1): " mode

mode=${mode:-1}

if [ "$mode" == "2" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
    echo "🔧 개발 모드로 실행합니다 (코드 변경 시 자동 반영)"
else
    COMPOSE_FILE="docker-compose.yml"
    echo "🚀 프로덕션 모드로 실행합니다"
fi

echo ""

# Docker 이미지 빌드
echo "📦 Docker 이미지 빌드 중..."
docker-compose -f $COMPOSE_FILE build

if [ $? -eq 0 ]; then
    echo "✅ 빌드 완료"
else
    echo "❌ 빌드 실패"
    exit 1
fi

echo ""

# 컨테이너 시작
echo "🚀 컨테이너 시작 중..."
docker-compose -f $COMPOSE_FILE up -d

if [ $? -eq 0 ]; then
    echo "✅ 컨테이너 시작 완료"
    echo ""
    echo "=========================================="
    echo "서비스 접속 정보"
    echo "=========================================="
    echo "웹 대시보드: http://localhost:5000"
    echo "API: http://localhost:5000/api"
    echo "헬스 체크: http://localhost:5000/api/health"
    echo ""
    echo "로그 확인: docker-compose -f $COMPOSE_FILE logs -f"
    echo "컨테이너 중지: docker-compose -f $COMPOSE_FILE down"
    echo "=========================================="
else
    echo "❌ 컨테이너 시작 실패"
    exit 1
fi

