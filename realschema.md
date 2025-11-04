

# 📦 smartcompressor_ai 스키마 구조 요약

---

## 📂 전체 테이블 분류

| 영역           | 테이블 목록                                      |
|----------------|--------------------------------------------------|
| 사용자/권한    | `users`, `sessions`, `user_store_access`, `stores` |
| 디바이스/수집 | `devices`, `sensor_readings`, `monitoring_data`, `sensor_statistics` |
| 오디오/AI      | `audio_files`, `ai_analysis_results`, `anomalies` |
| 라벨링/전문가 | `labels`, `labeling_stats`, `experts`             |

---

## 👤 사용자/스토어/세션

### `users`
- **PK**: `id` (serial)
- **핵심 컬럼**: `username`, `email` (UNIQUE), `password_hash`, `role` (`user` 기본), `is_active`
- **타임스탬프**: `created_at`, `updated_at`, `last_login`, `deleted_at`
- **인덱스**: `email`, `username`, `role`
- **참조됨**: `sessions`, `stores`, `user_store_access`, `audio_files`, `monitoring_data`, `anomalies`, `ai_analysis_results`

### `sessions`
- **PK**: `id` (serial)
- **핵심 컬럼**: `session_id` (UNIQUE), `user_id` (FK), `expires_at`, `ip_address`, `user_agent`
- **인덱스**: `session_id`, `user_id`, `expires_at`

### `stores`
- **PK**: `id` (varchar(50))
- **핵심 컬럼**: `name`, `owner_id` (FK), `is_active`, 타임스탬프
- **참조됨**: `devices`, `audio_files`, `monitoring_data`, `user_store_access`

### `user_store_access`
- **PK**: 복합키 (`user_id`, `store_id`)
- **핵심 컬럼**: `permissions` (jsonb), `granted_by` (FK), `granted_at`, `expires_at`
- **FK**: `user_id` → `users`, `store_id` → `stores`

---

## 🔧 디바이스/수집/통계

### `devices`
- **PK**: `id` (varchar(50))
- **핵심 컬럼**: `store_id` (FK), `device_type`, `status`, `device_name`, `firmware_version`, 타임스탬프
- **참조됨**: `sensor_readings`, `sensor_statistics`, `monitoring_data`, `audio_files`, `anomalies`

### `sensor_readings` (원시 데이터)
- **PK**: `id` (serial)
- **핵심 컬럼**: `device_id` (FK), `timestamp`, `temperature`, `vibration_x/y/z`, `power_consumption`, `audio_level`, `metadata` (jsonb)
- **인덱스**: `device_id`, `timestamp`, `(device_id, timestamp)`

### `monitoring_data` (요약 데이터)
- **PK**: `id` (serial)
- **핵심 컬럼**: `user_id`, `store_id`, `device_id`, `temperature`, `vibration_level`, `power_consumption`, `audio_level`, `status`, `timestamp`
- **인덱스**: `user_id`, `timestamp`, `(store_id, device_id)`

### `sensor_statistics` (시간/일 단위 통계)
- **PK**: `id` (serial)
- **핵심 컬럼**: `device_id`, `date`, `hour`, 평균/최대/최소 값들, `anomaly_count`
- **제약조건**: `UNIQUE(device_id, date, hour)`
- **인덱스**: `device_id`, `date`, `(device_id, date)`

---

## 🎧 오디오/AI/이상징후

### `audio_files`
- **PK**: `id` (serial)
- **핵심 컬럼**: `user_id`, `store_id`, `device_id`, `file_name`, `file_path`, `file_size`, `duration_seconds`, `sample_rate`, `format`, `upload_timestamp`, `is_processed`
- **인덱스**: `user_id`, `store_id`, `upload_timestamp`
- **참조됨**: `ai_analysis_results`

### `ai_analysis_results`
- **PK**: `id` (serial)
- **핵심 컬럼**: `audio_file_id`, `user_id`, `is_overload`, `confidence`, `analysis_timestamp`
- **부가 정보**: `model_info`, `features_extracted`, `quality_metrics`, `optimization_info`, `noise_info` (모두 JSONB)
- **인덱스**: `audio_file_id`, `user_id`, `analysis_timestamp`

### `anomalies`
- **PK**: `id` (serial)
- **핵심 컬럼**: `device_id`, `timestamp`, `anomaly_type`, `severity`, `confidence`, `is_resolved`, `resolved_by`, `sensor_data` (jsonb)
- **인덱스**: `device_id`, `timestamp`, `anomaly_type`, `severity`, `is_resolved`

---

## 🏷️ 라벨링/전문가

### `labels`
- **PK**: `id` (serial)
- **핵심 컬럼**: `file_name`, `label`, `confidence`, `labeler_id`
- **부가 정보**: `file_hash` (UNIQUE), `metadata` (jsonb), `store_id`, `device_id`, 타임스탬프
- **인덱스**: `file_hash`, `label`, `labeler_id`, `store_id`, `created_at`, `metadata` (GIN)
- **트리거**: `update_labels_updated_at` (자동 갱신)

### `labeling_stats`
- **PK**: `id` (serial)
- **핵심 컬럼**: `date`, `total_labeled`, `normal_count`, `warning_count`, `critical_count`, `unknown_count`, `avg_confidence`
- **제약조건**: `UNIQUE(date)`

### `experts`
- **PK**: `id` (varchar(50))
- **핵심 컬럼**: `name`, `email`, `role`, `is_active`, `created_at`, `last_active`, `deleted_at`

---

## 🔗 핵심 관계 흐름 (Foreign Key)

- `users` → `sessions`, `stores`, `user_store_access`, `audio_files`, `monitoring_data`, `anomalies`, `ai_analysis_results`
- `stores` → `devices`, `audio_files`, `monitoring_data`, `user_store_access`
- `devices` → `sensor_readings`, `sensor_statistics`, `monitoring_data`, `audio_files`, `anomalies`
- `audio_files` → `ai_analysis_results`

---

