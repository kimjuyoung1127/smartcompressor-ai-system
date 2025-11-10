/**
 * Customer Sample Data API
 * 샘플 데이터 생성 및 관리
 */

const express = require('express');
const router = express.Router();
const { authenticateSession } = require('../../middleware/auth');
const { requireRole } = require('../../middleware/rbac');

const customerAuth = [
    authenticateSession,
    requireRole(['admin', 'premium_user'])
];

/**
 * 샘플 데이터 생성
 * POST /api/customer/sample-data/generate
 */
router.post('/generate', customerAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        
        // TODO: 이미 데이터가 있는지 확인
        // TODO: 샘플 데이터 생성
        //   - 디바이스 3개
        //   - 7일간 센서 데이터
        //   - 이상 징후 2-3개
        //   - 오디오 파일 5개
        
        res.json({
            success: true,
            message: '샘플 데이터가 생성되었습니다',
            data: {
                devices_created: 3,
                sensor_readings_created: 504, // 7일 * 24시간 * 3개
                anomalies_created: 3,
                audio_files_created: 5,
                generated_at: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('샘플 데이터 생성 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'SAMPLE_GENERATION_ERROR',
                message: '샘플 데이터를 생성할 수 없습니다',
                details: error.message
            }
        });
    }
});

/**
 * 샘플 데이터 확인
 * GET /api/customer/sample-data/status
 */
router.get('/status', customerAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        
        // TODO: 샘플 데이터 존재 여부 확인
        
        res.json({
            success: true,
            data: {
                has_sample_data: false,
                sample_device_count: 0,
                last_generated: null
            }
        });
    } catch (error) {
        console.error('샘플 데이터 상태 확인 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'STATUS_ERROR',
                message: '샘플 데이터 상태를 확인할 수 없습니다',
                details: error.message
            }
        });
    }
});

/**
 * 샘플 데이터 삭제
 * DELETE /api/customer/sample-data/clear
 */
router.delete('/clear', customerAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        
        // TODO: 샘플 데이터만 삭제
        // metadata에 sample=true로 표시된 데이터만 삭제
        
        res.json({
            success: true,
            message: '샘플 데이터가 삭제되었습니다',
            data: {
                devices_deleted: 0,
                sensor_readings_deleted: 0,
                anomalies_deleted: 0,
                audio_files_deleted: 0,
                deleted_at: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('샘플 데이터 삭제 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'SAMPLE_DELETE_ERROR',
                message: '샘플 데이터를 삭제할 수 없습니다',
                details: error.message
            }
        });
    }
});

module.exports = router;
