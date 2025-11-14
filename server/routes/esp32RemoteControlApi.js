const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');

// 디바이스 상태 저장 (메모리 기반, 실제로는 DB 사용 권장)
const deviceStatus = {};
const deviceHeartbeats = {};

/**
 * 하트비트 수신 - 센서가 주기적으로 상태를 전송
 * POST /api/esp32/heartbeat
 */
router.post('/heartbeat', (req, res) => {
    try {
        const deviceId = req.headers['x-device-id'] || req.body.device_id || 'unknown';
        const timestamp = Date.now();
        
        console.log(`[HEARTBEAT] Device: ${deviceId}, Timestamp: ${new Date().toISOString()}`);
        
        // 디바이스 상태 저장
        deviceStatus[deviceId] = {
            ...req.body,
            last_heartbeat: timestamp,
            last_update: new Date().toISOString(),
            online: true
        };
        
        // 하트비트 기록
        if (!deviceHeartbeats[deviceId]) {
            deviceHeartbeats[deviceId] = [];
        }
        deviceHeartbeats[deviceId].push({
            timestamp,
            ...req.body
        });
        
        // 최근 100개만 유지
        if (deviceHeartbeats[deviceId].length > 100) {
            deviceHeartbeats[deviceId] = deviceHeartbeats[deviceId].slice(-100);
        }
        
        res.json({
            success: true,
            message: 'Heartbeat received',
            timestamp
        });
        
    } catch (error) {
        console.error('Heartbeat 오류:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 디바이스 상태 조회 - 원격 모니터링
 * GET /api/esp32/device/:deviceId
 */
router.get('/device/:deviceId', (req, res) => {
    try {
        const deviceId = req.params.deviceId;
        const status = deviceStatus[deviceId];
        
        if (!status) {
            return res.status(404).json({
                success: false,
                error: 'Device not found',
                message: `디바이스 ${deviceId}의 상태를 찾을 수 없습니다.`
            });
        }
        
        // 온라인 여부 확인 (마지막 하트비트가 1분 이내면 온라인)
        const isOnline = (Date.now() - status.last_heartbeat) < 60000;
        status.online = isOnline;
        
        // 하트비트 히스토리
        const heartbeats = deviceHeartbeats[deviceId] || [];
        
        res.json({
            success: true,
            device_id: deviceId,
            is_online: isOnline,
            current_status: status,
            recent_heartbeats: heartbeats.slice(-10), // 최근 10개
            stats: {
                total_heartbeats: heartbeats.length,
                last_seen: new Date(status.last_heartbeat).toISOString(),
                uptime: status.uptime || 0
            }
        });
        
    } catch (error) {
        console.error('디바이스 상태 조회 오류:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 모든 디바이스 목록
 * GET /api/esp32/devices
 */
router.get('/devices', (req, res) => {
    try {
        const devices = Object.keys(deviceStatus).map(deviceId => {
            const status = deviceStatus[deviceId];
            const isOnline = (Date.now() - status.last_heartbeat) < 60000;
            
            return {
                device_id: deviceId,
                is_online: isOnline,
                last_seen: new Date(status.last_heartbeat).toISOString(),
                wifi_connected: status.wifi_connected,
                system_healthy: status.system_healthy,
                error_counts: status.error_counts || {},
                uptime: status.uptime
            };
        });
        
        res.json({
            success: true,
            devices,
            total: devices.length,
            online: devices.filter(d => d.is_online).length
        });
        
    } catch (error) {
        console.error('디바이스 목록 조회 오류:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 리부트 명령 전송
 * POST /api/esp32/device/:deviceId/reboot
 */
router.post('/device/:deviceId/reboot', (req, res) => {
    try {
        const deviceId = req.params.deviceId;
        const status = deviceStatus[deviceId];
        
        if (!status) {
            return res.status(404).json({
                success: false,
                error: 'Device not found'
            });
        }
        
        // 리부트 명령을 디바이스 상태에 저장
        // 실제로는 MQTT나 OTA 업데이트를 통해 명령 전송
        deviceStatus[deviceId].reboot_requested = true;
        deviceStatus[deviceId].reboot_requested_at = Date.now();
        
        console.log(`[REBOOT] 리부트 명령 전송: ${deviceId}`);
        
        res.json({
            success: true,
            message: '리부트 명령이 전송되었습니다.',
            device_id: deviceId,
            reboot_requested: true
        });
        
    } catch (error) {
        console.error('리부트 명령 오류:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 리부트 명령 확인 및 처리
 * GET /api/esp32/device/:deviceId/reboot/check
 */
router.get('/device/:deviceId/reboot/check', (req, res) => {
    try {
        const deviceId = req.params.deviceId;
        const status = deviceStatus[deviceId];
        
        if (!status || !status.reboot_requested) {
            return res.json({
                should_reboot: false
            });
        }
        
        // 리부트 요청이 있으면 true 반환
        res.json({
            should_reboot: true,
            reboot_requested_at: status.reboot_requested_at
        });
        
        // 리부트 요청 플래그 제거
        delete status.reboot_requested;
        delete status.reboot_requested_at;
        
    } catch (error) {
        console.error('리부트 확인 오류:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * WiFi 재연결 명령
 * POST /api/esp32/device/:deviceId/reconnect-wifi
 */
router.post('/device/:deviceId/reconnect-wifi', (req, res) => {
    try {
        const deviceId = req.params.deviceId;
        const status = deviceStatus[deviceId];
        
        if (!status) {
            return res.status(404).json({
                success: false,
                error: 'Device not found'
            });
        }
        
        // WiFi 재연결 명령
        deviceStatus[deviceId].reconnect_wifi_requested = true;
        deviceStatus[deviceId].reconnect_wifi_at = Date.now();
        
        console.log(`[WIFI] WiFi 재연결 명령 전송: ${deviceId}`);
        
        res.json({
            success: true,
            message: 'WiFi 재연결 명령이 전송되었습니다.',
            device_id: deviceId
        });
        
    } catch (error) {
        console.error('WiFi 재연결 명령 오류:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 설정 변경 명령
 * POST /api/esp32/device/:deviceId/config
 */
router.post('/device/:deviceId/config', (req, res) => {
    try {
        const deviceId = req.params.deviceId;
        const { upload_interval, heartbeat_interval, enabled } = req.body;
        
        if (!deviceStatus[deviceId]) {
            return res.status(404).json({
                success: false,
                error: 'Device not found'
            });
        }
        
        // 설정 변경 명령
        deviceStatus[deviceId].config_requested = {
            upload_interval,
            heartbeat_interval,
            enabled,
            requested_at: Date.now()
        };
        
        console.log(`[CONFIG] 설정 변경 명령 전송: ${deviceId}`, req.body);
        
        res.json({
            success: true,
            message: '설정 변경 명령이 전송되었습니다.',
            device_id: deviceId,
            new_config: req.body
        });
        
    } catch (error) {
        console.error('설정 변경 명령 오류:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 설정 조회
 * GET /api/esp32/device/:deviceId/config
 */
router.get('/device/:deviceId/config', (req, res) => {
    try {
        const deviceId = req.params.deviceId;
        const status = deviceStatus[deviceId];
        
        if (!status) {
            return res.status(404).json({
                success: false,
                error: 'Device not found'
            });
        }
        
        res.json({
            success: true,
            device_id: deviceId,
            config: status.config_requested || null,
            current_config: {
                upload_enabled: status.upload_enabled,
                wifi_connected: status.wifi_connected
            }
        });
        
    } catch (error) {
        console.error('설정 조회 오류:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

module.exports = router;
