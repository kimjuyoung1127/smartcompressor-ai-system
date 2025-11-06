# 📋 RDS 정보 확인 요청

## 현재 상황

✅ **EC2 서버 리전 확인 완료**: `ap-northeast-2` (서울)  
📍 **EC2 호스트명**: `ec2-3-39-124-0.ap-northeast-2.compute.amazonaws.com`

**결론**: EC2와 DB가 같은 리전(서울)이므로 리전 문제는 아닙니다.

## 문제 원인 추정

현재 .env 파일에는 김주영님 계정의 DB가 설정되어 있습니다:
- DB_HOST: `signalcraft.cb8e6ea8w70p.ap-northeast-2.rds.amazonaws.com`
- DB_USER: `jason`
- DB_PASSWORD: `suhocjstk`

이 DB가 접속되지 않는 이유는:
1. **대표님 계정의 RDS가 아닐 수 있음**
2. **보안 그룹 설정 문제** (EC2와 RDS가 통신 불가)
3. **VPC 설정 문제**

## 필요한 정보

AWS 콘솔에서 다음 정보를 확인해주세요:

### 1. RDS 인스턴스 정보
- **엔드포인트** (Endpoint)
  - 예: `xxx.ap-northeast-2.rds.amazonaws.com`
- **포트** (보통 5432)
- **마스터 사용자 이름**
- **데이터베이스 이름**

### 2. 확인 방법
1. AWS 콘솔 → **서울 리전 (ap-northeast-2)** 선택
2. RDS 서비스 → 데이터베이스
3. PostgreSQL 인스턴스 선택
4. 연결 및 보안 탭에서 위 정보 확인

## .env 파일 수정 방법

### 방법 1: 스크립트 사용 (권장)

RDS 정보를 확인하신 후:
```bash
chmod +x update_env_file.sh
./update_env_file.sh
```

스크립트가 정보를 입력받아 자동으로 .env 파일을 업데이트합니다.

### 방법 2: 직접 수정

EC2 서버에 접속하여:
```bash
ssh ubuntu@3.39.124.0
cd /home/ubuntu/smartcompressor-ai-system

# 백업
cp .env .env.backup

# 편집
nano .env
```

다음 형식으로 수정:
```env
# AWS RDS PostgreSQL Connection Settings
DB_HOST=확인한_엔드포인트
DB_PORT=5432
DB_NAME=확인한_데이터베이스명
DB_USER=확인한_사용자명
DB_PASSWORD=설정하신_비밀번호

# Connection Pool Settings
DB_POOL_SIZE=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

## 보안 그룹 확인

.env 파일 수정 후에도 접속이 안 되면:

1. AWS 콘솔 → RDS → 데이터베이스 → 보안
2. VPC 보안 그룹 확인
3. 인바운드 규칙에서:
   - 타입: PostgreSQL
   - 포트: 5432
   - 소스: EC2의 보안 그룹 또는 EC2의 IP

## 다음 단계

1. ✅ AWS 콘솔에서 RDS 정보 확인 (서울 리전)
2. ⏳ 확인한 정보를 알려주시면 .env 파일 수정 도와드립니다
3. ⏳ 보안 그룹 확인 (필요한 경우)

---

**참고**: RDS 정보를 확인하신 후 알려주시면 바로 올바른 .env 파일 내용을 작성해드리겠습니다!

