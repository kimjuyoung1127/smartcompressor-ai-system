#!/usr/bin/env python3
"""ESP32 데이터 타임스탬프 수정 스크립트"""

import json
import os
from datetime import datetime

def fix_timestamps(filepath):
    """파일의 타임스탬프를 수정"""
    print(f"Processing: {filepath}")
    
    # 파일 읽기
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        print(f"  Error: File is not a JSON array")
        return False
    
    print(f"  Total records: {len(data)}")
    
    # 파일명에서 날짜 추출
    filename = os.path.basename(filepath)
    # ICE_STORE_24H_002_2025-10-20.json -> 2025-10-20
    date_str = filename.split('_')[-1].replace('.json', '')
    base_date = datetime.strptime(date_str, '%Y-%m-%d')
    
    # 수정된 데이터 수
    modified_count = 0
    
    # 각 레코드 처리
    for i, record in enumerate(data):
        # 타임스탬프가 없거나 잘못된 경우 수정
        if 'timestamp' not in record or record['timestamp'] < 1000000000:
            # 시작 시간: 해당 날짜 00:00:00
            start_time = int(base_date.timestamp() * 1000)
            # 15초 간격으로 증가 (센서 전송 간격)
            record['timestamp'] = start_time + (i * 15000)
            modified_count += 1
    
    print(f"  Modified records: {modified_count}")
    
    # 백업
    backup_path = filepath + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"  Backup created: {backup_path}")
    
    # 수정된 파일 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"  Fixed file saved")
    
    return True

if __name__ == '__main__':
    files = [
        '/var/www/smartcompressor/data/esp32_features/ICE_STORE_24H_002_2025-10-20.json',
        '/var/www/smartcompressor/data/esp32_features/ICE_STORE_24H_002_2025-10-21.json',
        '/var/www/smartcompressor/data/esp32_features/ICE_STORE_24H_002_2025-10-22.json'
    ]
    
    for filepath in files:
        if os.path.exists(filepath):
            fix_timestamps(filepath)
            print()
        else:
            print(f"File not found: {filepath}")
