/**
 * 라벨링 시스템 라우트
 * RBAC 기반 접근 제어 적용
 */

const express = require('express');
const router = express.Router();
const path = require('path');
const { requireLabeler } = require('../middleware/rbac');
const DatabaseService = require('../../services/database_service');

const db = new DatabaseService();

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

// 라벨링 페이지 접근 (labeler, admin만 가능)
router.get('/interface', [authenticateSession, requireLabeler], (req, res) => {
    res.sendFile(path.join(__dirname, '../../static/high_quality_labeling_tool.html'));
});

// 라벨 저장 API (작업자 ID 자동 추가)
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
