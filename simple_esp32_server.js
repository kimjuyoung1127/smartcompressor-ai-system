require('dotenv').config();
const express = require('express');
const path = require('path');
const fs = require('fs');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// CORS 설정 (ESP32 센서용)
app.use(cors({
    origin: ['http://localhost:3000', 'http://3.39.124.0:3000', 'https://signalcraft.kr', 'http://signalcraft.kr'],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: [
        'Content-Type', 
        'Authorization', 
        'X-Requested-With',
        'X-Device-ID',
        'X-Store-Type', 
        'X-Location',
        'Accept',
        'Origin',
        'User-Agent'
    ]
}));

// 미들웨어 설정
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// 정적 파일 서빙
app.use('/static', express.static(path.join(__dirname, 'static')));

// ESP32 특징 데이터 저장 디렉토리 생성
const featuresDir = path.join(__dirname, 'data/esp32_features');
if (!fs.existsSync(featuresDir)) {
    fs.mkdirSync(featuresDir, { recursive: true });
    console.log('✅ ESP32 데이터 디렉토리 생성:', featuresDir);
}

// ESP32 특징 데이터 저장 엔드포인트
app.post('/api/esp32/features', (req, res) => {
    try {
        console.log('=== ESP32 Features API 호출됨 ===');
        console.log('Timestamp:', new Date().toISOString());
        console.log('Request IP:', req.ip || req.connection.remoteAddress);
        console.log('Request body:', JSON.stringify(req.body, null, 2));
        console.log('Request headers:', JSON.stringify(req.headers, null, 2));
        
        const features = req.body;
        const deviceId = req.headers['x-device-id'] || features.device_id || 'unknown';
        const storeType = req.headers['x-store-type'] || features.store_type || 'unknown';
        const location = req.headers['x-location'] || features.location || 'unknown';
        
        console.log(`ESP32 특징 데이터 수신 - Device: ${deviceId}`);
        console.log(`Store Type: ${storeType}, Location: ${location}`);
        console.log(`RMS: ${features.rms_energy}, Compressor: ${features.compressor_state > 0.5 ? 'ON' : 'OFF'}`);
        console.log(`Decibel: ${features.decibel_level}dB, Anomaly: ${features.anomaly_score}, Efficiency: ${features.efficiency_score}`);
        
        // 메타데이터 추가
        const dataWithMeta = {
            ...features,
            received_at: new Date().toISOString(),
            device_id: deviceId,
            store_type: storeType,
            location: location,
            server_ip: req.ip || req.connection.remoteAddress
        };
        
        // 파일로 저장
        const filename = `features_${deviceId}_${Date.now()}.json`;
        const filepath = path.join(featuresDir, filename);
        
        fs.writeFileSync(filepath, JSON.stringify(dataWithMeta, null, 2));
        
        console.log(`✅ ESP32 데이터 저장 완료 - ${filename}`);
        console.log(`파일 크기: ${fs.statSync(filepath).size} bytes`);
        
        res.json({
            success: true,
            message: 'ESP32 특징 데이터 저장 완료',
            device_id: deviceId,
            timestamp: features.timestamp,
            data_size: JSON.stringify(dataWithMeta).length,
            filename: filename
        });
        
    } catch (error) {
        console.error('ESP32 특징 데이터 처리 오류:', error);
        res.status(500).json({
            success: false,
            message: 'ESP32 특징 데이터 처리 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// ESP32 특징 데이터 조회 엔드포인트
app.get('/api/esp32/features/recent', (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 50;
        const deviceId = req.query.device_id;
        
        console.log(`ESP32 특징 데이터 조회 - Device: ${deviceId}, Limit: ${limit}`);
        
        if (!fs.existsSync(featuresDir)) {
            return res.json({
                success: true,
                data: [],
                count: 0,
                total: 0
            });
        }
        
        // 모든 JSON 파일 찾기
        const files = fs.readdirSync(featuresDir)
            .filter(file => file.endsWith('.json'))
            .map(file => {
                const filepath = path.join(featuresDir, file);
                const stats = fs.statSync(filepath);
                return {
                    filename: file,
                    filepath: filepath,
                    modified: stats.mtime
                };
            })
            .sort((a, b) => b.modified - a.modified)
            .slice(0, limit);
        
        const data = [];
        for (const file of files) {
            try {
                const content = fs.readFileSync(file.filepath, 'utf8');
                const parsed = JSON.parse(content);
                
                if (Array.isArray(parsed)) {
                    data.push(...parsed);
                } else {
                    data.push(parsed);
                }
            } catch (err) {
                console.error(`파일 읽기 오류: ${file.filename}`, err);
            }
        }
        
        // 시간순으로 정렬 (최신이 먼저)
        data.sort((a, b) => (b.timestamp || b.server_timestamp || 0) - (a.timestamp || a.server_timestamp || 0));
        
        // 디바이스 ID 필터링
        let filteredData = data;
        if (deviceId) {
            filteredData = data.filter(item => item.device_id === deviceId);
        }
        
        // 제한된 개수만 반환
        filteredData = filteredData.slice(0, limit);
        
        res.json({
            success: true,
            data: filteredData,
            count: filteredData.length,
            total: data.length
        });
        
    } catch (error) {
        console.error('ESP32 특징 데이터 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: 'ESP32 특징 데이터 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 디바이스 목록 조회
app.get('/api/esp32/devices', (req, res) => {
    try {
        console.log('디바이스 목록 조회 요청');
        
        if (!fs.existsSync(featuresDir)) {
            return res.json({
                success: true,
                devices: [],
                total_devices: 0,
                total_data: 0
            });
        }
        
        const files = fs.readdirSync(featuresDir)
            .filter(file => file.endsWith('.json'));
        
        const devices = new Set();
        let totalDataCount = 0;
        
        files.forEach(file => {
            try {
                const filePath = path.join(featuresDir, file);
                const fileContent = fs.readFileSync(filePath, 'utf8');
                const data = JSON.parse(fileContent);
                
                if (Array.isArray(data)) {
                    data.forEach(item => {
                        if (item.device_id) {
                            devices.add(item.device_id);
                        }
                    });
                    totalDataCount += data.length;
                } else if (data.device_id) {
                    devices.add(data.device_id);
                    totalDataCount++;
                }
            } catch (error) {
                console.error(`파일 읽기 오류 ${file}:`, error.message);
            }
        });
        
        const deviceList = Array.from(devices).map(deviceId => ({
            device_id: deviceId,
            last_seen: getLastSeenTime(deviceId),
            data_count: getDataCount(deviceId)
        }));
        
        console.log(`디바이스 목록 조회 완료: ${deviceList.length}개 디바이스`);
        
        res.json({
            success: true,
            devices: deviceList,
            total_devices: deviceList.length,
            total_data: totalDataCount
        });
        
    } catch (error) {
        console.error('디바이스 목록 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '디바이스 목록 조회 실패',
            error: error.message
        });
    }
});

// 통계 데이터 조회
app.get('/api/esp32/stats', (req, res) => {
    try {
        console.log('통계 데이터 조회 요청');
        
        if (!fs.existsSync(featuresDir)) {
            return res.json({
                success: true,
                stats: {
                    total_data: 0,
                    total_devices: 0,
                    avg_rms: 0,
                    avg_anomaly: 0,
                    compressor_ratio: 0,
                    device_stats: {},
                    hourly_stats: {}
                }
            });
        }
        
        const files = fs.readdirSync(featuresDir)
            .filter(file => file.endsWith('.json'));
        
        let allData = [];
        const deviceStats = {};
        const hourlyStats = {};
        
        // 모든 데이터 수집
        files.forEach(file => {
            try {
                const filePath = path.join(featuresDir, file);
                const fileContent = fs.readFileSync(filePath, 'utf8');
                const data = JSON.parse(fileContent);
                
                if (Array.isArray(data)) {
                    allData = allData.concat(data);
                } else {
                    allData.push(data);
                }
            } catch (error) {
                console.error(`파일 읽기 오류 ${file}:`, error.message);
            }
        });
        
        // 통계 계산
        allData.forEach(item => {
            const deviceId = item.device_id;
            const hour = new Date(item.timestamp).getHours();
            
            // 디바이스별 통계
            if (!deviceStats[deviceId]) {
                deviceStats[deviceId] = {
                    count: 0,
                    total_rms: 0,
                    total_anomaly: 0,
                    compressor_on_count: 0,
                    max_rms: 0,
                    max_anomaly: 0
                };
            }
            
            deviceStats[deviceId].count++;
            deviceStats[deviceId].total_rms += item.rms_energy || 0;
            deviceStats[deviceId].total_anomaly += item.anomaly_score || 0;
            deviceStats[deviceId].max_rms = Math.max(deviceStats[deviceId].max_rms, item.rms_energy || 0);
            deviceStats[deviceId].max_anomaly = Math.max(deviceStats[deviceId].max_anomaly, item.anomaly_score || 0);
            
            if (item.compressor_state > 0.5) {
                deviceStats[deviceId].compressor_on_count++;
            }
            
            // 시간대별 통계
            if (!hourlyStats[hour]) {
                hourlyStats[hour] = {
                    count: 0,
                    total_rms: 0,
                    compressor_on_count: 0
                };
            }
            hourlyStats[hour].count++;
            hourlyStats[hour].total_rms += item.rms_energy || 0;
            if (item.compressor_state > 0.5) {
                hourlyStats[hour].compressor_on_count++;
            }
        });
        
        // 평균 계산
        Object.keys(deviceStats).forEach(deviceId => {
            const stats = deviceStats[deviceId];
            stats.avg_rms = stats.total_rms / stats.count;
            stats.avg_anomaly = stats.total_anomaly / stats.count;
            stats.compressor_ratio = stats.compressor_on_count / stats.count;
        });
        
        Object.keys(hourlyStats).forEach(hour => {
            const stats = hourlyStats[hour];
            stats.avg_rms = stats.total_rms / stats.count;
            stats.compressor_ratio = stats.compressor_on_count / stats.count;
        });
        
        // 전체 통계
        const totalData = allData.length;
        const avgRms = allData.reduce((sum, item) => sum + (item.rms_energy || 0), 0) / totalData;
        const avgAnomaly = allData.reduce((sum, item) => sum + (item.anomaly_score || 0), 0) / totalData;
        const compressorOnCount = allData.filter(item => item.compressor_state > 0.5).length;
        const compressorRatio = compressorOnCount / totalData;
        
        console.log(`통계 데이터 조회 완료: ${totalData}개 데이터`);
        
        res.json({
            success: true,
            stats: {
                total_data: totalData,
                total_devices: Object.keys(deviceStats).length,
                avg_rms: avgRms,
                avg_anomaly: avgAnomaly,
                compressor_ratio: compressorRatio,
                device_stats: deviceStats,
                hourly_stats: hourlyStats
            }
        });
        
    } catch (error) {
        console.error('통계 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '통계 조회 실패',
            error: error.message
        });
    }
});

// 헬스 체크 엔드포인트
app.get('/api/health', (req, res) => {
    res.json({
        success: true,
        message: 'ESP32 서버 정상 작동 중',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// 헬퍼 함수들
function getLastSeenTime(deviceId) {
    try {
        const files = fs.readdirSync(featuresDir)
            .filter(file => file.endsWith('.json'))
            .sort((a, b) => {
                const statA = fs.statSync(path.join(featuresDir, a));
                const statB = fs.statSync(path.join(featuresDir, b));
                return statB.mtime - statA.mtime;
            });

        for (const file of files) {
            try {
                const filePath = path.join(featuresDir, file);
                const fileContent = fs.readFileSync(filePath, 'utf8');
                const data = JSON.parse(fileContent);
                
                const items = Array.isArray(data) ? data : [data];
                const deviceData = items.find(item => item.device_id === deviceId);
                
                if (deviceData) {
                    return new Date(deviceData.timestamp).toISOString();
                }
            } catch (error) {
                continue;
            }
        }
        return null;
    } catch (error) {
        return null;
    }
}

function getDataCount(deviceId) {
    try {
        const files = fs.readdirSync(featuresDir)
            .filter(file => file.endsWith('.json'));

        let count = 0;
        files.forEach(file => {
            try {
                const filePath = path.join(featuresDir, file);
                const fileContent = fs.readFileSync(filePath, 'utf8');
                const data = JSON.parse(fileContent);
                
                const items = Array.isArray(data) ? data : [data];
                count += items.filter(item => item.device_id === deviceId).length;
            } catch (error) {
                // 무시
            }
        });
        return count;
    } catch (error) {
        return 0;
    }
}

// 간단한 대시보드 페이지
app.get('/dashboard', (req, res) => {
    res.sendFile(path.join(__dirname, 'simple_dashboard.html'));
});

// ESP32 대시보드 페이지
app.get('/esp32-dashboard', (req, res) => {
    res.removeHeader('ETag');
    res.removeHeader('Last-Modified');
    res.set('Cache-Control', 'no-cache, no-store, must-revalidate, private');
    res.set('Pragma', 'no-cache');
    res.set('Expires', '0');
    res.set('Vary', '*');
    res.sendFile(path.join(__dirname, 'static/pages/esp32_dashboard.html'));
});

// 루트 페이지
app.get('/', (req, res) => {
    res.json({
        message: 'ESP32 센서 데이터 수신 서버',
        dashboard: 'http://signalcraft.kr:3000/esp32-dashboard',
        endpoints: {
            'POST /api/esp32/features': 'ESP32 센서 데이터 저장',
            'GET /api/esp32/features/recent': '최근 데이터 조회',
            'GET /api/esp32/devices': '디바이스 목록 조회',
            'GET /api/esp32/stats': '통계 데이터 조회',
            'GET /api/health': '서버 상태 확인'
        },
        timestamp: new Date().toISOString()
    });
});

// 서버 시작
const server = app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 ESP32 센서 데이터 수신 서버가 http://0.0.0.0:${PORT} 에서 실행 중입니다`);
    console.log(`🌐 외부 접근: http://signalcraft.kr:${PORT}`);
    console.log(`🌐 ESP32 센서: http://3.39.124.0:${PORT}`);
    console.log(`📁 데이터 저장: ${featuresDir}`);
    console.log(`🔗 API 엔드포인트: /api/esp32/features`);
    console.log(`⏰ 시작 시간: ${new Date().toISOString()}`);
    console.log(`💾 SQLite 없이 파일 기반 저장 사용`);
    console.log(`🔧 ESP32 센서에서 3.39.124.0:3000으로 요청 가능`);
});

// 서버 정보 출력
server.on('listening', () => {
    const address = server.address();
    console.log(`📡 서버 주소: ${address.address}:${address.port}`);
    console.log(`🔌 프로토콜: ${address.family}`);
});

// 연결 이벤트 로깅
server.on('connection', (socket) => {
    console.log(`🔗 새 연결: ${socket.remoteAddress}:${socket.remotePort}`);
});

// 에러 처리
process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    process.exit(0);
});
