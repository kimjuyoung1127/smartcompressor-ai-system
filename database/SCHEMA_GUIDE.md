# 데이터베이스 스키마 정의 가이드

## 📖 개발자 요청에 대한 답변

개발자가 요청한 내용:
> "데이터베이스에 들어갈 스키마는 service/database_service.js 외에 따로 정하신게 있으실까요? 스키마를 잘 정의하면 개발속도가 빠르고 중간에 변경할것이 적어서 좋을것같습니다"

## ✅ 현재 상황

### 문제점
1. **스키마 분산**: 스키마가 여러 파일에 분산되어 있음
   - `services/database_service.js` - PostgreSQL 메인 스키마
   - `services/sqlite_database_service.js` - SQLite 스키마  
   - 각 Python 서비스 파일들 (`user_permission_service.py`, `sensor_data_service.py` 등)

2. **관리 어려움**
   - 스키마 변경 시 여러 파일 수정 필요
   - 버전 관리 및 일관성 유지 어려움
   - 마이그레이션 시스템 없음

### 해결책
중앙화된 스키마 관리 시스템을 구축했습니다:

## 📁 새로운 구조

```
database/
├── schema.sql              # ✅ 단일 소스 스키마 정의
├── migrations/             # ✅ 스키마 변경 이력 관리
│   ├── README.md
│   └── YYYYMMDDHHMMSS_*.sql
├── migrate.js              # ✅ 마이그레이션 실행 스크립트
├── README.md              # ✅ 전체 가이드
└── SCHEMA_GUIDE.md        # ✅ 이 파일
```

## 🎯 스키마 정의 원칙

### 1. 단일 소스 원칙 (Single Source of Truth)
- **`database/schema.sql`**이 모든 스키마의 단일 소스입니다
- 모든 스키마 변경은 이 파일에서 시작합니다
- 서비스 파일들은 이 스키마를 참조합니다

### 2. 마이그레이션 기반 변경
- 스키마 변경은 마이그레이션 파일로 관리
- 각 변경은 타임스탬프와 함께 기록
- 롤백 가능하도록 설계

### 3. 버전 관리
- Git으로 모든 변경 추적
- 변경 이력은 마이그레이션 파일로 확인

## 🚀 사용 방법

### 스키마 확인
```bash
# 메인 스키마 파일 확인
cat database/schema.sql
```

### 스키마 적용
```bash
# PostgreSQL에 스키마 적용
psql -U postgres -d smartcompressor_ai -f database/schema.sql
```

### 스키마 변경
1. `database/schema.sql` 수정
2. 마이그레이션 파일 생성 (필요시)
3. `node database/migrate.js` 실행
4. 테스트

## 📝 스키마 정의 예시

### 테이블 추가 시

**1. schema.sql에 추가**
```sql
-- 새 테이블 정의
CREATE TABLE IF NOT EXISTS user_store_access (
    user_id INTEGER REFERENCES users(id),
    store_id VARCHAR(50) REFERENCES stores(id),
    permissions JSONB,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, store_id)
);
```

**2. 마이그레이션 파일 생성 (선택사항)**
```bash
# database/migrations/20240115120000_add_user_store_access.sql
```

**3. 서비스 파일에서 사용**
```javascript
// services/database_service.js
// 스키마는 자동으로 schema.sql에서 읽어옵니다
```

## 🔄 기존 코드와의 호환성

`services/database_service.js`는 이제 `database/schema.sql`을 읽어서 사용합니다:

```javascript
// 기존: 하드코딩된 스키마
await client.query(`CREATE TABLE IF NOT EXISTS users (...)`);

// 변경 후: 스키마 파일에서 읽기
const schemaSQL = fs.readFileSync('database/schema.sql', 'utf8');
await client.query(schemaSQL);
```

## ✅ 장점

1. **개발 속도 향상**
   - 스키마 한 곳에서 확인 가능
   - 변경 시 한 파일만 수정
   - 중복 코드 제거

2. **일관성 유지**
   - 모든 서비스가 동일한 스키마 참조
   - 버전 불일치 방지

3. **변경 관리 용이**
   - 마이그레이션으로 변경 이력 추적
   - 롤백 가능
   - 팀 협업 용이

4. **문서화 자동화**
   - 스키마 파일 자체가 문서
   - 주석으로 설명 추가 가능

## 📚 다음 단계

1. ✅ 스키마 파일 생성 완료
2. ✅ 마이그레이션 시스템 구축 완료
3. ✅ database_service.js 수정 완료
4. ⏳ 다른 서비스 파일들도 스키마 파일 참조하도록 수정 (필요시)
5. ⏳ 개발팀에 스키마 관리 가이드 공유

## 🤝 개발자에게 전달할 메시지

> 네, 맞습니다! 스키마를 중앙에서 관리하는 것이 훨씬 좋습니다. 
> 
> 이제 모든 스키마는 **`database/schema.sql`** 파일에 정의되어 있습니다.
> 
> **사용 방법:**
> - 스키마 확인: `database/schema.sql` 파일 열기
> - 스키마 변경: `database/schema.sql` 수정 후 마이그레이션 실행
> - 마이그레이션 실행: `node database/migrate.js`
> 
> 스키마 변경 시 이 파일만 수정하면 되고, `database_service.js`는 자동으로 이 스키마를 사용합니다.
> 
> 자세한 내용은 `database/README.md`를 참고하세요!

