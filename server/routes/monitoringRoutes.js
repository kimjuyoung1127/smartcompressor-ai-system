const express = require('express');
const DatabaseService = require('../../database/database_service');
const router = express.Router();

// PostgreSQL 데이터베이스 서비스 초기화
const db = new DatabaseService();

// 모니터링 데이터 저장
router.post('/data', async (req, res) => {
    try {
        const { 
            user_id, 
            store_id, 
            device_id, 
            temperature, 
            vibration_level, 
            power_consumption, 
            audio_level, 
            status 
        } = req.body;

        // 필수 필드 검증
        if (!user_id) {
            return res.status(400).json({
                success: false,
                message: '사용자 ID가 필요합니다.'
            });
        }

        const monitoringData = {
            user_id,
            store_id: store_id || null,
            device_id: device_id || null,
            temperature: temperature || null,
            vibration_level: vibration_level || null,
            power_consumption: power_consumption || null,
            audio_level: audio_level || null,
            status: status || 'normal'
        };

        const savedData = await db.saveMonitoringData(monitoringData);
        console.log('💾 모니터링 데이터 저장됨:', savedData.id);

        res.json({
            success: true,
            message: '모니터링 데이터가 저장되었습니다.',
            data: savedData
        });

    } catch (error) {
        console.error('모니터링 데이터 저장 오류:', error);
        res.status(500).json({
            success: false,
            message: '모니터링 데이터 저장 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 사용자별 모니터링 데이터 조회
router.get('/data', async (req, res) => {
    try {
        const userId = req.query.user_id;
        const hours = parseInt(req.query.hours) || 24;

        if (!userId) {
            return res.status(400).json({
                success: false,
                message: '사용자 ID가 필요합니다.'
            });
        }

        const data = await db.getMonitoringDataByUser(userId, hours);

        res.json({
            success: true,
            data: data,
            period: `${hours}시간`
        });

    } catch (error) {
        console.error('모니터링 데이터 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '모니터링 데이터 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 모니터링 상태 조회
router.get('/status', (req, res) => {
    res.json({
        success: true,
        is_running: true,
        message: '모니터링 서비스가 실행 중입니다.',
        timestamp: new Date().toISOString()
    });
});

// 모니터링 시작
router.post('/start', (req, res) => {
    res.json({
        success: true,
        message: '모니터링이 시작되었습니다.',
        timestamp: new Date().toISOString()
    });
});

// 모니터링 중지
router.post('/stop', (req, res) => {
    res.json({
        success: true,
        message: '모니터링이 중지되었습니다.',
        timestamp: new Date().toISOString()
    });
});

module.exports = router;