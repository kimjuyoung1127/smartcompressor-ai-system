# DB 연결 정보 최종 확인 방법

## 🔍 현재 상황
- `.env` 파일에 DB 정보 없음
- PM2 환경 변수에도 DB 정보 없음
- 실행 중인 애플리케이션이 어떻게 연결하는지 확인 필요

## ✅ 해결 방법

### 방법 1: 실행 중인 애플리케이션 로그 확인

```bash
# PM2 로그에서 DB 연결 정보 확인
pm2 logs --lines 200 --nostream | grep -i "database\|postgres\|connected\|host\|user\|password"

# 또는 최근 에러 로그
pm2 logs --err --lines 100
```

### 방법 2: 코드에서 하드코딩된 정보 확인

```bash
cd /var/www/smartcompressor

# database_service.js에서 실제 사용하는 값 확인
cat services/database_service.js | grep -A 15 "new Pool"

# 또는 다른 설정 파일 확인
find . -name "*.js" -o -name "*.json" | xargs grep -l "postgres\|database" | head -10
```

### 방법 3: 로컬 PostgreSQL peer 인증 사용 (가장 간단)

```bash
cd /var/www/smartcompressor

# peer 인증으로 직접 실행 (비밀번호 불필요)
sudo -u postgres psql -d smartcompressor_ai -f database/migrations/20241104180000_add_core_tables_and_improvements.sql
```

### 방법 4: PostgreSQL 비밀번호 재설정

```bash
# PostgreSQL에 접속하여 비밀번호 확인/재설정
sudo -u postgres psql

# PostgreSQL 프롬프트에서:
ALTER USER postgres WITH PASSWORD 'new_password';
\q

# 그 다음
export DB_PASSWORD="new_password"
export PGPASSWORD="$DB_PASSWORD"
psql -h localhost -U postgres -d smartcompressor_ai -f database/migrations/20241104180000_add_core_tables_and_improvements.sql
```

### 방법 5: 실행 중인 서비스의 실제 연결 테스트

```bash
# 애플리케이션이 실제로 연결하는 DB 확인
pm2 logs --lines 50 | grep -i "database\|postgres" | tail -10

# 또는 서비스가 실행 중인지 확인
pm2 list
pm2 describe 0
```

## 🎯 가장 가능성 높은 해결책

### 시나리오 1: 로컬 PostgreSQL 사용 (peer 인증)

```bash
cd /var/www/smartcompressor

# 데이터베이스가 존재하는지 확인
sudo -u postgres psql -l | grep smartcompressor

# 마이그레이션 실행 (peer 인증)
sudo -u postgres psql -d smartcompressor_ai -f database/migrations/20241104180000_add_core_tables_and_improvements.sql
```

### 시나리오 2: RDS 사용 (환경 변수 없음)

애플리케이션이 다른 방식으로 연결 정보를 얻고 있을 수 있습니다:
- AWS Secrets Manager
- 하드코딩된 값
- 다른 설정 파일

```bash
# AWS 설정 확인
aws rds describe-db-instances 2>/dev/null | grep -i "endpoint\|address"

# 또는 코드에서 확인
grep -r "rds\|amazonaws" . --include="*.js" --include="*.json" | head -10
```

## 💡 빠른 해결책 (단계별)

### 1단계: 데이터베이스 존재 확인

```bash
# PostgreSQL에 접속 가능한지 확인
sudo -u postgres psql -l
```

### 2단계: smartcompressor_ai 데이터베이스 확인

```bash
sudo -u postgres psql -c "\l" | grep smartcompressor
```

### 3단계: 데이터베이스가 있으면 마이그레이션 실행

```bash
cd /var/www/smartcompressor
sudo -u postgres psql -d smartcompressor_ai -f database/migrations/20241104180000_add_core_tables_and_improvements.sql
```

### 4단계: 데이터베이스가 없으면 생성 후 실행

```bash
# 데이터베이스 생성
sudo -u postgres psql -c "CREATE DATABASE smartcompressor_ai;"

# 마이그레이션 실행
cd /var/www/smartcompressor
sudo -u postgres psql -d smartcompressor_ai -f database/migrations/20241104180000_add_core_tables_and_improvements.sql
```

## 🚀 추천 실행 순서

1. **먼저 peer 인증 시도** (가장 간단)
   ```bash
   sudo -u postgres psql -d smartcompressor_ai -f /var/www/smartcompressor/database/migrations/20241104180000_add_core_tables_and_improvements.sql
   ```

2. **실패하면 데이터베이스 확인**
   ```bash
   sudo -u postgres psql -l
   ```

3. **실행 중인 애플리케이션 로그 확인**
   ```bash
   pm2 logs --lines 100 | grep -i "database\|postgres\|connected"
   ```

