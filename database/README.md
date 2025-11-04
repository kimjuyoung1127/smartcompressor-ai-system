# 데이터베이스 스키마 관리

## 📋 개요

이 디렉토리는 SmartCompressor AI 시스템의 데이터베이스 스키마를 중앙에서 관리합니다.

## 📁 파일 구조

```
database/
├── schema.sql              # 메인 스키마 파일 (단일 소스)
├── migrations/             # 마이그레이션 파일들
│   ├── README.md          # 마이그레이션 가이드
│   └── YYYYMMDDHHMMSS_*.sql
├── migrate.js              # 마이그레이션 실행 스크립트
├── smartcompressor.db      # SQLite 데이터베이스 (로컬 개발용)
└── README.md              # 이 파일
```

## 🎯 스키마 관리 원칙

### 1. 단일 소스 원칙 (Single Source of Truth)
- **`schema.sql`**이 모든 스키마 정의의 단일 소스입니다
- 스키마 변경 시 이 파일을 먼저 수정합니다
- 다른 서비스 파일들은 이 스키마를 참조합니다

### 2. 마이그레이션 기반 변경
- 스키마 변경은 마이그레이션 파일로 관리합니다
- 각 변경은 타임스탬프와 함께 기록됩니다
- 롤백 가능하도록 설계합니다

### 3. 버전 관리
- 모든 스키마 변경은 Git으로 추적됩니다
- 변경 이력은 마이그레이션 파일로 확인 가능합니다

## 🚀 사용 방법

### 초기 스키마 생성

```bash
# PostgreSQL에 스키마 생성
psql -U postgres -d smartcompressor_ai -f database/schema.sql
```

### 마이그레이션 실행

```bash
# 대기 중인 모든 마이그레이션 실행
node database/migrate.js

# 마이그레이션 상태 확인
node database/migrate.js --status
```

### 새 마이그레이션 추가

1. `database/migrations/` 폴더에 새 마이그레이션 파일 생성
2. 파일명: `YYYYMMDDHHMMSS_description.sql`
3. SQL 작성 (BEGIN/COMMIT 포함)
4. `schema.sql` 업데이트 (최신 상태 유지)
5. 마이그레이션 실행 및 테스트

## 📝 현재 스키마 구조

### 주요 테이블

1. **사용자 관리**
   - `users` - 사용자 정보
   
2. **매장 및 장치**
   - `stores` - 매장 정보
   - `devices` - 장치 정보

3. **라벨링**
   - `labels` - 라벨링 데이터
   - `experts` - 전문가 정보
   - `labeling_stats` - 라벨링 통계

4. **오디오 및 AI 분석**
   - `audio_files` - 오디오 파일 메타데이터
   - `ai_analysis_results` - AI 분석 결과

5. **모니터링**
   - `monitoring_data` - 실시간 모니터링 데이터

## 🔧 개발자 가이드

### 스키마 변경 시 체크리스트

- [ ] `database/schema.sql` 업데이트
- [ ] 새 마이그레이션 파일 생성 (필요시)
- [ ] 인덱스 추가/수정 확인
- [ ] 외래키 관계 확인
- [ ] 테스트 환경에서 마이그레이션 테스트
- [ ] 프로덕션 배포 전 백업
- [ ] 문서 업데이트

### 서비스 파일에서 스키마 사용

**기존 방식 (비권장):**
```javascript
// services/database_service.js
await client.query(`
    CREATE TABLE IF NOT EXISTS users (...)
`);
```

**권장 방식:**
```javascript
// services/database_service.js
const fs = require('fs');
const path = require('path');

async createTables() {
    const schema = fs.readFileSync(
        path.join(__dirname, '../database/schema.sql'),
        'utf8'
    );
    await client.query(schema);
}
```

## 📚 참고 자료

- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)
- [마이그레이션 가이드](./migrations/README.md)

## ⚠️ 주의사항

1. **프로덕션 배포 전**: 항상 백업을 수행하세요
2. **마이그레이션 순서**: 타임스탬프 순서대로 실행됩니다
3. **롤백 계획**: 마이그레이션 실패 시 롤백 방법을 미리 준비하세요
4. **의존성**: 외래키나 인덱스 추가 시 의존 테이블 확인 필수

## 🤝 기여 가이드

스키마 변경 제안 시:
1. 이슈 생성 또는 PR 작성
2. 변경 이유 및 영향 범위 설명
3. 마이그레이션 파일 포함
4. 테스트 결과 첨부

