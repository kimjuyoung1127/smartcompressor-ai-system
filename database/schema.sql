-- =====================================================
-- SmartCompressor AI System - Database Schema
-- =====================================================
-- 이 파일은 전체 데이터베이스 스키마의 단일 소스입니다.
-- 스키마 변경 시 이 파일만 수정하면 됩니다.
-- 
-- 마이그레이션: database/migrations/ 폴더 사용
-- 버전 관리: 각 마이그레이션은 타임스탬프와 함께 관리됩니다.
-- =====================================================

-- =====================================================
-- 1. 사용자 관리 테이블
-- =====================================================

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'user',
    additional_info JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- =====================================================
-- 2. 매장 및 장치 관리 테이블
-- =====================================================

-- 매장 테이블
CREATE TABLE IF NOT EXISTS stores (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    owner_id INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 장치 테이블
CREATE TABLE IF NOT EXISTS devices (
    id VARCHAR(50) PRIMARY KEY,
    store_id VARCHAR(50) REFERENCES stores(id) ON DELETE CASCADE,
    device_type VARCHAR(50) DEFAULT 'compressor',
    device_name VARCHAR(100),
    location VARCHAR(100),
    firmware_version VARCHAR(50),
    hardware_version VARCHAR(50),
    last_seen TIMESTAMP,
    status VARCHAR(20) DEFAULT 'offline',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 3. 라벨링 및 전문가 관리 테이블
-- =====================================================

-- 라벨링 테이블
CREATE TABLE IF NOT EXISTS labels (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(50),
    file_hash VARCHAR(64) UNIQUE,
    label VARCHAR(20) NOT NULL CHECK (label IN ('normal', 'warning', 'critical', 'unknown')),
    confidence INTEGER NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    notes TEXT,
    labeler_id VARCHAR(50) NOT NULL,
    store_id VARCHAR(50),
    device_id VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 전문가 테이블
CREATE TABLE IF NOT EXISTS experts (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(50) DEFAULT 'labeler',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 라벨링 통계 테이블
CREATE TABLE IF NOT EXISTS labeling_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_labeled INTEGER DEFAULT 0,
    normal_count INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    critical_count INTEGER DEFAULT 0,
    unknown_count INTEGER DEFAULT 0,
    avg_confidence DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 4. 오디오 파일 및 AI 분석 테이블
-- =====================================================

-- 오디오 파일 메타데이터 테이블
CREATE TABLE IF NOT EXISTS audio_files (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    store_id VARCHAR(50) REFERENCES stores(id),
    device_id VARCHAR(50) REFERENCES devices(id),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    duration_seconds DECIMAL(10, 2),
    sample_rate INTEGER,
    channels INTEGER,
    format VARCHAR(20),
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_processed BOOLEAN DEFAULT false
);

-- AI 분석 결과 테이블
CREATE TABLE IF NOT EXISTS ai_analysis_results (
    id SERIAL PRIMARY KEY,
    audio_file_id INTEGER REFERENCES audio_files(id),
    user_id INTEGER REFERENCES users(id),
    is_overload BOOLEAN NOT NULL,
    confidence DECIMAL(5, 4) NOT NULL,
    processing_time_ms INTEGER,
    model_info JSONB,
    features_extracted JSONB,
    quality_metrics JSONB,
    optimization_info JSONB,
    noise_info JSONB,
    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message TEXT
);

-- =====================================================
-- 5. 인증 및 세션 관리 테이블
-- =====================================================

-- 세션 테이블
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 사용자 매장 접근 권한 테이블
CREATE TABLE IF NOT EXISTS user_store_access (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    store_id VARCHAR(50) REFERENCES stores(id) ON DELETE CASCADE,
    permissions JSONB DEFAULT '{}',
    granted_by INTEGER REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    PRIMARY KEY (user_id, store_id)
);

-- =====================================================
-- 6. 센서 데이터 및 이상 감지 테이블
-- =====================================================

-- 센서 데이터 테이블 (시계열 데이터)
CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) REFERENCES devices(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    temperature DECIMAL(5, 2),
    vibration_x DECIMAL(8, 4),
    vibration_y DECIMAL(8, 4),
    vibration_z DECIMAL(8, 4),
    power_consumption DECIMAL(8, 2),
    audio_level DECIMAL(8, 4),
    sensor_quality DECIMAL(5, 2),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 이상 감지 테이블
CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) REFERENCES devices(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    anomaly_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    confidence DECIMAL(5, 2) NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    description TEXT,
    sensor_data JSONB,
    is_resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP,
    resolved_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 센서 통계 테이블 (집계 데이터)
CREATE TABLE IF NOT EXISTS sensor_statistics (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) REFERENCES devices(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    hour INTEGER NOT NULL CHECK (hour >= 0 AND hour <= 23),
    avg_temperature DECIMAL(5, 2),
    max_temperature DECIMAL(5, 2),
    min_temperature DECIMAL(5, 2),
    avg_vibration DECIMAL(8, 4),
    max_vibration DECIMAL(8, 4),
    avg_power_consumption DECIMAL(8, 2),
    max_power_consumption DECIMAL(8, 2),
    anomaly_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(device_id, date, hour)
);

-- =====================================================
-- 7. 모니터링 데이터 테이블
-- =====================================================

-- 실시간 모니터링 데이터 테이블
CREATE TABLE IF NOT EXISTS monitoring_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    store_id VARCHAR(50) REFERENCES stores(id),
    device_id VARCHAR(50) REFERENCES devices(id),
    temperature DECIMAL(5, 2),
    vibration_level DECIMAL(8, 4),
    power_consumption DECIMAL(8, 2),
    audio_level DECIMAL(8, 4),
    status VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 6. 인덱스 생성
-- =====================================================

-- 라벨링 관련 인덱스
CREATE INDEX IF NOT EXISTS idx_labels_timestamp ON labels(created_at);
CREATE INDEX IF NOT EXISTS idx_labels_label ON labels(label);
CREATE INDEX IF NOT EXISTS idx_labels_labeler ON labels(labeler_id);
CREATE INDEX IF NOT EXISTS idx_labels_store ON labels(store_id);
CREATE INDEX IF NOT EXISTS idx_labels_file_hash ON labels(file_hash);
CREATE INDEX IF NOT EXISTS idx_labels_metadata ON labels USING GIN(metadata);

-- 사용자 관련 인덱스
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- 오디오 파일 관련 인덱스
CREATE INDEX IF NOT EXISTS idx_audio_files_user ON audio_files(user_id);
CREATE INDEX IF NOT EXISTS idx_audio_files_store ON audio_files(store_id);
CREATE INDEX IF NOT EXISTS idx_audio_files_timestamp ON audio_files(upload_timestamp);

-- AI 분석 결과 관련 인덱스
CREATE INDEX IF NOT EXISTS idx_ai_results_audio_file ON ai_analysis_results(audio_file_id);
CREATE INDEX IF NOT EXISTS idx_ai_results_user ON ai_analysis_results(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_results_timestamp ON ai_analysis_results(analysis_timestamp);

-- 세션 관련 인덱스
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);

-- 사용자 매장 접근 권한 관련 인덱스
CREATE INDEX IF NOT EXISTS idx_user_store_access_user ON user_store_access(user_id);
CREATE INDEX IF NOT EXISTS idx_user_store_access_store ON user_store_access(store_id);

-- 센서 데이터 관련 인덱스
CREATE INDEX IF NOT EXISTS idx_sensor_readings_device ON sensor_readings(device_id);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_timestamp ON sensor_readings(device_id, timestamp);

-- 이상 감지 관련 인덱스
CREATE INDEX IF NOT EXISTS idx_anomalies_device ON anomalies(device_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomalies_type ON anomalies(anomaly_type);
CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity);
CREATE INDEX IF NOT EXISTS idx_anomalies_resolved ON anomalies(is_resolved);

-- 센서 통계 관련 인덱스
CREATE INDEX IF NOT EXISTS idx_sensor_statistics_device ON sensor_statistics(device_id);
CREATE INDEX IF NOT EXISTS idx_sensor_statistics_date ON sensor_statistics(date);
CREATE INDEX IF NOT EXISTS idx_sensor_statistics_device_date ON sensor_statistics(device_id, date);

-- 모니터링 데이터 관련 인덱스
CREATE INDEX IF NOT EXISTS idx_monitoring_user ON monitoring_data(user_id);
CREATE INDEX IF NOT EXISTS idx_monitoring_timestamp ON monitoring_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_monitoring_store_device ON monitoring_data(store_id, device_id);

-- =====================================================
-- 7. 트리거 및 함수
-- =====================================================

-- updated_at 자동 업데이트 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- labels 테이블 updated_at 자동 업데이트 트리거
DROP TRIGGER IF EXISTS update_labels_updated_at ON labels;
CREATE TRIGGER update_labels_updated_at
    BEFORE UPDATE ON labels
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- users 테이블 updated_at 자동 업데이트 트리거
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- stores 테이블 updated_at 자동 업데이트 트리거
DROP TRIGGER IF EXISTS update_stores_updated_at ON stores;
CREATE TRIGGER update_stores_updated_at
    BEFORE UPDATE ON stores
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- devices 테이블 updated_at 자동 업데이트 트리거
DROP TRIGGER IF EXISTS update_devices_updated_at ON devices;
CREATE TRIGGER update_devices_updated_at
    BEFORE UPDATE ON devices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 8. 기존 테이블에 컬럼 추가 (호환성 유지)
-- =====================================================

-- users 테이블에 additional_info 컬럼 추가 (이미 있으면 무시)
ALTER TABLE users ADD COLUMN IF NOT EXISTS additional_info JSONB;

-- =====================================================
-- 9. 표준 필드 추가 (소프트 삭제 등)
-- =====================================================

-- 소프트 삭제를 위한 deleted_at 컬럼 추가
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE devices ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE labels ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE experts ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE audio_files ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;

