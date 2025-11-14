# ✅ 로컬 PostgreSQL 사용 안내

## 확인 완료

✅ **PostgreSQL 16.10** 설치되어 있음  
✅ **PostgreSQL 서비스** 실행 중  
✅ **포트 5432** 사용 중 (localhost에서 리스닝)

## 결론

EC2 서버에 PostgreSQL이 이미 설치되어 있으므로, **RDS가 필요 없습니다!**

`.env` 파일을 `localhost`로 수정하면 됩니다.

---

## 다음 단계

### 1단계: 데이터베이스 정보 확인 (선택사항)

먼저 어떤 데이터베이스와 사용자가 있는지 확인:
```bash
chmod +x check_local_db_info.sh
./check_local_db_info.sh
```

### 2단계: .env 파일 수정

**방법 A: 스크립트 사용 (권장)**

```bash
chmod +x update_env_to_localhost.sh
./update_env_to_localhost.sh
```

스크립트가 다음 정보를 입력받습니다:
- 데이터베이스명 (기본값: signalcraft)
- 사용자명 (기본값: postgres)
- 비밀번호 (postgres 사용자의 비밀번호)

**방법 B: 직접 수정**

EC2 서버에 접속:
```bash
ssh ubuntu@3.39.124.0
cd /home/ubuntu/smartcompressor-ai-system
nano .env
```

다음과 같이 수정:
```env
# Local PostgreSQL Connection Settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=signalcraft
DB_USER=postgres
DB_PASSWORD=설정하신_비밀번호

# Connection Pool Settings
DB_POOL_SIZE=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

---

## 비밀번호를 모르는 경우

postgres 사용자의 비밀번호를 모르신다면:

### 방법 1: 비밀번호 확인
EC2 서버에서:
```bash
sudo -u postgres psql
\password postgres
# 새 비밀번호 입력
\q
```

### 방법 2: 다른 사용자 사용
ubuntu 사용자로 PostgreSQL 접속 (비밀번호 없이):
```bash
# ubuntu 사용자가 PostgreSQL에 접근 가능한지 확인
psql -U ubuntu -d signalcraft
```

가능하면:
```env
DB_USER=ubuntu
DB_PASSWORD=
```

---

## 권장 설정

일반적으로 다음 설정이 작동합니다:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=signalcraft
DB_USER=postgres
DB_PASSWORD=postgres설정한비밀번호
```

또는 비밀번호 없는 접속을 허용하려면 `pg_hba.conf` 설정이 필요할 수 있습니다.

---

## 확인

.env 파일 수정 후:
1. 서버 재시작
2. DB 연결 테스트

```bash
ssh ubuntu@3.39.124.0
cd /home/ubuntu/smartcompressor-ai-system
node -e "require('pg').Pool({host:'localhost',port:5432,database:'signalcraft',user:'postgres',password:'비밀번호'}).query('SELECT 1', (err,res) => console.log(err || '연결 성공!'))"
```

---

**다음 단계로 진행하시겠습니까?** 😊

