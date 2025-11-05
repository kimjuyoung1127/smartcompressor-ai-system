물론이죠! 아래는 복잡한 내용을 **간결하고 명확하게 정리한 요약본**입니다. 개발자나 기획자가 빠르게 이해할 수 있도록 핵심만 뽑아 정리했습니다.

---

# 🧠 SignalCraft Phase 2 핵심 점검 요약

## ✅ 전체 플로우는 타당
- **큐 → 오디오/피크 로드 → 라벨 편집 → 저장** 흐름은 구조적으로 문제 없음

---

## ⚠️ 주요 개선 필요 항목

### 1. 🔗 엔드포인트 명세 불일치 
- **해결**: 모든 API 경로를 `/api/...` 형식으로 통일 (프론트도 동일하게)

---

### 2. 🔐 인증/세션 전파 방식
- **문제**: `X-User-ID` 헤더 직접 사용은 스푸핑 위험
- **해결**:  
  - Node.js에서 인증 처리 후 내부망으로 Flask에 프록시  
  - Flask는 `X-Internal-User-ID`, `X-Internal-Roles` 등 **내부 전용 헤더만 신뢰**  
  - 외부 요청은 해당 헤더 무시

---

### 3. 🎧 오디오 스트리밍 (Range 지원)
- **문제**: `send_file`만 사용하면 큰 파일 재생 시 끊김
- **해결**: `/api/audio/file/{id}`에서 `Range` 헤더 파싱 → `206 Partial Content`로 응답

---

### 4. 🛡️ 파일 경로 노출
- **문제**: DB의 `file_path`를 클라이언트에 직접 노출
- **해결**: 항상 `/api/audio/file/{id}` 프록시 경로만 반환 (스토리지 경로 숨김)

---

### 5. 📦 큐 응답 필드 누락
- **문제**: 저장 시 필요한 정보(file_name, file_size 등) 누락 가능
- **해결**: `/api/labeling/queue` 응답에 모든 필드 포함 → 프론트는 숨김 필드로 유지

---

### 6. 🔒 동시 편집 락
- **문제**: 두 라벨러가 같은 파일 작업 가능성
- **해결**:  
  - `/api/labeling/lock` API 또는 `/queue` 조회 시 서버가 락 할당  
  - TTL 설정, 저장 시 락 해제

---

### 7. 🧪 메타데이터 검증
- **문제**: 라벨 metadata가 무검증 상태
- **해결**: 서버에서 JSON Schema로 검증 (좌표/시간/주파수 범위, 빈 배열 방지 등)

---

### 8. 🧱 DB 무결성 & 중복 저장 방지
- **DDL 요약**:
  - `labels(audio_file_id, labeler_user_id, status)` → `UNIQUE` (단, `status=final` 조건)
  - FK: `labels.audio_file_id → audio_files.id`, `labeler_user_id → users.id`
  - 저장 성공 시 `audio_files.is_processed = true` 또는 `labeled_by` 상태 업데이트

---

### 9. 📈 Peaks 생성/캐시
- **문제**: 매번 `audiowaveform` 실행은 비효율
- **해결**: 최초 1회 생성 후 ETag/Last-Modified 기반 캐시  
- **명령 예**:
  ```bash
  audiowaveform -i <input> -o <out>.json --pixels-per-second 50 --bits 8
  ```

---

### 10. 🔀 Flask vs Node 배치 전략
- **선택지 A (추천)**: Node → 내부 프록시 → Flask  
  - RBAC 인증은 Node에서 처리  
  - Flask는 내부 요청만 수신 (CORS 비활성, 내부망 전용)

- **선택지 B**: Node에 라벨링 라우트 직접 구현 (단일 스택)  
  - 유지보수는 쉬우나, 기존 구조와 충돌 가능

---

