-- Migration: 20241104180000_add_core_tables_and_improvements
-- Description: 핵심 테이블 추가 및 스키마 개선
-- Author: System
-- Date: 2024-11-04

BEGIN;

-- =====================================================
-- 1. 세션 관리 테이블 추가
-- =====================================================

CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);

-- =====================================================
-- 2. 사용자 매장 접근 권한 테이블 추가
-- =====================================================

CREATE TABLE IF NOT EXISTS user_store_access (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    store_id VARCHAR(50) REFERENCES stores(id) ON DELETE CASCADE,
    permissions JSONB DEFAULT '{}',
    granted_by INTEGER REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    PRIMARY KEY (user_id, store_id)
);

CREATE INDEX IF NOT EXISTS idx_user_store_access_user ON user_store_access(user_id);
CREATE INDEX IF NOT EXISTS idx_user_store_access_store ON user_store_access(store_id);

-- =====================================================
-- 3. 센서 데이터 테이블 추가
-- =====================================================

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

CREATE INDEX IF NOT EXISTS idx_sensor_readings_device ON sensor_readings(device_id);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_timestamp ON sensor_readings(device_id, timestamp);

-- =====================================================
-- 4. 이상 감지 테이블 추가
-- =====================================================

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

CREATE INDEX IF NOT EXISTS idx_anomalies_device ON anomalies(device_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomalies_type ON anomalies(anomaly_type);
CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity);
CREATE INDEX IF NOT EXISTS idx_anomalies_resolved ON anomalies(is_resolved);

-- =====================================================
-- 5. 센서 통계 테이블 추가
-- =====================================================

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

CREATE INDEX IF NOT EXISTS idx_sensor_statistics_device ON sensor_statistics(device_id);
CREATE INDEX IF NOT EXISTS idx_sensor_statistics_date ON sensor_statistics(date);
CREATE INDEX IF NOT EXISTS idx_sensor_statistics_device_date ON sensor_statistics(device_id, date);

-- =====================================================
-- 6. 기존 테이블 수정 (외래키 및 타입 통일)
-- =====================================================

-- stores 테이블: owner_id를 INTEGER로 변경하고 외래키 추가
ALTER TABLE stores 
    ALTER COLUMN owner_id TYPE INTEGER USING owner_id::INTEGER,
    ADD CONSTRAINT fk_stores_owner FOREIGN KEY (owner_id) REFERENCES users(id);

-- stores 테이블에 updated_at 추가
ALTER TABLE stores ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- devices 테이블에 추가 필드 추가
ALTER TABLE devices ADD COLUMN IF NOT EXISTS device_name VARCHAR(100);
ALTER TABLE devices ADD COLUMN IF NOT EXISTS firmware_version VARCHAR(50);
ALTER TABLE devices ADD COLUMN IF NOT EXISTS hardware_version VARCHAR(50);
ALTER TABLE devices ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP;
ALTER TABLE devices ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'offline';
ALTER TABLE devices ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- audio_files 테이블: store_id, device_id 타입 변경 및 외래키 추가
ALTER TABLE audio_files 
    ALTER COLUMN store_id TYPE VARCHAR(50) USING store_id::VARCHAR(50),
    ALTER COLUMN device_id TYPE VARCHAR(50) USING device_id::VARCHAR(50),
    ADD CONSTRAINT fk_audio_files_store FOREIGN KEY (store_id) REFERENCES stores(id),
    ADD CONSTRAINT fk_audio_files_device FOREIGN KEY (device_id) REFERENCES devices(id);

-- monitoring_data 테이블: store_id, device_id 타입 변경 및 외래키 추가
ALTER TABLE monitoring_data 
    ALTER COLUMN store_id TYPE VARCHAR(50) USING store_id::VARCHAR(50),
    ALTER COLUMN device_id TYPE VARCHAR(50) USING device_id::VARCHAR(50),
    ADD CONSTRAINT fk_monitoring_data_store FOREIGN KEY (store_id) REFERENCES stores(id),
    ADD CONSTRAINT fk_monitoring_data_device FOREIGN KEY (device_id) REFERENCES devices(id);

-- =====================================================
-- 7. 트리거 추가
-- =====================================================

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
-- 8. 표준 필드 추가 (소프트 삭제)
-- =====================================================

ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE devices ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE labels ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE experts ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE audio_files ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;

COMMIT;

