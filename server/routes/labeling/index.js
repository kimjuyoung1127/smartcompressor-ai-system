/**
 * 라벨링 시스템 라우트
 * RBAC 기반 접근 제어 적용
 */

const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');
const { requireLabeler } = require('../../middleware/rbac');
const DatabaseService = require('../../../services/database_service');
const multer = require('multer');

const db = new DatabaseService();

// 파일 업로드 설정
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        const uploadDir = path.join(__dirname, '../../data/labeling_ready');
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
    },
    filename: function (req, file, cb) {
        // 파일명 규칙: labeling_unknown_timestamp.ext
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const ext = path.extname(file.originalname);
        const newFilename = `labeling_unknown_${timestamp}${ext}`;
        cb(null, newFilename);
    }
});
const upload = multer({ storage: storage });

// 세션 검증 미들웨어 (authRoutes에서 가져온 것과 동일)
const authenticateSession = async (req, res, next) => {
    try {
        const sessionId = req.cookies.sessionId;
        if (!sessionId) {
            return res.status(401).json({ 
                success: false, 
                message: '로그인이 필요합니다.' 
            });
        }

        const session = await db.getSession(sessionId);
        if (!session) {
            return res.status(401).json({ 
                success: false, 
                message: '유효하지 않은 세션입니다.' 
            });
        }

        const sessData = session.sess;
        req.user = {
            userId: sessData.user_id || sessData.user?.id,
            username: sessData.user?.username,
            email: sessData.user?.email,
            role: sessData.user?.role,
            roles: sessData.user?.roles || [sessData.user?.role]
        };
        next();
    } catch (error) {
        console.error('세션 검증 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '세션 검증 중 오류가 발생했습니다.' 
        });
    }
};

// 라벨링 대기열 조회
router.get('/queue', [authenticateSession, requireLabeler], async (req, res) => {
    try {
        const client = await db.pool.connect();
        try {
            // audio_files에서 labeling 관련 파일만 가져오고, labels 테이블과 조인하여 처리 여부 확인
            const result = await client.query(`
                SELECT 
                    af.id,
                    af.file_name,
                    af.file_path,
                    COALESCE(l.id IS NOT NULL, false) as is_processed,
                    af.upload_timestamp,
                    af.duration_seconds,
                    af.sample_rate
                FROM audio_files af
                LEFT JOIN labels l ON af.file_name = l.file_name
                WHERE af.file_name LIKE 'labeling_%'
                ORDER BY af.upload_timestamp DESC
            `);
            
            const queue = result.rows.map(item => ({
                id: item.id,
                file_name: item.file_name,
                url: `/api/labeling/audio/${item.id}`,  // 이 엔드포인트는 아래에 정의
                peaks_url: `/api/labeling/peaks/${item.id}`,  // 이 엔드포인트는 아래에 정의
                is_processed: item.is_processed
            }));
            
            res.json(queue);
        } finally {
            client.release();
        }
    } catch (error) {
        console.error('대기열 조회 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '대기열 조회 중 오류가 발생했습니다.' 
        });
    }
});

// 오디오 파일 제공
router.get('/audio/:fileId', [authenticateSession, requireLabeler], async (req, res) => {
    try {
        const fileId = req.params.fileId;
        const client = await db.pool.connect();
        try {
            const result = await client.query(
                'SELECT file_path FROM audio_files WHERE id = $1',
                [fileId]
            );
            
            if (result.rows.length === 0) {
                return res.status(404).json({ error: 'Audio file not found' });
            }
            
            const filePath = result.rows[0].file_path;
            if (!fs.existsSync(filePath)) {
                return res.status(404).json({ error: 'Audio file not found on disk' });
            }
            
            res.sendFile(path.resolve(filePath));
        } finally {
            client.release();
        }
    } catch (error) {
        console.error('오디오 파일 제공 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '오디오 파일 제공 중 오류가 발생했습니다.' 
        });
    }
});

// 오디오 파일 삭제
router.delete('/audio/:fileId', [authenticateSession, requireLabeler], async (req, res) => {
    try {
        const fileId = req.params.fileId;
        const client = await db.pool.connect();
        try {
            // 먼저 파일 정보를 가져옴
            const fileResult = await client.query(
                'SELECT file_name, file_path FROM audio_files WHERE id = $1',
                [fileId]
            );
            
            if (fileResult.rows.length === 0) {
                return res.status(404).json({ error: 'Audio file not found' });
            }
            
            const { file_name, file_path } = fileResult.rows[0];
            
            // 관련 레이블 삭제
            await client.query('DELETE FROM labels WHERE file_name = $1', [file_name]);
            
            // 오디오 파일 레코드 삭제
            await client.query('DELETE FROM audio_files WHERE id = $1', [fileId]);
            
            // 실제 파일이 존재하면 삭제
            if (fs.existsSync(file_path)) {
                fs.unlinkSync(file_path);
            }
            
            // 관련 피크스 파일도 삭제 (존재할 경우)
            const peaksDir = path.join(__dirname, '../../data/peaks_cache');
            const peaksFile = path.join(peaksDir, `${path.basename(file_path, path.extname(file_path))}.json`);
            if (fs.existsSync(peaksFile)) {
                fs.unlinkSync(peaksFile);
            }
            
            res.json({ 
                success: true, 
                message: 'Audio file and associated data deleted successfully' 
            });
        } finally {
            client.release();
        }
    } catch (error) {
        console.error('오디오 파일 삭제 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '오디오 파일 삭제 중 오류가 발생했습니다.' 
        });
    }
});

// 피크스 데이터 제공 (audiowaveform 생성)
router.get('/peaks/:fileId', [authenticateSession, requireLabeler], async (req, res) => {
    try {
        const fileId = req.params.fileId;
        const client = await db.pool.connect();
        try {
            const result = await client.query(
                'SELECT file_path FROM audio_files WHERE id = $1',
                [fileId]
            );
            
            if (result.rows.length === 0) {
                return res.status(404).json({ error: 'Audio file not found' });
            }
            
            const filePath = result.rows[0].file_path;
            const peaksDir = path.join(__dirname, '../../data/peaks_cache');
            if (!fs.existsSync(peaksDir)) {
                fs.mkdirSync(peaksDir, { recursive: true });
            }
            
            // 피크스 파일명 생성
            const originalName = path.basename(filePath, path.extname(filePath));
            const peaksFile = path.join(peaksDir, `${originalName}.json`);
            
            // 피크스 파일이 없으면 생성 (이 부분은 서버 실행 시 audiowaveform 설치 및 실행이 필요)
            if (!fs.existsSync(peaksFile)) {
                // 이 부분은 서버에 audiowaveform이 설치되어 있어야 실행 가능
                const { execSync } = require('child_process');
                try {
                    execSync(`audiowaveform -i "${filePath}" -o "${peaksFile}" --pixels-per-second 100 --bits 8`);
                } catch (execError) {
                    console.error('audiowaveform 실행 오류:', execError);
                    // 임시로 빈 피크스 데이터 생성
                    fs.writeFileSync(peaksFile, JSON.stringify({
                        version: 2,
                        channels: 1,
                        data: []
                    }));
                }
            }
            
            res.sendFile(path.resolve(peaksFile));
        } finally {
            client.release();
        }
    } catch (error) {
        console.error('피크스 데이터 제공 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '피크스 데이터 제공 중 오류가 발생했습니다.' 
        });
    }
});

// 라벨 저장
router.post('/save', [authenticateSession, requireLabeler], async (req, res) => {
    try {
        // 로그인한 사용자 정보 자동 추가
        const labelData = {
            ...req.body,
            labeler_user_id: req.user.userId,  // realschema.md 기준
            labeler_id: req.user.username,     // 레거시 지원
        };
        
        // 필수 필드 검증
        if (!labelData.audio_file_id) {
            return res.status(400).json({ 
                success: false, 
                message: 'audio_file_id는 필수입니다.' 
            });
        }

        // audio_file_id로 file_name을 조회
        const client = await db.pool.connect();
        try {
            // audio_files에서 파일 이름을 가져옴
            const fileResult = await client.query(
                'SELECT file_name FROM audio_files WHERE id = $1',
                [labelData.audio_file_id]
            );

            if (fileResult.rows.length === 0) {
                return res.status(400).json({
                    success: false,
                    message: 'Invalid audio file ID'
                });
            }

            const fileName = fileResult.rows[0].file_name;

            // 레이블 저장
            const insertResult = await client.query(`
                INSERT INTO labels (file_name, label, confidence, labeler_id, metadata)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (file_name) 
                DO UPDATE SET 
                    label = EXCLUDED.label,
                    confidence = EXCLUDED.confidence,
                    labeler_id = EXCLUDED.labeler_id,
                    metadata = EXCLUDED.metadata,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING *
            `, [
                fileName,
                labelData.label || 'unknown',
                labelData.confidence || 50,
                req.user.userId,
                JSON.stringify(labelData.annotations || [])
            ]);

            res.json({ 
                success: true, 
                message: '라벨이 성공적으로 저장되었습니다.',
                data: insertResult.rows[0]
            });
        } finally {
            client.release();
        }
    } catch (error) {
        console.error('라벨 저장 오류:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message,
            message: '라벨 저장 중 오류가 발생했습니다.' 
        });
    }
});

// 오디오 파일 업로드
router.post('/upload', [authenticateSession, requireLabeler, upload.single('audio_file')], async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({
                success: false,
                error: "No audio file provided"
            });
        }

        // 파일 정보를 데이터베이스에 저장
        const client = await db.pool.connect();
        try {
            // 업로드된 파일 정보를 audio_files 테이블에 저장
            const insertResult = await client.query(`
                INSERT INTO audio_files (
                    user_id, file_name, file_path, file_size, format, upload_timestamp, is_processed
                ) VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP, FALSE)
                RETURNING id
            `, [
                req.user.userId,           // user_id
                req.file.filename,         // file_name
                req.file.path,             // file_path
                req.file.size,             // file_size
                path.extname(req.file.originalname).substring(1).toLowerCase(), // format (확장자에서 . 제거)
            ]);

            res.json({
                success: true,
                message: "File uploaded successfully",
                filename: req.file.filename,
                file_path: req.file.path,
                file_id: insertResult.rows[0].id
            });

        } finally {
            client.release();
        }

    } catch (error) {
        console.error('파일 업로드 오류:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            message: '파일 업로드 중 오류가 발생했습니다.'
        });
    }
});

// 라벨링 페이지 접근 (labeler, admin만 가능)
router.get('/interface', [authenticateSession, requireLabeler], (req, res) => {
    res.sendFile(path.join(__dirname, '../../static/high_quality_labeling_tool.html'));
});

// 라벨 저장 API (작업자 ID 자동 추가) - 기존 엔드포인트 유지
router.post('/save-label', [authenticateSession, requireLabeler], async (req, res) => {
    try {
        // 로그인한 사용자 정보 자동 추가
        const labelData = {
            ...req.body,
            labeler_user_id: req.user.userId,  // realschema.md 기준
            labeler_id: req.user.username,     // 레거시 지원
        };
        
        // 필수 필드 검증
        if (!labelData.file_name || !labelData.label || labelData.confidence === undefined) {
            return res.status(400).json({ 
                success: false, 
                message: 'file_name, label, confidence는 필수입니다.' 
            });
        }
        
        const result = await db.saveLabel(labelData);
        
        res.json({ 
            success: true, 
            message: '라벨이 성공적으로 저장되었습니다.',
            data: result 
        });
    } catch (error) {
        console.error('라벨 저장 오류:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message,
            message: '라벨 저장 중 오류가 발생했습니다.' 
        });
    }
});

// 라벨링 통계 조회 (labeler, admin만 가능)
router.get('/stats', [authenticateSession, requireLabeler], async (req, res) => {
    try {
        const stats = await db.getStats();
        res.json({ 
            success: true, 
            data: stats 
        });
    } catch (error) {
        console.error('통계 조회 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '통계 조회 중 오류가 발생했습니다.' 
        });
    }
});

// 라벨링 이력 조회 (labeler, admin만 가능)
router.get('/history', [authenticateSession, requireLabeler], async (req, res) => {
    try {
        const { page = 1, limit = 20, label, store_id } = req.query;
        const history = await db.getHistory({ 
            page: parseInt(page), 
            limit: parseInt(limit),
            label,
            store_id
        });
        res.json({ 
            success: true, 
            data: history 
        });
    } catch (error) {
        console.error('이력 조회 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '이력 조회 중 오류가 발생했습니다.' 
        });
    }
});

// 내 라벨링 작업 조회 (자신의 작업만)
router.get('/my-labels', [authenticateSession, requireLabeler], async (req, res) => {
    try {
        const { page = 1, limit = 20 } = req.query;
        const client = await db.pool.connect();
        
        try {
            const offset = (page - 1) * limit;
            const result = await client.query(
                `SELECT * FROM labels 
                 WHERE labeler_user_id = $1
                 ORDER BY created_at DESC 
                 LIMIT $2 OFFSET $3`,
                [req.user.userId, limit, offset]
            );
            
            const countResult = await client.query(
                'SELECT COUNT(*) as total FROM labels WHERE labeler_user_id = $1',
                [req.user.userId]
            );
            
            res.json({ 
                success: true, 
                data: {
                    labels: result.rows,
                    pagination: {
                        page: parseInt(page),
                        limit: parseInt(limit),
                        total: parseInt(countResult.rows[0].total)
                    }
                }
            });
        } finally {
            client.release();
        }
    } catch (error) {
        console.error('내 라벨 조회 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '라벨 조회 중 오류가 발생했습니다.' 
        });
    }
});

module.exports = router;
