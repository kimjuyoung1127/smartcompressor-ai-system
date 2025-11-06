# 🔧 .env 파일 수정 안내

## 현재 상황

**EC2 서버**: 3.39.124.0  
**현재 .env 파일의 DB**: ap-northeast-2 (서울 리전) - 김주영님의 계정 DB

**문제**: 
- EC2 서버와 DB가 다른 리전에 있으면 접속 불가
- EC2가 us-east-1에 있다면, us-east-1의 DB가 필요

## 확인 절차

### 1단계: EC2 서버 리전 확인

WSL 터미널에서 실행:
```bash
chmod +x check_ec2_region_and_db.sh
./check_ec2_region_and_db.sh
```

또는 직접 EC2에 접속하여:
```bash
ssh ubuntu@3.39.124.0
curl http://169.254.169.254/latest/meta-data/placement/region
```

### 2단계: 올바른 DB 정보 확인

#### 만약 EC2가 **us-east-1**이면:
```env
# AWS RDS PostgreSQL Connection Settings (us-east-1)
DB_HOST=your-rds-endpoint.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=signalcraft
DB_USER=your_user
DB_PASSWORD=your_password

# Connection Pool Settings
DB_POOL_SIZE=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

#### 만약 EC2가 **ap-northeast-2** (서울)이면:
현재 설정이 맞을 수 있지만, **대표님 계정의 RDS 정보**로 교체 필요:
```env
# AWS RDS PostgreSQL Connection Settings (ap-northeast-2)
DB_HOST=대표님_RDS_엔드포인트.ap-northeast-2.rds.amazonaws.com
DB_PORT=5432
DB_NAME=signalcraft
DB_USER=대표님_사용자명
DB_PASSWORD=대표님_비밀번호

# Connection Pool Settings
DB_POOL_SIZE=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

## .env 파일 수정 방법

### EC2 서버에서 직접 수정:

```bash
ssh ubuntu@3.39.124.0
cd /home/ubuntu/smartcompressor-ai-system

# 백업
cp .env .env.backup_$(date +%Y%m%d)

# 편집
nano .env
# 또는
vi .env
```

### 올바른 .env 파일 내용 예시 (us-east-1 기준):

```env
# AWS RDS PostgreSQL Connection Settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=signalcraft
DB_USER=signalcraft_user
DB_PASSWORD=your_secure_password

# Connection Pool Settings
DB_POOL_SIZE=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

**또는**

```env
# AWS RDS PostgreSQL Connection Settings
DB_HOST=your-rds-instance.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=signalcraft
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Connection Pool Settings
DB_POOL_SIZE=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

## 확인 사항

1. ✅ **EC2 리전 확인** (위 스크립트 실행)
2. ✅ **RDS 엔드포인트 확인** (AWS 콘솔에서 확인)
3. ✅ **보안 그룹 설정 확인** (EC2와 RDS가 같은 VPC 또는 통신 가능한지)
4. ✅ **사용자명/비밀번호 확인** (대표님 계정 정보)

## AWS 콘솔에서 RDS 정보 확인 방법

1. AWS 콘솔 로그인
2. RDS 서비스로 이동
3. 데이터베이스 선택
4. **엔드포인트** 확인 (예: `xxx.us-east-1.rds.amazonaws.com`)
5. **데이터베이스 이름** 확인
6. **마스터 사용자 이름** 확인

## 주의사항

⚠️ **보안**: `.env` 파일에는 비밀번호가 평문으로 저장됩니다.  
⚠️ **리전 불일치**: EC2와 RDS가 다른 리전이면 같은 VPC가 아니므로 접속 불가합니다.  
⚠️ **보안 그룹**: RDS의 보안 그룹이 EC2의 보안 그룹에서 오는 트래픽을 허용해야 합니다.

## 다음 단계

1. `check_ec2_region_and_db.sh` 실행하여 EC2 리전 확인
2. 대표님에게 올바른 RDS 정보 요청
3. `.env` 파일 수정
4. 서버 재시작 및 연결 테스트

