/**
 * Customer Dashboard API
 * 대시보드 요약 데이터 제공
 */

const express = require('express');
const router = express.Router();
const { authenticateSession } = require('../../middleware/auth');
const { requireRole } = require('../../middleware/rbac');

// 권한 체크 미들웨어
const customerAuth = [
    authenticateSession,
    requireRole(['admin', 'premium_user'])
];

/**
 * 대시보드 요약 데이터
 * GET /api/customer/dashboard/summary
 */
router.get('/summary', customerAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        
        // TODO: 실제 데이터베이스에서 데이터 가져오기
        // 현재는 목업 데이터 반환
        const summary = {
            totalDevices: 0,
            onlineDevices: 0,
            offlineDevices: 0,
            activeAnomalies: 0,
            resolvedAnomalies: 0,
            lastUpdate: new Date().toISOString()
        };
        
        res.json({
            success: true,
            data: summary,
            meta: {
                has_data: false,
                empty_reason: 'no_devices_registered',
                suggestion: '디바이스를 추가하여 시작하세요',
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('대시보드 요약 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'SUMMARY_ERROR',
                message: '대시보드 요약 데이터를 불러올 수 없습니다',
                details: error.message
            }
        });
    }
});

/**
 * 최근 활동 내역
 * GET /api/customer/dashboard/recent-activity
 */
router.get('/recent-activity', customerAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        const limit = parseInt(req.query.limit) || 10;
        
        // TODO: 실제 데이터베이스에서 최근 활동 가져오기
        const activities = [];
        
        res.json({
            success: true,
            data: activities,
            meta: {
                has_data: activities.length > 0,
                count: activities.length,
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('최근 활동 조회 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'ACTIVITY_ERROR',
                message: '최근 활동을 불러올 수 없습니다',
                details: error.message
            }
        });
    }
});

/**
 * 대시보드 차트 데이터
 * GET /api/customer/dashboard/charts
 */
router.get('/charts', customerAuth, async (req, res) => {
    try {
        const userId = req.user.userId;
        const timeRange = req.query.range || '7d'; // 7d, 30d, 90d
        
        // TODO: 실제 차트 데이터 생성
        const chartData = {
            deviceStatus: {
                labels: ['온라인', '오프라인', '점검중', '오류'],
                data: [0, 0, 0, 0]
            },
            sensorTrends: {
                labels: [],
                datasets: []
            },
            anomalyTrends: {
                labels: [],
                data: []
            }
        };
        
        res.json({
            success: true,
            data: chartData,
            meta: {
                has_data: false,
                timeRange: timeRange,
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        console.error('차트 데이터 오류:', error);
        res.status(500).json({
            success: false,
            error: {
                code: 'CHART_ERROR',
                message: '차트 데이터를 불러올 수 없습니다',
                details: error.message
            }
        });
    }
});

module.exports = router;
