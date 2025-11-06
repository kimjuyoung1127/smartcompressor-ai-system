# 데이터베이스 마이그레이션 가이드

## 개요

이 폴더는 데이터베이스 스키마 변경을 관리하는 마이그레이션 파일들을 저장합니다.

## 마이그레이션 파일 명명 규칙

```
YYYYMMDDHHMMSS_description.sql
```

예시:
- `20240115120000_add_user_store_access_table.sql`
- `20240120143000_add_analytics_tables.sql`

## 마이그레이션 파일 구조

```sql
-- Migration: 20240115120000_add_user_store_access_table
-- Description: 사용자 매장 접근 권한 테이블 추가
-- Author: 개발자 이름
-- Date: 2024-01-15

BEGIN;

-- 마이그레이션 SQL 작성
CREATE TABLE IF NOT EXISTS user_store_access (
    user_id INTEGER REFERENCES users(id),
    store_id VARCHAR(50) REFERENCES stores(id),
    permissions JSONB,
    granted_by INTEGER REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    PRIMARY KEY (user_id, store_id)
);

CREATE INDEX IF NOT EXISTS idx_user_store_access_user ON user_store_access(user_id);
CREATE INDEX IF NOT EXISTS idx_user_store_access_store ON user_store_access(store_id);

COMMIT;
```

## 마이그레이션 실행 방법

### 자동 실행 (권장)
```bash
# Node.js 환경에서
node database/migrate.js
```

### 수동 실행
```bash
# PostgreSQL에 직접 실행
psql -U postgres -d smartcompressor_ai -f database/migrations/YYYYMMDDHHMMSS_description.sql
```

## 마이그레이션 작성 시 주의사항

1. **항상 트랜잭션 사용**: `BEGIN`과 `COMMIT`으로 감싸기
2. **IF NOT EXISTS 사용**: 이미 존재하는 테이블/컬럼에 대해 에러 방지
3. **롤백 가능하도록**: 마이그레이션 실패 시 롤백 가능하도록 작성
4. **의존성 확인**: 외래키나 인덱스 추가 시 의존 테이블 확인
5. **데이터 백업**: 중요한 데이터 변경 전 백업 권장

## 마이그레이션 버전 관리

마이그레이션 실행 상태는 `schema_migrations` 테이블에 기록됩니다:

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 새 마이그레이션 추가 방법

1. 새 마이그레이션 파일 생성 (타임스탬프 포함)
2. SQL 작성 (BEGIN/COMMIT 포함)
3. `database/schema.sql` 업데이트 (최신 스키마 반영)
4. 마이그레이션 실행
5. 테스트 및 검증

