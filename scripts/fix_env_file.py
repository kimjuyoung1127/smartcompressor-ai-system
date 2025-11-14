#!/usr/bin/env python3
"""
.env 파일의 null 바이트 문제 해결 스크립트
"""

import os
from pathlib import Path

def fix_env_file(env_path=".env"):
    """.env 파일의 null 바이트 제거"""
    if not os.path.exists(env_path):
        print(f"⚠️ {env_path} 파일이 없습니다.")
        return False
    
    try:
        # 원본 파일 백업
        backup_path = f"{env_path}.backup"
        if os.path.exists(env_path):
            with open(env_path, 'rb') as f:
                original_content = f.read()
            
            # 백업
            with open(backup_path, 'wb') as f:
                f.write(original_content)
            print(f"✅ 백업 생성: {backup_path}")
        
        # null 바이트 제거
        with open(env_path, 'rb') as f:
            content = f.read()
        
        # null 바이트 제거
        cleaned_content = content.replace(b'\x00', b'')
        
        # 수정된 내용 저장
        with open(env_path, 'wb') as f:
            f.write(cleaned_content)
        
        print(f"✅ {env_path} 파일 수정 완료")
        print(f"   - null 바이트 제거됨")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print(".env 파일 null 바이트 제거")
    print("="*60)
    print()
    
    fix_env_file()

