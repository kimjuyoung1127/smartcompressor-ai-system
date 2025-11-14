# Docker 사용 가이드

## 📋 개요

Docker를 사용하여 SmartCompressor AI 시스템을 다른 컴퓨터에서도 쉽게 실행할 수 있습니다.

---

## 🚀 빠른 시작

### 1. Docker 설치 확인

```bash
# Docker 버전 확인
docker --version
docker-compose --version
```

### 2. 프로젝트 클론

```bash
git clone https://github.com/SEONBEOM-Kim/smartcompressor-ai-system.git
cd smartcompressor-ai-system
```

### 3. 환경 변수 설정

```bash
cp env.example .env
# .env 파일 편집
```

### 4. Docker 컨테이너 실행

```bash
# 프로덕션 모드
docker-compose up -d

# 개발 모드 (코드 변경 시 자동 반영)
docker-compose -f docker-compose.dev.yml up -d
```

### 5. 서비스 접속

- **웹 대시보드**: http://localhost:5000
- **API**: http://localhost:5000/api
- **헬스 체크**: http://localhost:5000/api/health

---

## 🔧 주요 명령어

### 컨테이너 관리

```bash
# 컨테이너 시작
docker-compose up -d

# 컨테이너 중지
docker-compose down

# 컨테이너 재시작
docker-compose restart

# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f app
```

### 이미지 관리

```bash
# 이미지 빌드
docker-compose build

# 이미지 재빌드 (캐시 없이)
docker-compose build --no-cache

# 이미지 삭제
docker-compose down --rmi all
```

### 컨테이너 내부 접속

```bash
# 컨테이너 내부 접속
docker-compose exec app bash

# Python 셸 실행
docker-compose exec app python

# 테스트 실행
docker-compose exec app pytest tests/ -v
```

---

## 📦 볼륨 마운트

### 개발 모드

개발 모드에서는 코드 변경이 자동으로 반영됩니다:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

**마운트된 디렉토리**:
- `./` → `/app` (코드)
- `./data` → `/app/data` (데이터)
- `./uploads` → `/app/uploads` (업로드 파일)

### 프로덕션 모드

프로덕션 모드에서는 데이터만 마운트됩니다:

```bash
docker-compose up -d
```

---

## 🔍 문제 해결

### 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker-compose logs app

# 컨테이너 재빌드
docker-compose up -d --build
```

### 포트 충돌

```bash
# 다른 포트 사용
docker-compose up -d
# docker-compose.yml에서 포트 변경: "5001:5000"
```

### 데이터 손실 방지

```bash
# 볼륨 확인
docker-compose down -v  # 주의: 데이터 삭제됨

# 데이터 백업
docker-compose exec app tar -czf /tmp/backup.tar.gz /app/data
```

---

## 🎯 사용 시나리오

### 시나리오 1: 새로운 개발자 온보딩

```bash
# 1. 저장소 클론
git clone https://github.com/SEONBEOM-Kim/smartcompressor-ai-system.git
cd smartcompressor-ai-system

# 2. 환경 변수 설정
cp .env.example .env

# 3. Docker 실행
docker-compose up -d

# 4. 서비스 확인
curl http://localhost:5000/api/health
```

**소요 시간**: 약 5분

---

### 시나리오 2: 다른 컴퓨터에서 개발

```bash
# 1. 코드 동기화 (Git)
git pull

# 2. Docker 재빌드 (필요시)
docker-compose up -d --build

# 3. 개발 모드 실행
docker-compose -f docker-compose.dev.yml up -d
```

**장점**: 환경 설정 불필요, 즉시 개발 시작 가능

---

### 시나리오 3: 프로덕션 배포

```bash
# 1. 프로덕션 설정 확인
docker-compose -f docker-compose.prod.yml config

# 2. 프로덕션 모드 실행
docker-compose -f docker-compose.prod.yml up -d

# 3. 로그 모니터링
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 📊 리소스 사용량

### 최소 요구사항

- **CPU**: 2 코어
- **메모리**: 4GB RAM
- **디스크**: 10GB 여유 공간

### 권장 사양

- **CPU**: 4 코어 이상
- **메모리**: 8GB RAM 이상
- **디스크**: 50GB 여유 공간

### 리소스 모니터링

```bash
# 컨테이너 리소스 사용량 확인
docker stats smartcompressor-ai-app
```

---

## 🔐 보안 고려사항

### 환경 변수 관리

```bash
# .env 파일은 절대 커밋하지 마세요
echo ".env" >> .gitignore

# 프로덕션에서는 Docker Secrets 사용
docker-compose -f docker-compose.prod.yml up -d
```

### 네트워크 격리

```bash
# Docker 네트워크 확인
docker network ls

# 네트워크 상세 정보
docker network inspect smartcompressor-ai-system_smartcompressor-network
```

---

## 💡 모범 사례

1. **개발 시**: `docker-compose.dev.yml` 사용
2. **테스트 시**: `docker-compose.test.yml` 사용 (필요시 생성)
3. **프로덕션**: `docker-compose.prod.yml` 사용

---

## 📝 추가 리소스

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 공식 문서](https://docs.docker.com/compose/)
- 프로젝트 README: `README_개발자_가이드.md`

---

**작성일**: 2024년  
**버전**: 1.0  
**상태**: 프로덕션 준비 완료

