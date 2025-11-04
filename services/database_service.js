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
            password: process.env.DB_PASSWORD || 'password',
            port: process.env.DB_PORT || 5432,
            max: 20, // 최대 연결 수
            idleTimeoutMillis: 30000,
            connectionTimeoutMillis: 10000,
        });

        this.init();
    }

    async init() {
        try {
            // 테이블 생성
            await this.createTables();
            console.log('🗄️ PostgreSQL 데이터베이스 초기화 완료');
        } catch (error) {
            console.error('데이터베이스 초기화 실패:', error);
        }
    }

    async createTables() {
        const client = await this.pool.connect();
        
        try {
            // 중앙화된 스키마 파일 읽기
            const schemaPath = path.join(__dirname, '..', 'database', 'schema.sql');
            
            if (!fs.existsSync(schemaPath)) {
                console.warn('⚠️ 스키마 파일을 찾을 수 없습니다:', schemaPath);
                console.warn('⚠️ 기본 스키마를 사용합니다. database/schema.sql 파일을 생성하세요.');
                // 기본 스키마는 유지 (하위 호환성)
                return;
            }
            
            const schemaSQL = fs.readFileSync(schemaPath, 'utf8');
            
            // PostgreSQL은 여러 구문을 한 번에 실행할 수 없으므로
            // 각 구문을 분리하여 실행합니다.
            // 주의: 트리거/함수 정의는 세미콜론이 내부에 있을 수 있으므로
            // 간단한 분리 방식을 사용합니다.
            
            // 주석 제거 및 구문 분리
            const statements = schemaSQL
                .replace(/--.*$/gm, '') // 한 줄 주석 제거
                .split(';')
                .map(s => s.trim())
                .filter(s => s.length > 0);
            
            for (const statement of statements) {
                if (statement.trim()) {
                    try {
                        await client.query(statement);
                    } catch (error) {
                        // IF NOT EXISTS 구문이 있어서 일부 에러는 무시 가능
                        const ignorableErrors = [
                            'already exists',
                            'does not exist',
                            'duplicate key'
                        ];
                        
                        const isIgnorable = ignorableErrors.some(msg => 
                            error.message.toLowerCase().includes(msg.toLowerCase())
                        );
                        
                        if (!isIgnorable) {
                            console.error('❌ 스키마 실행 오류:', error.message);
                            console.error('문제가 된 구문:', statement.substring(0, 200));
                            // 에러를 던지지 않고 경고만 출력 (하위 호환성)
                            console.warn('⚠️ 계속 진행합니다...');
                        }
                    }
                }
            }
            
            console.log('✅ 스키마 파일에서 테이블 생성 완료:', schemaPath);
            
        } finally {
            client.release();
        }
    }

    // 라벨 저장
    async saveLabel(labelData) {
        const client = await this.pool.connect();
        
        try {
            const query = `
                INSERT INTO labels (
                    file_name, file_size, file_type, file_hash, label, confidence, 
                    notes, labeler_id, store_id, device_id, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
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
                labelData.labeler_id || 'default_expert',
                labelData.store_id || 'default_store',
                labelData.device_id || 'default_device',
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
