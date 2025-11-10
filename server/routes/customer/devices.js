/**
 * Customer Devices API
 * 디바이스 관리
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
 * 디바이스 목록 조회
 * GET /api/customer/devices
 */
router.get('/', customerAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        const page = parseInt(req.query.page) || 1;
        const perPage = parseInt(req.query.per_page) || 10;
        const status = req.query.status; // online, offline, all
        
        // TODO: 실제 데이터베이스에서 디바이스 조회
        const devices = [];
        
        res.json({
            success: true,
            data: devices,
            meta: {
                has_data: devices.length > 0,
                empty_reason: devices.length === 0 ? 'no_devices_registered' : null,
                suggestion: devices.length === 0 ? '디바이스를 추가하여 시작하세요' : null,
                page: page,
                per_page: perPage,
                total: devices.length,
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('디바이스 목록 조회 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'DEVICE_FETCH_ERROR',
                message: '디바이스 목록을 불러올 수 없습니다',
                details: error.message
            }
        });
    }
});

/**
 * 디바이스 상세 조회
 * GET /api/customer/devices/:deviceId
 */
router.get('/:deviceId', customerAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        const deviceId = req.params.deviceId;
        
        // TODO: 실제 데이터베이스에서 디바이스 상세 정보 조회
        // TODO: 권한 확인 (사용자가 이 디바이스에 접근할 수 있는지)
        
        res.status(404).json({
            success: false,
            error: {
                code: 'DEVICE_NOT_FOUND',
                message: '디바이스를 찾을 수 없습니다'
            }
        });
    } catch (error) {
        console.error('디바이스 상세 조회 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'DEVICE_DETAIL_ERROR',
                message: '디바이스 정보를 불러올 수 없습니다',
                details: error.message
            }
        });
    }
});

/**
 * 디바이스 센서 데이터 조회
 * GET /api/customer/devices/:deviceId/sensors
 */
router.get('/:deviceId/sensors', customerAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        const deviceId = req.params.deviceId;
        const timeRange = req.query.range || '1h'; // 1h, 24h, 7d, 30d
        
        // TODO: 실제 센서 데이터 조회
        const sensorData = {
            temperature: [],
            vibration: [],
            power: [],
            audio: []
        };
        
        res.json({
            success: true,
            data: sensorData,
            meta: {
                has_data: false,
                device_id: deviceId,
                time_range: timeRange,
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('센서 데이터 조회 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'SENSOR_DATA_ERROR',
                message: '센서 데이터를 불러올 수 없습니다',
                details: error.message
            }
        });
    }
});

/**
 * 디바이스 정보 수정
 * PUT /api/customer/devices/:deviceId
 */
router.put('/:deviceId', customerAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        const deviceId = req.params.deviceId;
        const { device_name, location, description } = req.body;
        
        // TODO: 권한 확인 및 디바이스 정보 업데이트
        
        res.json({
            success: true,
            message: '디바이스 정보가 업데이트되었습니다',
            data: {
                device_id: deviceId,
                updated_at: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('디바이스 수정 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'DEVICE_UPDATE_ERROR',
                message: '디바이스 정보를 수정할 수 없습니다',
                details: error.message
            }
        });
    }
});

/**
 * 디바이스 삭제
 * DELETE /api/customer/devices/:deviceId
 */
router.delete('/:deviceId', customerAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        const deviceId = req.params.deviceId;
        
        // TODO: 권한 확인 및 디바이스 삭제
        
        res.json({
            success: true,
            message: '디바이스가 삭제되었습니다',
            data: {
                device_id: deviceId,
                deleted_at: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('디바이스 삭제 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'DEVICE_DELETE_ERROR',
                message: '디바이스를 삭제할 수 없습니다',
                details: error.message
            }
        });
    }
});

module.exports = router;
