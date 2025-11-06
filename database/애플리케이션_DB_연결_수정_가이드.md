# 애플리케이션 DB 연결 수정 가이드

## 🔍 현재 상황

애플리케이션이 실행 중이지만 데이터베이스 연결에 실패하고 있습니다:
```
데이터베이스 초기화 실패: error: password authentication failed for user "postgres"
```

## ✅ 해결 방법

### 방법 1: PostgreSQL 비밀번호 설정 (권장)

애플리케이션이 기본값 `password`를 사용하므로, PostgreSQL에 해당 비밀번호를 설정하세요:

```bash
# PostgreSQL에 접속
sudo -u postgres psql

# PostgreSQL 프롬프트에서:
ALTER USER postgres WITH PASSWORD 'password';
\q

# 애플리케이션 재시작
pm2 restart signalcraft-app
```

### 방법 2: .env 파일에 DB 연결 정보 추가

```bash
cd /var/www/smartcompressor

# .env 파일에 추가
cat >> .env << EOF
DB_HOST=localhost
DB_USER=postgres
DB_NAME=smartcompressor_ai
DB_PORT=5432
DB_PASSWORD=password
EOF

# PM2 재시작 (환경 변수 업데이트)
pm2 restart signalcraft-app --update-env
```

### 방법 3: peer 인증 사용 (로컬 PostgreSQL)

PostgreSQL이 peer 인증을 사용하도록 설정:

```bash
# PostgreSQL 설정 파일 확인
sudo nano /etc/postgresql/*/main/pg_hba.conf

# 다음 줄을 찾아서:
# local   all             postgres                                peer
# 이렇게 변경 (또는 이미 peer로 되어 있으면 그대로)

# PostgreSQL 재시작
sudo systemctl restart postgresql

# 애플리케이션 코드 수정 필요 (database_service.js에서 peer 인증 사용)
```

## 🎯 추천 해결 방법

### 1단계: PostgreSQL 비밀번호 설정

```bash
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'password';"
```

### 2단계: 연결 테스트

```bash
export PGPASSWORD="password"
psql -h localhost -U postgres -d smartcompressor_ai -c "SELECT version();"
unset PGPASSWORD
```

### 3단계: 애플리케이션 재시작

```bash
pm2 restart signalcraft-app
```

### 4단계: 로그 확인

```bash
pm2 logs signalcraft-app --lines 50 | grep -i "database\|postgres\|초기화"
```

## 📋 확인 사항

### 애플리케이션이 정상 작동하는지 확인

```bash
# PM2 상태
pm2 list

# 애플리케이션 로그 (에러 없는지 확인)
pm2 logs signalcraft-app --lines 100 --err

# 데이터베이스 연결 성공 메시지 확인
pm2 logs signalcraft-app --lines 50 | grep -i "초기화 완료\|데이터베이스"
```

## ⚠️ 주의사항

1. **비밀번호 보안**: 프로덕션 환경에서는 강력한 비밀번호 사용
2. **환경 변수**: .env 파일에 DB 정보를 추가하는 것이 안전
3. **재시작**: 환경 변수 변경 후 PM2 재시작 필요

