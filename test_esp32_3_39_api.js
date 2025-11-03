const http = require('http');

// ESP32에서 보내는 것과 동일한 데이터 구조
const testData = {
    device_id: "ICE_STORE_24H_002",
    timestamp: Date.now(),
    sensor_number: "002",
    store_type: "ice_cream_24h",
    location: "bupyeong_branch",
    rms_energy: 150.5,
    spectral_centroid: 3500.0,
    zero_crossing_rate: 0.12,
    decibel_level: 47.5,
    compressor_state: 1.0,
    anomaly_score: 0.15,
    efficiency_score: 0.85,
    sound_type: 1.0,
    intensity_level: 0.6
};

const postData = JSON.stringify(testData);

// 3.39.124.0:3000으로 요청 (ESP32가 사용하는 주소)
const options = {
    hostname: '3.39.124.0',
    port: 3000,
    path: '/api/esp32/features',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData),
        'X-Device-ID': 'ICE_STORE_24H_002',
        'X-Store-Type': 'ice_cream_24h',
        'X-Location': 'bupyeong_branch'
    }
};

console.log('=== ESP32 3.39.124.0 API 테스트 시작 ===');
console.log('서버:', `http://${options.hostname}:${options.port}${options.path}`);
console.log('데이터:', JSON.stringify(testData, null, 2));

const req = http.request(options, (res) => {
    console.log(`\n=== 응답 수신 ===`);
    console.log(`상태 코드: ${res.statusCode}`);
    console.log(`응답 헤더:`, res.headers);
    
    let responseData = '';
    res.on('data', (chunk) => {
        responseData += chunk;
    });
    
    res.on('end', () => {
        console.log(`응답 본문:`, responseData);
        try {
            const parsed = JSON.parse(responseData);
            console.log(`파싱된 응답:`, JSON.stringify(parsed, null, 2));
        } catch (e) {
            console.log(`JSON 파싱 실패:`, e.message);
        }
        console.log('\n=== 테스트 완료 ===');
    });
});

req.on('error', (e) => {
    console.error(`요청 오류: ${e.message}`);
    console.error(`오류 코드: ${e.code}`);
    console.error(`오류 세부사항:`, e);
});

req.setTimeout(10000, () => {
    console.error('요청 타임아웃 (10초)');
    req.destroy();
});

req.write(postData);
req.end();
