const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');

// ESP32 특징 데이터 저장
router.post('/features', (req, res) => {
    try {
        const features = req.body;
        const deviceId = req.headers['x-device-id'] || 'unknown';
        
        console.log(`ESP32 특징 데이터 수신 - Device: ${deviceId}`);
        console.log(`RMS: ${features.rms_energy}, Compressor: ${features.compressor_state > 0.5 ? 'ON' : 'OFF'}`);
        console.log(`Anomaly: ${features.anomaly_score}, Efficiency: ${features.efficiency_score}`);
        
        // 특징 데이터를 파일로 저장
        const featuresDir = path.join(__dirname, '../../data/features');
        if (!fs.existsSync(featuresDir)) {
            fs.mkdirSync(featuresDir, { recursive: true });
        }
        
        const filename = `features_${deviceId}_${Date.now()}.json`;
        const filepath = path.join(featuresDir, filename);
        
        // 메타데이터 추가
        const dataWithMeta = {
            ...features,
            received_at: new Date().toISOString(),
            device_id: deviceId,
            store_type: req.headers['x-store-type'] || 'unknown'
        };
        
        fs.writeFileSync(filepath, JSON.stringify(dataWithMeta, null, 2));
        
        // 압축기 상태 변화 감지
        detectCompressorStateChange(features, deviceId);
        
        // 이상 패턴 감지
        detectAnomaly(features, deviceId);
        
        res.json({
            success: true,
            message: '특징 데이터 저장 완료',
            device_id: deviceId,
            timestamp: features.timestamp,
            data_size: JSON.stringify(dataWithMeta).length
        });
        
    } catch (error) {
        console.error('특징 데이터 처리 오류:', error);
        res.status(500).json({
            success: false,
            message: '특징 데이터 처리 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 압축기 상태 변화 감지
function detectCompressorStateChange(features, deviceId) {
    const stateFile = path.join(__dirname, '../../data/features', `state_${deviceId}.json`);
    
    let lastState = { compressor_state: 0, timestamp: 0 };
    if (fs.existsSync(stateFile)) {
        try {
            lastState = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
        } catch (e) {
            console.log('상태 파일 읽기 실패, 새로 시작');
        }
    }
    
    const currentState = features.compressor_state > 0.5 ? 1 : 0;
    const lastCompressorState = lastState.compressor_state > 0.5 ? 1 : 0;
    
    if (currentState !== lastCompressorState) {
        const stateChange = {
            device_id: deviceId,
            timestamp: features.timestamp,
            from_state: lastCompressorState ? 'ON' : 'OFF',
            to_state: currentState ? 'ON' : 'OFF',
            rms_energy: features.rms_energy,
            anomaly_score: features.anomaly_score,
            efficiency_score: features.efficiency_score
        };
        
        console.log(`🔄 압축기 상태 변화: ${stateChange.from_state} → ${stateChange.to_state}`);
        
        // 상태 변화 로그 저장
        const changeLogFile = path.join(__dirname, '../../data/features', `state_changes_${deviceId}.json`);
        let changes = [];
        if (fs.existsSync(changeLogFile)) {
            try {
                changes = JSON.parse(fs.readFileSync(changeLogFile, 'utf8'));
            } catch (e) {
                changes = [];
            }
        }
        
        changes.push(stateChange);
        fs.writeFileSync(changeLogFile, JSON.stringify(changes, null, 2));
    }
    
    // 현재 상태 저장
    fs.writeFileSync(stateFile, JSON.stringify({
        compressor_state: features.compressor_state,
        timestamp: features.timestamp,
        rms_energy: features.rms_energy,
        anomaly_score: features.anomaly_score
    }));
}

// 이상 패턴 감지
function detectAnomaly(features, deviceId) {
    const anomalyThreshold = 0.7;
    const efficiencyThreshold = 0.3;
    
    if (features.anomaly_score > anomalyThreshold) {
        console.log(`⚠️ 이상 패턴 감지 - Device: ${deviceId}, Score: ${features.anomaly_score}`);
        
        const anomaly = {
            device_id: deviceId,
            timestamp: features.timestamp,
            anomaly_score: features.anomaly_score,
            rms_energy: features.rms_energy,
            compressor_state: features.compressor_state > 0.5 ? 'ON' : 'OFF',
            efficiency_score: features.efficiency_score,
            temperature_estimate: features.temperature_estimate,
            detected_at: new Date().toISOString()
        };
        
        // 이상 로그 저장
        const anomalyFile = path.join(__dirname, '../../data/features', `anomalies_${deviceId}.json`);
        let anomalies = [];
        if (fs.existsSync(anomalyFile)) {
            try {
                anomalies = JSON.parse(fs.readFileSync(anomalyFile, 'utf8'));
            } catch (e) {
                anomalies = [];
            }
        }
        
        anomalies.push(anomaly);
        fs.writeFileSync(anomalyFile, JSON.stringify(anomalies, null, 2));
    }
    
    if (features.efficiency_score < efficiencyThreshold) {
        console.log(`🔧 효율성 저하 감지 - Device: ${deviceId}, Efficiency: ${features.efficiency_score}`);
    }
}

// 특징 데이터 조회
router.get('/features/:deviceId', (req, res) => {
    try {
        const deviceId = req.params.deviceId;
        const featuresDir = path.join(__dirname, '../../data/features');
        
        if (!fs.existsSync(featuresDir)) {
            return res.json([]);
        }
        
        const files = fs.readdirSync(featuresDir)
            .filter(file => file.startsWith(`features_${deviceId}_`))
            .map(file => {
                const filepath = path.join(featuresDir, file);
                const stats = fs.statSync(filepath);
                return {
                    filename: file,
                    size: stats.size,
                    modified: stats.mtime.toISOString()
                };
            })
            .sort((a, b) => new Date(b.modified) - new Date(a.modified));
        
        res.json(files);
        
    } catch (error) {
        console.error('특징 데이터 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '특징 데이터 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 압축기 상태 변화 조회
router.get('/state-changes/:deviceId', (req, res) => {
    try {
        const deviceId = req.params.deviceId;
        const changeLogFile = path.join(__dirname, '../../data/features', `state_changes_${deviceId}.json`);
        
        if (!fs.existsSync(changeLogFile)) {
            return res.json([]);
        }
        
        const changes = JSON.parse(fs.readFileSync(changeLogFile, 'utf8'));
        res.json(changes);
        
    } catch (error) {
        console.error('상태 변화 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '상태 변화 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 이상 패턴 조회
router.get('/anomalies/:deviceId', (req, res) => {
    try {
        const deviceId = req.params.deviceId;
        const anomalyFile = path.join(__dirname, '../../data/features', `anomalies_${deviceId}.json`);
        
        if (!fs.existsSync(anomalyFile)) {
            return res.json([]);
        }
        
        const anomalies = JSON.parse(fs.readFileSync(anomalyFile, 'utf8'));
        res.json(anomalies);
        
    } catch (error) {
        console.error('이상 패턴 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '이상 패턴 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

module.exports = router;
