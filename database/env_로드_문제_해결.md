# .env 파일 로드 문제 해결 가이드

## 🔍 문제 상황

`source .env`를 실행했지만 환경 변수가 로드되지 않습니다.

## ✅ 해결 방법

### 방법 1: .env 파일 형식 확인 및 수동 로드

```bash
cd /var/www/smartcompressor

# 1. .env 파일 내용 확인 (비밀번호는 마스킹)
cat .env | head -20

# 2. .env 파일 형식 확인
file .env

# 3. 수동으로 환경 변수 추출 및 설정
export DB_HOST=$(grep "^DB_HOST" .env | cut -d '=' -f2 | tr -d ' ' | tr -d '"')
export DB_USER=$(grep "^DB_USER" .env | cut -d '=' -f2 | tr -d ' ' | tr -d '"')
export DB_NAME=$(grep "^DB_NAME" .env | cut -d '=' -f2 | tr -d ' ' | tr -d '"')
export DB_PORT=$(grep "^DB_PORT" .env | cut -d '=' -f2 | tr -d ' ' | tr -d '"')
export DB_PASSWORD=$(grep "^DB_PASSWORD" .env | cut -d '=' -f2 | tr -d ' ' | tr -d '"')
export PGPASSWORD="$DB_PASSWORD"

# 4. 환경 변수 확인
echo "DB_HOST: $DB_HOST"
echo "DB_USER: $DB_USER"
echo "DB_NAME: $DB_NAME"
echo "DB_PORT: $DB_PORT"
```

### 방법 2: set -a 사용 (모든 변수 자동 export)

```bash
cd /var/www/smartcompressor

# set -a: 모든 변수를 자동으로 export
set -a
source .env
set +a

# 환경 변수 확인
echo "DB_HOST: $DB_HOST"
echo "DB_USER: $DB_USER"
```

### 방법 3: .env 파일 직접 읽기 및 eval 사용

```bash
cd /var/www/smartcompressor

# .env 파일에서 주석과 빈 줄 제외하고 export
while IFS= read -r line; do
    # 주석과 빈 줄 건너뛰기
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$line" ]] && continue
    
    # export 추가
    if [[ "$line" =~ ^[[:space:]]*([^=]+)=(.*)$ ]]; then
        export "$line"
    fi
done < .env

# 환경 변수 확인
echo "DB_HOST: $DB_HOST"
echo "DB_USER: $DB_USER"
```

### 방법 4: Node.js를 통한 간접 실행 (가장 안전)

```bash
cd /var/www/smartcompressor

# Node.js는 .env 파일을 자동으로 읽을 수 있도록 설정되어 있을 수 있음
# 또는 dotenv 패키지 사용
node database/migrate.js
```

### 방법 5: 직접 값 확인 후 수동 입력

```bash
cd /var/www/smartcompressor

# .env 파일에서 실제 값 확인
cat .env | grep -E '^DB_'

# 직접 값 입력 (예시 - 실제 값으로 교체)
export DB_HOST="localhost"
export DB_USER="postgres"
export DB_NAME="smartcompressor_ai"
export DB_PORT="5432"
export DB_PASSWORD="실제_비밀번호"
export PGPASSWORD="$DB_PASSWORD"
```

## 🔍 .env 파일 확인 명령어

```bash
# .env 파일 존재 확인
ls -la .env

# .env 파일 권한 확인
stat .env

# .env 파일 첫 20줄 확인 (비밀번호는 마스킹)
cat .env | head -20 | sed 's/\(PASSWORD=\).*/\1***/'

# .env 파일에서 DB 관련 변수만 확인
cat .env | grep -E '^DB_' | sed 's/\(PASSWORD=\).*/\1***/'

# .env 파일 인코딩 확인
file .env
```

## 💡 추천 방법

가장 확실한 방법은 **방법 1 (수동 추출)**입니다:

```bash
cd /var/www/smartcompressor

# 한 번에 실행
export DB_HOST=$(grep "^DB_HOST" .env | cut -d '=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'")
export DB_USER=$(grep "^DB_USER" .env | cut -d '=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'")
export DB_NAME=$(grep "^DB_NAME" .env | cut -d '=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'")
export DB_PORT=$(grep "^DB_PORT" .env | cut -d '=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'")
export DB_PASSWORD=$(grep "^DB_PASSWORD" .env | cut -d '=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'")
export PGPASSWORD="$DB_PASSWORD"

# 확인
echo "DB_HOST: $DB_HOST"
echo "DB_USER: $DB_USER"
echo "DB_NAME: $DB_NAME"

# 마이그레이션 실행
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f database/migrations/20241104180000_add_core_tables_and_improvements.sql
```

## 🚨 주의사항

1. `.env` 파일에 특수 문자가 있으면 따옴표 처리 필요
2. Windows 줄바꿈(`\r\n`)이 있으면 문제 발생 가능 → `dos2unix .env` 실행
3. 파일 권한 문제 가능 → `chmod 644 .env` 확인

