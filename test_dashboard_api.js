const http = require('http');

// API 테스트 함수
function testApi(endpoint, description) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'localhost',
            port: 3000,
            path: endpoint,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        };

        console.log(`\n=== ${description} ===`);
        console.log(`URL: http://localhost:3000${endpoint}`);

        const req = http.request(options, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                console.log(`상태 코드: ${res.statusCode}`);
                try {
                    const parsed = JSON.parse(data);
                    console.log(`응답:`, JSON.stringify(parsed, null, 2));
                    resolve(parsed);
                } catch (e) {
                    console.log(`응답 (텍스트):`, data);
                    resolve(data);
                }
            });
        });

        req.on('error', (e) => {
            console.error(`오류: ${e.message}`);
            reject(e);
        });

        req.setTimeout(5000, () => {
            console.error('타임아웃');
            req.destroy();
            reject(new Error('타임아웃'));
        });

        req.end();
    });
}

// 모든 API 테스트
async function runTests() {
    try {
        console.log('🚀 ESP32 대시보드 API 테스트 시작');
        
        // 1. 헬스 체크
        await testApi('/api/health', '헬스 체크');
        
        // 2. 디바이스 목록
        await testApi('/api/esp32/devices', '디바이스 목록 조회');
        
        // 3. 최근 데이터
        await testApi('/api/esp32/features/recent?limit=10', '최근 데이터 조회');
        
        // 4. 통계 데이터
        await testApi('/api/esp32/stats', '통계 데이터 조회');
        
        // 5. 대시보드 페이지
        await testApi('/esp32-dashboard', '대시보드 페이지');
        
        console.log('\n✅ 모든 API 테스트 완료');
        
    } catch (error) {
        console.error('\n❌ 테스트 실패:', error.message);
    }
}

runTests();
