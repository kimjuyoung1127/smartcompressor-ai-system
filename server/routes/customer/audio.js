/**
 * Customer Audio API
 * 오디오 분석
 */

const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const { authenticateSession } = require('../../middleware/auth');
const { requireRole } = require('../../middleware/rbac');

const customerAuth = [
    authenticateSession,
    requireRole(['admin', 'premium_user'])
];

// 파일 업로드 설정
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        const uploadDir = path.join(__dirname, '../../../uploads/audio');
        cb(null, uploadDir);
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, 'audio-' + uniqueSuffix + path.extname(file.originalname));
    }
});

const upload = multer({
    storage: storage,
    limits: {
        fileSize: 10 * 1024 * 1024 // 10MB
    },
    fileFilter: function (req, file, cb) {
        const allowedMimes = ['audio/wav', 'audio/mpeg', 'audio/mp3'];
        if (allowedMimes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error('지원하지 않는 파일 형식입니다'));
        }
    }
});

/**
 * 오디오 파일 업로드
 * POST /api/customer/audio/upload
 */
router.post('/upload', customerAuth, upload.single('audio'), async (req, res) => {
    try {
        const userId = req.user.userId;
        const file = req.file;
        const { device_id, description } = req.body;
        
        if (!file) {
            return res.status(400).json({
                success: false,
                error: {
                    code: 'FILE_MISSING',
                    message: '파일이 업로드되지 않았습니다'
                }
            });
        }
        
        // TODO: 파일 정보 데이터베이스에 저장
        // TODO: AI 분석 큐에 추가
        
        res.json({
            success: true,
            message: '오디오 파일이 업로드되었습니다',
            data: {
                file_id: 'audio_' + Date.now(),
                file_name: file.originalname,
                file_size: file.size,
                device_id: device_id,
                status: 'processing',
                uploaded_at: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('오디오 업로드 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'UPLOAD_ERROR',
                message: '오디오 파일을 업로드할 수 없습니다',
                details: error.message
            }
        });
    }
});

/**
 * 오디오 파일 목록
 * GET /api/customer/audio/files
 */
router.get('/files', customerAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        const page = parseInt(req.query.page) || 1;
        const perPage = parseInt(req.query.per_page) || 10;
        
        // TODO: 오디오 파일 목록 조회
        const files = [];
        
        res.json({
            success: true,
            data: files,
            meta: {
                has_data: files.length > 0,
                empty_reason: files.length === 0 ? 'no_audio_files' : null,
                page: page,
                per_page: perPage,
                total: files.length,
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('오디오 파일 목록 조회 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'FILE_LIST_ERROR',
                message: '오디오 파일 목록을 불러올 수 없습니다',
                details: error.message
            }
        });
    }
});

/**
 * AI 분석 결과
 * GET /api/customer/audio/:fileId/analysis
 */
router.get('/:fileId/analysis', customerAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        const fileId = req.params.fileId;
        
        // TODO: AI 분석 결과 조회
        
        res.json({
            success: true,
            data: {
                file_id: fileId,
                is_overload: false,
                confidence: 0,
                status: 'no_analysis',
                features_extracted: null,
                analyzed_at: null
            },
            meta: {
                has_data: false,
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('AI 분석 결과 조회 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'ANALYSIS_ERROR',
                message: 'AI 분석 결과를 불러올 수 없습니다',
                details: error.message
            }
        });
    }
});

/**
 * 오디오 파일 삭제
 * DELETE /api/customer/audio/:fileId
 */
router.delete('/:fileId', customerAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        const fileId = req.params.fileId;
        
        // TODO: 파일 삭제 (파일 시스템 + 데이터베이스)
        
        res.json({
            success: true,
            message: '오디오 파일이 삭제되었습니다',
            data: {
                file_id: fileId,
                deleted_at: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('오디오 파일 삭제 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'DELETE_ERROR',
                message: '오디오 파일을 삭제할 수 없습니다',
                details: error.message
            }
        });
    }
});

module.exports = router;
