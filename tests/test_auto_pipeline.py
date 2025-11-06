#!/usr/bin/env python3
"""
자동 라벨링 파이프라인 테스트
"""

import os
import sys
import time
import requests
from datetime import datetime

def test_labeling_server():
    """라벨링 서버 상태 테스트"""
    print("🔍 라벨링 서버 상태 확인 중...")
    
    try:
        response = requests.get("http://localhost:3000/api/labeling/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 라벨링 서버 정상 작동")
            print(f"   전체 파일: {stats['stats']['total']}개")
            print(f"   라벨링 대기: {stats['stats']['ready']}개")
            print(f"   라벨링 완료: {stats['stats']['labeled']}개")
            return True
        else:
            print(f"❌ 라벨링 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 라벨링 서버 연결 실패: {e}")
        return False

def test_file_upload():
    """파일 업로드 테스트"""
    print("\n📤 파일 업로드 테스트 중...")
    
    # 테스트용 더미 파일 생성
    test_file_path = "test_audio.wav"
    if not os.path.exists(test_file_path):
        # 간단한 WAV 파일 생성 (1초 길이)
        import numpy as np
        import soundfile as sf
        
        sample_rate = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440Hz 사인파
        
        sf.write(test_file_path, audio, sample_rate)
        print(f"✅ 테스트 파일 생성: {test_file_path}")
    
    try:
        # 파일 업로드
        with open(test_file_path, 'rb') as f:
            files = {'audio': (test_file_path, f, 'audio/wav')}
            data = {
                'fileName': f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.wav',
                'suggestedLabel': 'normal',
                'fileSize': os.path.getsize(test_file_path),
                'createdTime': datetime.now().isoformat(),
                'status': 'ready_for_labeling'
            }
            
            response = requests.post(
                "http://localhost:3000/api/labeling/upload",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 파일 업로드 성공: {result['data']['fileName']}")
                return True
            else:
                print(f"❌ 업로드 실패: {result.get('message')}")
                return False
        else:
            print(f"❌ 업로드 실패: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 파일 업로드 오류: {e}")
        return False
    finally:
        # 테스트 파일 정리
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_auto_pipeline():
    """자동 파이프라인 테스트"""
    print("\n🔄 자동 파이프라인 테스트 중...")
    
    try:
        # 자동 파이프라인 실행
        from ai.auto_labeling_pipeline import AutoLabelingPipeline
        
        pipeline = AutoLabelingPipeline()
        result = pipeline.run_pipeline(max_files=5)
        
        if result['success']:
            print(f"✅ 파이프라인 실행 성공")
            print(f"   발견된 파일: {result['total_found']}개")
            print(f"   처리된 파일: {result['processed']}개")
            print(f"   실패한 파일: {result['failed']}개")
            return True
        else:
            print(f"❌ 파이프라인 실행 실패: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 파이프라인 테스트 오류: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 자동 라벨링 파이프라인 테스트 시작")
    print("=" * 50)
    
    # 1. 라벨링 서버 상태 확인
    server_ok = test_labeling_server()
    
    if not server_ok:
        print("\n❌ 라벨링 서버가 실행되지 않았습니다.")
        print("   다음 명령어로 서버를 시작하세요:")
        print("   node simple_labeling_server.js")
        return False
    
    # 2. 파일 업로드 테스트
    upload_ok = test_file_upload()
    
    # 3. 자동 파이프라인 테스트
    pipeline_ok = test_auto_pipeline()
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    print(f"라벨링 서버: {'✅ 정상' if server_ok else '❌ 오류'}")
    print(f"파일 업로드: {'✅ 정상' if upload_ok else '❌ 오류'}")
    print(f"자동 파이프라인: {'✅ 정상' if pipeline_ok else '❌ 오류'}")
    
    if server_ok and upload_ok and pipeline_ok:
        print("\n🎉 모든 테스트 통과! 자동 라벨링 파이프라인이 정상 작동합니다.")
        return True
    else:
        print("\n⚠️ 일부 테스트 실패. 설정을 확인해주세요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
