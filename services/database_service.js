/**
 * PostgreSQL 데이터베이스 서비스
 * 확장성과 성능을 고려한 라벨링 데이터 관리
 */

const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

class DatabaseService {
    constructor() {
        // PostgreSQL 연결 설정
        this.pool = new Pool({
            user: process.env.DB_USER || 'postgres',
            host: process.env.DB_HOST || 'localhost',
            database: process.env.DB_NAME || 'smartcompressor_ai',
            password: process.env.DB_PASSWORD || 'signalcraft6898',
            port: process.env.DB_PORT || 5432,
            max: 20, // 최대 연결 수
            idleTimeoutMillis: 30000,
            connectionTimeoutMillis: 10000,
        });

        this.init();
    }

    async init() {
        try {
            // 연결 테스트
            const client = await this.pool.connect();
            console.log('✅ PostgreSQL 연결 성공');
            
            // 테이블 존재 여부 확인
            const result = await client.query(`
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            `);
            
            const tablesExist = parseInt(result.rows[0].count) > 0;
            
            if (tablesExist) {
                console.log('🗄️ 데이터베이스 테이블이 이미 존재합니다 (스키마 생성 건너뜀)');
            } else {
                console.log('🔨 데이터베이스 테이블 생성 중...');
                await this.createTables();
                console.log('✅ 데이터베이스 테이블 생성 완료');
            }
            
            client.release();
            console.log('🗄️ PostgreSQL 데이터베이스 초기화 완료');
        } catch (error) {
            console.error('❌ 데이터베이스 초기화 실패:', error.message);
        }
    }

    async createTables() {
        const client = await this.pool.connect();
        
        try {
            // ===== 1단계: 참조되는 기본 테이블 먼저 생성 =====
            
            // users 테이블 (다른 테이블에서 참조됨)
            await client.query(`
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
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMPTZ
                )
            `);

            // stores 테이블
            await client.query(`
                CREATE TABLE IF NOT EXISTS stores (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    location VARCHAR(255),
                    owner_id VARCHAR(50),
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            `);

            // ===== 2단계: users/stores를 참조하는 테이블 생성 =====
            
            // 장치 테이블
            await client.query(`
                CREATE TABLE IF NOT EXISTS devices (
                    id VARCHAR(50) PRIMARY KEY,
                    store_id VARCHAR(50) REFERENCES stores(id),
                    device_type VARCHAR(50) DEFAULT 'compressor',
                    location VARCHAR(100),
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            `);

            // 전문가 테이블 (레거시 - experts는 users로 통합되었지만 호환성 유지)
            await client.query(`
                CREATE TABLE IF NOT EXISTS experts (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    role VARCHAR(50) DEFAULT 'labeler',
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            `);

            // 라벨링 테이블 (users를 참조)
            await client.query(`
                CREATE TABLE IF NOT EXISTS labels (
                    id SERIAL PRIMARY KEY,
                    file_name VARCHAR(255) NOT NULL,
                    file_size BIGINT,
                    file_type VARCHAR(50),
                    file_hash VARCHAR(64) UNIQUE,
                    label VARCHAR(20) NOT NULL CHECK (label IN ('normal', 'warning', 'critical', 'unknown')),
                    confidence INTEGER NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
                    notes TEXT,
                    labeler_id VARCHAR(50),
                    store_id VARCHAR(50),
                    device_id VARCHAR(50),
                    metadata JSONB,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            `);
            
            // labeler_user_id 컬럼 추가 (users 테이블이 이미 생성되었으므로 안전)
            await client.query(`
                ALTER TABLE labels 
                ADD COLUMN IF NOT EXISTS labeler_user_id INTEGER REFERENCES users(id)
            `);

            // 라벨링 통계 테이블
            await client.query(`
                CREATE TABLE IF NOT EXISTS labeling_stats (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL UNIQUE,
                    total_labeled INTEGER DEFAULT 0,
                    normal_count INTEGER DEFAULT 0,
                    warning_count INTEGER DEFAULT 0,
                    critical_count INTEGER DEFAULT 0,
                    unknown_count INTEGER DEFAULT 0,
                    avg_confidence DECIMAL(5,2) DEFAULT 0,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            `);

            // audio_files 테이블 (오디오 파일 메타데이터)
            await client.query(`
                CREATE TABLE IF NOT EXISTS audio_files (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    store_id INTEGER,
                    device_id INTEGER,
                    file_name VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_size BIGINT,
                    duration_seconds DECIMAL(10, 2),
                    sample_rate INTEGER,
                    channels INTEGER,
                    format VARCHAR(20),
                    upload_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    is_processed BOOLEAN DEFAULT false
                )
            `);

            // ai_analysis_results 테이블 (AI 분석 결과)
            await client.query(`
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
                )
            `);

            // monitoring_data 테이블 (실시간 모니터링 데이터)
            await client.query(`
                CREATE TABLE IF NOT EXISTS monitoring_data (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    store_id INTEGER,
                    device_id INTEGER,
                    temperature DECIMAL(5, 2),
                    vibration_level DECIMAL(8, 4),
                    power_consumption DECIMAL(8, 2),
                    audio_level DECIMAL(8, 4),
                    status VARCHAR(20),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            `);

            // 인덱스 생성
            await client.query(`
                CREATE INDEX IF NOT EXISTS idx_labels_timestamp ON labels(created_at);
                CREATE INDEX IF NOT EXISTS idx_labels_label ON labels(label);
                CREATE INDEX IF NOT EXISTS idx_labels_labeler ON labels(labeler_id);
                CREATE INDEX IF NOT EXISTS idx_labels_store ON labels(store_id);
                CREATE INDEX IF NOT EXISTS idx_labels_file_hash ON labels(file_hash);
                CREATE INDEX IF NOT EXISTS idx_labels_metadata ON labels USING GIN(metadata);
            `);

            // 트리거 생성 (updated_at 자동 업데이트)
            await client.query(`
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            `);

            await client.query(`
                DROP TRIGGER IF EXISTS update_labels_updated_at ON labels;
                CREATE TRIGGER update_labels_updated_at
                    BEFORE UPDATE ON labels
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
            `);

        } finally {
            client.release();
        }
    }

    // 라벨 저장 (realschema.md 기준 - labeler_user_id 사용)
    async saveLabel(labelData) {
        const client = await this.pool.connect();
        
        try {
            // labeler_user_id가 필수인지 확인
            if (!labelData.labeler_user_id && !labelData.labeler_id) {
                throw new Error('labeler_user_id 또는 labeler_id는 필수입니다');
            }
            
            const query = `
                INSERT INTO labels (
                    file_name, file_size, file_type, file_hash, label, confidence, 
                    notes, labeler_id, labeler_user_id, store_id, device_id, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING *
            `;
            
            const values = [
                labelData.file_name,
                labelData.file_size || 0,
                labelData.file_type || 'audio/wav',
                labelData.file_hash || this.generateHash(labelData.file_name),
                labelData.label,
                labelData.confidence,
                labelData.notes || null,
                labelData.labeler_id || null,  // 레거시 지원
                labelData.labeler_user_id || null,  // 새로운 방식
                labelData.store_id || null,
                labelData.device_id || null,
                JSON.stringify(labelData.metadata || {})
            ];

            const result = await client.query(query, values);
            
            // 통계 업데이트
            await this.updateDailyStats(labelData.label);
            
            return result.rows[0];
            
        } finally {
            client.release();
        }
    }

    // 라벨링 통계 조회
    async getStats() {
        const client = await this.pool.connect();
        
        try {
            // 기본 통계
            const totalResult = await client.query('SELECT COUNT(*) as total FROM labels');
            const todayResult = await client.query(`
                SELECT COUNT(*) as today FROM labels 
                WHERE DATE(created_at) = CURRENT_DATE
            `);
            
            // 라벨 분포
            const distributionResult = await client.query(`
                SELECT label, COUNT(*) as count 
                FROM labels 
                GROUP BY label
            `);
            
            // 평균 신뢰도
            const confidenceResult = await client.query(`
                SELECT AVG(confidence) as avg_confidence 
                FROM labels
            `);
            
            // 최근 활동
            const activityResult = await client.query(`
                SELECT file_name, label, confidence, created_at
                FROM labels 
                ORDER BY created_at DESC 
                LIMIT 5
            `);

            const labelDistribution = {
                normal: 0,
                warning: 0,
                critical: 0,
                unknown: 0
            };

            distributionResult.rows.forEach(row => {
                labelDistribution[row.label] = parseInt(row.count);
            });

            return {
                total_labeled: parseInt(totalResult.rows[0].total),
                today_labeled: parseInt(todayResult.rows[0].today),
                accuracy: Math.round((confidenceResult.rows[0].avg_confidence || 0) * 10) / 10,
                pending_files: 0, // 실제로는 대기 중인 파일 수 계산
                label_distribution: labelDistribution,
                expert_performance: {
                    avg_confidence: Math.round((confidenceResult.rows[0].avg_confidence || 0) * 10) / 10,
                    labeling_speed: '2.3 files/min', // 계산 로직 추가 가능
                    quality_score: 94.8 // 계산 로직 추가 가능
                },
                recent_activity: activityResult.rows.map(row => ({
                    file: row.file_name,
                    label: row.label,
                    confidence: row.confidence,
                    timestamp: row.created_at
                }))
            };
            
        } finally {
            client.release();
        }
    }

    // 라벨링 이력 조회
    async getHistory(options = {}) {
        const client = await this.pool.connect();
        
        try {
            const { page = 1, limit = 20, label, store_id } = options;
            const offset = (page - 1) * limit;
            
            let whereClause = '';
            let params = [];
            let paramCount = 0;

            if (label) {
                whereClause += ` WHERE label = $${++paramCount}`;
                params.push(label);
            }

            if (store_id) {
                whereClause += whereClause ? ` AND store_id = $${++paramCount}` : ` WHERE store_id = $${++paramCount}`;
                params.push(store_id);
            }

            const query = `
                SELECT * FROM labels 
                ${whereClause}
                ORDER BY created_at DESC 
                LIMIT $${++paramCount} OFFSET $${++paramCount}
            `;
            
            params.push(limit, offset);
            
            const result = await client.query(query, params);
            
            // 총 개수 조회
            const countQuery = `SELECT COUNT(*) as total FROM labels ${whereClause}`;
            const countResult = await client.query(countQuery, params.slice(0, -2));
            
            return {
                history: result.rows,
                pagination: {
                    page: page,
                    limit: limit,
                    total: parseInt(countResult.rows[0].total),
                    total_pages: Math.ceil(parseInt(countResult.rows[0].total) / limit)
                }
            };
            
        } finally {
            client.release();
        }
    }

    // 전문가 등록
    async registerExpert(expertData) {
        const client = await this.pool.connect();
        
        try {
            const query = `
                INSERT INTO experts (id, name, email, role)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    last_active = CURRENT_TIMESTAMP
                RETURNING *
            `;
            
            const result = await client.query(query, [
                expertData.id,
                expertData.name,
                expertData.email,
                expertData.role || 'labeler'
            ]);
            
            return result.rows[0];
            
        } finally {
            client.release();
        }
    }

    // 전문가 목록 조회
    async getExperts() {
        const client = await this.pool.connect();
        
        try {
            const query = `
                SELECT 
                    e.*,
                    COUNT(l.id) as total_labeled,
                    AVG(l.confidence) as avg_confidence,
                    MAX(l.created_at) as last_labeling
                FROM experts e
                LEFT JOIN labels l ON e.id = l.labeler_id
                WHERE e.is_active = true
                GROUP BY e.id
                ORDER BY total_labeled DESC
            `;
            
            const result = await client.query(query);
            return result.rows.map(row => ({
                id: row.id,
                name: row.name,
                email: row.email,
                role: row.role,
                total_labeled: parseInt(row.total_labeled || 0),
                avg_confidence: Math.round((row.avg_confidence || 0) * 10) / 10,
                last_labeling: row.last_labeling,
                last_active: row.last_active
            }));
            
        } finally {
            client.release();
        }
    }

    // 일일 통계 업데이트
    async updateDailyStats(label) {
        const client = await this.pool.connect();
        
        try {
            const today = new Date().toISOString().split('T')[0];
            
            await client.query(`
                INSERT INTO labeling_stats (date, total_labeled, ${label}_count, avg_confidence)
                VALUES ($1, 1, 1, 0)
                ON CONFLICT (date) 
                DO UPDATE SET 
                    total_labeled = labeling_stats.total_labeled + 1,
                    ${label}_count = labeling_stats.${label}_count + 1,
                    avg_confidence = (
                        SELECT AVG(confidence) 
                        FROM labels 
                        WHERE DATE(created_at) = $1
                    )
            `, [today]);
            
        } finally {
            client.release();
        }
    }

    // 파일 해시 생성
    generateHash(fileName) {
        const crypto = require('crypto');
        return crypto.createHash('md5').update(fileName + Date.now()).digest('hex');
    }

    // ===== 사용자 관리 메서드들 =====
    
    async createUser(userData) {
        const { username, email, password_hash, full_name, phone, role = 'user', additional_info } = userData;
        const client = await this.pool.connect();
        try {
            const res = await client.query(
                `INSERT INTO users (username, email, password_hash, full_name, phone, role, additional_info)
                 VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *`,
                [username, email, password_hash, full_name, phone, role, JSON.stringify(additional_info)]
            );
            return res.rows[0];
        } finally {
            client.release();
        }
    }

    async getUserByUsername(username) {
        const client = await this.pool.connect();
        try {
            const res = await client.query(
                'SELECT * FROM users WHERE username = $1 AND is_active = true',
                [username]
            );
            return res.rows[0];
        } finally {
            client.release();
        }
    }

    async getUserByEmail(email) {
        const client = await this.pool.connect();
        try {
            const res = await client.query(
                'SELECT * FROM users WHERE email = $1 AND is_active = true',
                [email]
            );
            return res.rows[0];
        } finally {
            client.release();
        }
    }

    async updateUserLastLogin(userId) {
        const client = await this.pool.connect();
        try {
            await client.query(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = $1',
                [userId]
            );
        } finally {
            client.release();
        }
    }

    // ===== 세션 관리 메서드들 (connect-pg-simple 호환) =====
    
    async createSession(sessionId, userId, expiresAt, ipAddress = null, userAgent = null) {
        const client = await this.pool.connect();
        try {
            // users 테이블에서 사용자 정보 조회
            const userResult = await client.query(
                'SELECT id, username, email, role, roles FROM users WHERE id = $1',
                [userId]
            );
            
            if (userResult.rows.length === 0) {
                throw new Error('User not found');
            }
            
            const user = userResult.rows[0];
            
            // sess 데이터 구성 (connect-pg-simple 형식)
            const sessData = {
                cookie: {
                    originalMaxAge: 24 * 60 * 60 * 1000, // 24시간
                    expires: expiresAt,
                    httpOnly: true,
                    path: '/'
                },
                user: {
                    id: user.id,
                    username: user.username,
                    email: user.email,
                    role: user.role,
                    roles: user.roles || [user.role]
                },
                user_id: userId,
                ip_address: ipAddress,
                user_agent: userAgent
            };
            
            // sessions 테이블에 삽입 (realschema.md 기준)
            const res = await client.query(
                `INSERT INTO sessions (sid, sess, expire)
                 VALUES ($1, $2, $3)
                 ON CONFLICT (sid) DO UPDATE 
                 SET sess = EXCLUDED.sess, expire = EXCLUDED.expire
                 RETURNING *`,
                [sessionId, JSON.stringify(sessData), expiresAt]
            );
            
            return res.rows[0];
        } finally {
            client.release();
        }
    }
    
    async getSession(sessionId) {
        const client = await this.pool.connect();
        try {
            const res = await client.query(
                'SELECT * FROM sessions WHERE sid = $1 AND expire > NOW()',
                [sessionId]
            );
            
            if (res.rows.length === 0) {
                return null;
            }
            
            const session = res.rows[0];
            return {
                sid: session.sid,
                sess: typeof session.sess === 'string' ? JSON.parse(session.sess) : session.sess,
                expire: session.expire,
                user_id: session.sess?.user_id,
                username: session.sess?.user?.username,
                role: session.sess?.user?.role,
                roles: session.sess?.user?.roles
            };
        } finally {
            client.release();
        }
    }
    
    async deleteSession(sessionId) {
        const client = await this.pool.connect();
        try {
            await client.query(
                'DELETE FROM sessions WHERE sid = $1',
                [sessionId]
            );
        } finally {
            client.release();
        }
    }
    
    async cleanupExpiredSessions() {
        const client = await this.pool.connect();
        try {
            const result = await client.query(
                'DELETE FROM sessions WHERE expire < NOW()'
            );
            console.log(`🧹 만료된 세션 ${result.rowCount}개 정리됨`);
        } finally {
            client.release();
        }
    }

    // ===== 오디오 파일 관리 메서드들 =====
    
    async saveAudioFile(audioData) {
        const { user_id, store_id, device_id, file_name, file_path, file_size, duration_seconds, sample_rate, channels, format } = audioData;
        const client = await this.pool.connect();
        try {
            const res = await client.query(
                `INSERT INTO audio_files (user_id, store_id, device_id, file_name, file_path, file_size, duration_seconds, sample_rate, channels, format)
                 VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING *`,
                [user_id, store_id, device_id, file_name, file_path, file_size, duration_seconds, sample_rate, channels, format]
            );
            return res.rows[0];
        } finally {
            client.release();
        }
    }

    async getAudioFilesByUser(userId, page = 1, limit = 20) {
        const client = await this.pool.connect();
        try {
            const res = await client.query(
                `SELECT * FROM audio_files WHERE user_id = $1 
                 ORDER BY upload_timestamp DESC LIMIT $2 OFFSET $3`,
                [userId, limit, (page - 1) * limit]
            );
            const totalRes = await client.query('SELECT COUNT(*) FROM audio_files WHERE user_id = $1', [userId]);
            const total = parseInt(totalRes.rows[0].count, 10);

            return {
                files: res.rows,
                pagination: {
                    page,
                    limit,
                    total,
                    total_pages: Math.ceil(total / limit)
                }
            };
        } finally {
            client.release();
        }
    }

    // ===== AI 분석 결과 관리 메서드들 =====
    
    async saveAnalysisResult(analysisData) {
        const { audio_file_id, user_id, is_overload, confidence, processing_time_ms, model_info, features_extracted, quality_metrics, optimization_info, noise_info, message } = analysisData;
        const client = await this.pool.connect();
        try {
            const res = await client.query(
                `INSERT INTO ai_analysis_results (audio_file_id, user_id, is_overload, confidence, processing_time_ms, model_info, features_extracted, quality_metrics, optimization_info, noise_info, message)
                 VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) RETURNING *`,
                [audio_file_id, user_id, is_overload, confidence, processing_time_ms, model_info, features_extracted, quality_metrics, optimization_info, noise_info, message]
            );
            return res.rows[0];
        } finally {
            client.release();
        }
    }

    async getAnalysisResultsByUser(userId, page = 1, limit = 20) {
        const client = await this.pool.connect();
        try {
            const res = await client.query(
                `SELECT aar.*, af.file_name, af.upload_timestamp 
                 FROM ai_analysis_results aar
                 LEFT JOIN audio_files af ON aar.audio_file_id = af.id
                 WHERE aar.user_id = $1 
                 ORDER BY aar.analysis_timestamp DESC LIMIT $2 OFFSET $3`,
                [userId, limit, (page - 1) * limit]
            );
            const totalRes = await client.query('SELECT COUNT(*) FROM ai_analysis_results WHERE user_id = $1', [userId]);
            const total = parseInt(totalRes.rows[0].count, 10);

            return {
                results: res.rows,
                pagination: {
                    page,
                    limit,
                    total,
                    total_pages: Math.ceil(total / limit)
                }
            };
        } finally {
            client.release();
        }
    }

    // ===== 모니터링 데이터 관리 메서드들 =====
    
    async saveMonitoringData(monitoringData) {
        const { user_id, store_id, device_id, temperature, vibration_level, power_consumption, audio_level, status } = monitoringData;
        const client = await this.pool.connect();
        try {
            const res = await client.query(
                `INSERT INTO monitoring_data (user_id, store_id, device_id, temperature, vibration_level, power_consumption, audio_level, status)
                 VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING *`,
                [user_id, store_id, device_id, temperature, vibration_level, power_consumption, audio_level, status]
            );
            return res.rows[0];
        } finally {
            client.release();
        }
    }

    async getMonitoringDataByUser(userId, hours = 24) {
        const client = await this.pool.connect();
        try {
            const res = await client.query(
                `SELECT * FROM monitoring_data 
                 WHERE user_id = $1 AND timestamp >= NOW() - INTERVAL '${hours} hours'
                 ORDER BY timestamp DESC`,
                [userId]
            );
            return res.rows;
        } finally {
            client.release();
        }
    }

    // 데이터베이스 연결 종료
    async close() {
        await this.pool.end();
    }
}

module.exports = DatabaseService;
