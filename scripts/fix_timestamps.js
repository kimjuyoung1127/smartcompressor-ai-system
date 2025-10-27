#!/usr/bin/env node

/**
 * ESP32 데이터의 타임스탬프 형식을 통일하는 스크립트
 * 
 * 실행 방법:
 *   node scripts/fix_timestamps.js
 */

const fs = require('fs');
const path = require('path');

const featuresDir = path.join(__dirname, '../data/esp32_features');

console.log('🔄 ESP32 타임스탬프 정규화 시작...');
console.log(`📁 디렉토리: ${featuresDir}`);

if (!fs.existsSync(featuresDir)) {
    console.error('❌ 디렉토리가 존재하지 않습니다:', featuresDir);
    process.exit(1);
}

// 모든 JSON 파일 찾기
const files = fs.readdirSync(featuresDir)
    .filter(file => file.endsWith('.json') && !file.startsWith('test_'));

console.log(`📄 발견된 파일: ${files.length}개`);

let totalUpdated = 0;
let totalErrors = 0;

files.forEach((file, index) => {
    try {
        const filePath = path.join(featuresDir, file);
        let content = fs.readFileSync(filePath, 'utf8');
        let data = JSON.parse(content);
        
        let modified = false;
        let dataArray = Array.isArray(data) ? data : [data];
        
        // 각 항목의 타임스탬프를 수정
        dataArray.forEach(item => {
            if (item.timestamp) {
                // 현재 timestamp 값 확인
                const originalTimestamp = item.timestamp;
                let newTimestamp;
                
                // timestamp가 문자열인 경우 (예: "2025-10-27T...")
                if (typeof originalTimestamp === 'string') {
                    const date = new Date(originalTimestamp);
                    newTimestamp = date.getTime();
                }
                // timestamp가 숫자지만 잘못된 형식인 경우 (예: 79514)
                else if (typeof originalTimestamp === 'number') {
                    // timestamp가 너무 작은 경우 (예: 79514는 밀리초가 아님)
                    if (originalTimestamp < 1000000000) {
                        // 초 단위로 가정하여 밀리초로 변환
                        newTimestamp = originalTimestamp * 1000;
                    } else if (originalTimestamp < 1000000000000) {
                        // 밀리초로 가정
                        newTimestamp = originalTimestamp;
                    } else {
                        // 이미 올바른 형식 (예: 1761437340000)
                        newTimestamp = originalTimestamp;
                    }
                }
                
                // timestamp가 변경된 경우
                if (newTimestamp && newTimestamp !== originalTimestamp) {
                    item.timestamp = newTimestamp;
                    modified = true;
                }
                
                // received_at이 없는 경우 추가
                if (!item.received_at && item.server_timestamp) {
                    const date = new Date(item.server_timestamp);
                    item.received_at = date.toISOString();
                    modified = true;
                }
            }
        });
        
        if (modified) {
            // 배열 또는 단일 객체로 다시 저장
            const finalData = Array.isArray(data) ? dataArray : dataArray[0];
            fs.writeFileSync(filePath, JSON.stringify(finalData, null, 2));
            totalUpdated++;
            console.log(`✅ [${index + 1}/${files.length}] ${file} 업데이트됨`);
        }
        
    } catch (error) {
        console.error(`❌ [${index + 1}/${files.length}] ${file} 오류:`, error.message);
        totalErrors++;
    }
});

console.log('\n📊 정규화 완료');
console.log(`✅ 업데이트된 파일: ${totalUpdated}개`);
console.log(`❌ 오류 발생 파일: ${totalErrors}개`);
console.log(`📄 총 파일 수: ${files.length}개`);

