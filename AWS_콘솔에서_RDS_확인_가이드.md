# 📋 AWS 콘솔에서 RDS 정보 확인 가이드

## 빠른 확인 방법

### 방법 1: AWS 콘솔에서 확인 (가장 쉬움)

1. **AWS 콘솔 로그인**
   - https://console.aws.amazon.com 접속
   - 대표님 계정으로 로그인

2. **리전 확인**
   - 우측 상단에서 리전 선택
   - EC2 서버가 있는 리전 선택 (위 스크립트로 확인)

3. **RDS 서비스로 이동**
   - 서비스 검색에서 "RDS" 입력
   - RDS 대시보드로 이동

4. **데이터베이스 목록 확인**
   - 왼쪽 메뉴에서 "데이터베이스" 클릭
   - 목록에서 PostgreSQL 데이터베이스 선택

5. **필요한 정보 확인**
   - **엔드포인트** (예: `xxx.us-east-1.rds.amazonaws.com`)
   - **포트** (보통 5432)
   - **마스터 사용자 이름** (DB_USER)
   - **데이터베이스 이름** (DB_NAME)
   - **비밀번호** (설정하신 비밀번호)

### 방법 2: EC2 서버에서 AWS CLI로 확인

EC2 서버에 접속하여:
```bash
ssh ubuntu@3.39.124.0

# 리전 확인
curl http://169.254.169.254/latest/meta-data/placement/region

# AWS CLI로 RDS 목록 확인 (AWS CLI 설정 필요)
aws rds describe-db-instances --region us-east-1
```

## 확인할 정보

다음 정보를 확인하여 .env 파일에 입력해야 합니다:

```env
DB_HOST=확인한_RDS_엔드포인트
DB_PORT=5432
DB_NAME=확인한_데이터베이스_이름
DB_USER=확인한_마스터_사용자_이름
DB_PASSWORD=설정하신_비밀번호
```

## 예시

EC2가 **us-east-1** 리전에 있다면:
```env
DB_HOST=signalcraft.xxxxx.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=signalcraft
DB_USER=postgres
DB_PASSWORD=your_password
```

EC2가 **ap-northeast-2** 리전에 있다면:
```env
DB_HOST=signalcraft.xxxxx.ap-northeast-2.rds.amazonaws.com
DB_PORT=5432
DB_NAME=signalcraft
DB_USER=postgres
DB_PASSWORD=your_password
```

## .env 파일 수정 방법

정보 확인 후, EC2 서버에서:
```bash
ssh ubuntu@3.39.124.0
cd /home/ubuntu/smartcompressor-ai-system

# 백업
cp .env .env.backup

# 편집
nano .env
# 또는
vi .env
```

## 주의사항

⚠️ **리전 일치**: EC2와 RDS가 같은 리전에 있어야 접속 가능  
⚠️ **보안 그룹**: RDS의 보안 그룹이 EC2의 보안 그룹을 허용해야 함  
⚠️ **VPC**: 같은 VPC 또는 VPC 피어링 설정 필요

