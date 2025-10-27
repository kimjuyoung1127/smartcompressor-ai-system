#!/usr/bin/env node

/**
 * ESP32 데이터의 타임스탬프를 원래대로 복구하는 스크립트
 * 
 * 실행 방법:
 *   node scripts/recover_timestamps.js
 */

const fs = require('fs');
const path = require('path');

const featuresDir = path.join(__dirname, '../data/esp32_features');

console.log('🔄 ESP32 타임스탬프 복구 시작...');
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
        
        // 파일명에서 timestamp 추출 (파일명 형식: features_ICE_STORE_24H_002_1761561419679.json)
        const fileName = file.replace('.json', '');
        const parts = fileName.split('_');
        const fileTimestamp = parts.length >= 3 ? parseInt(parts[parts.length - 1]) : null;
        
        // 각 항목의 타임스탬프를 복구
        dataArray.forEach(item => {
            // timestamp가 1970년대인 경우 (잘못된 변환)
            if (item.timestamp) {
                const date = new Date(item.timestamp);
                const year = date.getFullYear();
                
                // 1970년대 데이터는 파일명의 timestamp로 복구
                if (year >= 1970 && year < 1980 && fileTimestamp) {
                    // received_at을 기준으로 올바른 timestamp 계산
                    if (item.received_at) {
                        const receivedDate = new Date(item.received_at);
                        const correctTimestamp = receivedDate.getTime();
                        
                        if (correctTimestamp !== item.timestamp) {
                            item.timestamp = correctTimestamp;
                            modified = true;
                        }
                    }
                }
            }
        });
        
        if (modified) {
            // 배열 또는 단일 객체로 다시 저장
            const finalData = Array.isArray(data) ? dataArray : dataArray[0];
            fs.writeFileSync(filePath, JSON.stringify(finalData, null, 2));
            totalUpdated++;
            console.log(`✅ [${index + 1}/${files.length}] ${file} 복구됨`);
        }
        
    } catch (error) {
        console.error(`❌ [${index + 1}/${files.length}] ${file} 오류:`, error.message);
        totalErrors++;
    }
});

console.log('\n📊 복구 완료');
console.log(`✅ 업데이트된 파일: ${totalUpdated}개`);
console.log(`❌ 오류 발생 파일: ${totalErrors}개`);
console.log(`📄 총 파일 수: ${files.length}개`);

