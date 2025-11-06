# 실행 중인 애플리케이션의 DB 연결 정보 확인

## 🔍 현재 상황
- `.env` 파일에 DB 정보 없음
- 기본값 `password`로 시도했지만 인증 실패
- 실행 중인 애플리케이션이 실제로 사용하는 연결 정보 확인 필요

## ✅ 해결 방법

### 방법 1: PM2 환경 변수 확인

```bash
# PM2로 실행 중인 모든 프로세스의 환경 변수 확인
pm2 env all

# 특정 프로세스의 환경 변수 확인
pm2 env 0

# 환경 변수에서 DB 관련만 추출
pm2 env 0 | grep -i "DB_\|DATABASE_\|POSTGRES"
```

### 방법 2: 실행 중인 프로세스의 환경 변수 확인

```bash
# PM2 프로세스 ID 확인
pm2 list

# 프로세스의 환경 변수 확인 (PID 사용)
pm2 show 0 | grep -A 30 "env"
```

### 방법 3: 애플리케이션 로그에서 연결 정보 확인

```bash
# PM2 로그 확인
pm2 logs --lines 200 | grep -i "database\|postgres\|connected\|host\|user"

# 또는 최근 로그
tail -100 ~/.pm2/logs/*.log | grep -i "database\|postgres"
```

### 방법 4: PostgreSQL 비밀번호 재설정 또는 확인

```bash
# 로컬 PostgreSQL의 경우 비밀번호 재설정
sudo -u postgres psql

# PostgreSQL에서 실행:
ALTER USER postgres PASSWORD 'new_password';

# 또는 peer 인증으로 직접 접속
sudo -u postgres psql -d smartcompressor_ai
```

### 방법 5: 실행 중인 서비스의 실제 연결 정보 추출

```bash
cd /var/www/smartcompressor

# ecosystem.config.js 확인 (PM2 설정)
cat ecosystem.config.js | grep -A 20 "env"

# 또는
cat ecosystem.config.js | jq '.apps[0].env' 2>/dev/null
```

### 방법 6: RDS 사용 여부 확인

```bash
# AWS 설정 확인
cat ~/.aws/config 2>/dev/null
cat ~/.aws/credentials 2>/dev/null

# 환경 변수에서 RDS 관련 확인
env | grep -i "RDS\|AWS"
```

## 🎯 가장 가능성 높은 해결책

### 1단계: PM2 환경 변수 확인

```bash
pm2 env 0
```

이 명령어로 실제 사용하는 DB 연결 정보를 확인할 수 있습니다.

### 2단계: 확인된 정보로 마이그레이션 실행

```bash
cd /var/www/smartcompressor

# PM2에서 확인한 값으로 설정
export DB_HOST="확인된_HOST"
export DB_USER="확인된_USER"
export DB_NAME="확인된_DB_NAME"
export DB_PASSWORD="확인된_PASSWORD"
export PGPASSWORD="$DB_PASSWORD"

# 마이그레이션 실행
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f database/migrations/20241104180000_add_core_tables_and_improvements.sql
```

### 3단계: 또는 로컬 PostgreSQL 사용 시

```bash
# peer 인증 사용 (로컬 PostgreSQL)
sudo -u postgres psql -d smartcompressor_ai -f /var/www/smartcompressor/database/migrations/20241104180000_add_core_tables_and_improvements.sql
```

## 💡 빠른 확인 명령어

```bash
# 한 번에 확인
echo "=== PM2 환경 변수 ==="
pm2 env 0 | grep -i "DB_\|DATABASE_\|POSTGRES" || echo "없음"

echo ""
echo "=== 시스템 환경 변수 ==="
env | grep -i "DB_\|DATABASE_\|POSTGRES" || echo "없음"

echo ""
echo "=== ecosystem.config.js ==="
cat ecosystem.config.js | grep -A 10 "env" 2>/dev/null || echo "파일 없음"

echo ""
echo "=== PM2 로그 (최근) ==="
pm2 logs --lines 50 --nostream | grep -i "database\|postgres\|connected" | tail -5 || echo "로그 없음"
```

## 🚀 다음 단계

1. **`pm2 env 0` 실행**하여 실제 DB 연결 정보 확인
2. 확인된 정보로 환경 변수 설정
3. 마이그레이션 실행

또는 로컬 PostgreSQL을 사용하는 경우:
```bash
sudo -u postgres psql -d smartcompressor_ai -f /var/www/smartcompressor/database/migrations/20241104180000_add_core_tables_and_improvements.sql
```

