# 데이터베이스 연결 정보 확인 가이드

## 🔍 상황
`.env` 파일에 DB 관련 환경 변수가 없습니다.

## ✅ 해결 방법

### 방법 1: 기본값 사용 (로컬 PostgreSQL)

코드에서 기본값이 설정되어 있습니다:
- DB_HOST: localhost
- DB_USER: postgres
- DB_NAME: smartcompressor_ai
- DB_PASSWORD: password (또는 기본값)

```bash
cd /var/www/smartcompressor

# 기본값으로 시도
export DB_HOST="localhost"
export DB_USER="postgres"
export DB_NAME="smartcompressor_ai"
export DB_PORT="5432"
export DB_PASSWORD="password"  # 실제 비밀번호로 변경
export PGPASSWORD="$DB_PASSWORD"

# 마이그레이션 실행
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f database/migrations/20241104180000_add_core_tables_and_improvements.sql
```

### 방법 2: 실행 중인 프로세스의 환경 변수 확인

```bash
# PM2로 실행 중인 경우
pm2 env 0 | grep -i DB

# 또는 모든 PM2 프로세스
pm2 env all | grep -i DB

# 시스템 환경 변수 확인
env | grep -i DB
printenv | grep -i DB
```

### 방법 3: 다른 설정 파일 확인

```bash
cd /var/www/smartcompressor

# config 파일 확인
find . -name "*.config.js" -o -name "*.config.json" | xargs grep -i "database\|postgres" 2>/dev/null

# 환경 변수 파일 확인
ls -la .env* config/*.env* 2>/dev/null

# ecosystem.config.js 확인 (PM2 설정)
cat ecosystem.config.js | grep -i "env\|DB" 2>/dev/null
```

### 방법 4: Node.js 스크립트로 실제 연결 정보 확인

```bash
cd /var/www/smartcompressor

# 데이터베이스 서비스 파일에서 실제 사용하는 값 확인
cat services/database_service.js | grep -A 10 "new Pool"
```

### 방법 5: 실행 중인 애플리케이션에서 확인

```bash
# 현재 실행 중인 Node.js 프로세스 확인
ps aux | grep node

# PM2 프로세스 확인
pm2 list
pm2 logs --lines 50 | grep -i "database\|postgres\|connected"
```

### 방법 6: PostgreSQL 기본 설정 확인

```bash
# 로컬 PostgreSQL에 직접 접속 시도
sudo -u postgres psql

# 또는
psql -U postgres -d postgres

# 데이터베이스 목록 확인
\l

# smartcompressor_ai 데이터베이스가 있는지 확인
\c smartcompressor_ai
```

## 🎯 가장 가능성 높은 방법

### RDS 사용 시

```bash
# RDS 엔드포인트 확인 (AWS에서)
# 또는 코드/설정 파일에서 확인

export DB_HOST="your-rds-endpoint.region.rds.amazonaws.com"
export DB_USER="postgres"
export DB_NAME="smartcompressor_ai"
export DB_PASSWORD="실제_비밀번호"
export PGPASSWORD="$DB_PASSWORD"

psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f database/migrations/20241104180000_add_core_tables_and_improvements.sql
```

### 로컬 PostgreSQL 사용 시

```bash
# PostgreSQL 비밀번호 확인/설정
sudo -u postgres psql

# 또는 peer 인증 사용
sudo -u postgres psql -d smartcompressor_ai -f /var/www/smartcompressor/database/migrations/20241104180000_add_core_tables_and_improvements.sql
```

## 💡 빠른 확인 명령어

```bash
cd /var/www/smartcompressor

# 1. PM2 환경 변수 확인
pm2 env 0 2>/dev/null | grep -i DB || echo "PM2 환경 변수 없음"

# 2. 시스템 환경 변수 확인
env | grep -i DB || echo "시스템 환경 변수 없음"

# 3. PostgreSQL 연결 테스트 (기본값)
psql -h localhost -U postgres -d smartcompressor_ai -c "SELECT version();" 2>&1

# 4. Node.js 스크립트로 마이그레이션 실행 (자동으로 환경 변수 읽음)
node database/migrate.js
```

## 🚀 추천 방법

**Node.js 마이그레이션 스크립트를 사용하는 것이 가장 안전합니다:**

```bash
cd /var/www/smartcompressor
node database/migrate.js
```

이 스크립트는 코드에서 기본값을 사용하거나, 실행 중인 프로세스의 환경 변수를 읽을 수 있습니다.

