#!/usr/bin/env python3
"""
테스트용 스펙트로그램 생성 스크립트
기존 오디오 파일에서 스펙트로그램 이미지를 생성합니다.
"""

import os
import sys
from pathlib import Path
import logging

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_spectrograms_from_audio():
    """오디오 파일에서 스펙트로그램 생성"""
    try:
        from ai.preprocessor import AudioPreprocessor
        
        # 스펙트로그램 출력 디렉토리
        output_dir = Path("data/spectrograms")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 오디오 파일 찾기
        audio_dirs = [
            Path("data/labeling_ready"),
            Path("data/real_audio_uploads"),
            Path("data/high_quality_sounds/normal_compressor"),
            Path("data/high_quality_sounds/abnormal_overload"),
        ]
        
        audio_files = []
        for audio_dir in audio_dirs:
            if audio_dir.exists():
                audio_files.extend(list(audio_dir.glob("*.wav")))
                audio_files.extend(list(audio_dir.glob("*.mp3")))
        
        if not audio_files:
            logger.warning("오디오 파일을 찾을 수 없습니다.")
            logger.info("테스트용 더미 스펙트로그램을 생성합니다...")
            create_dummy_spectrograms(output_dir)
            return
        
        logger.info(f"{len(audio_files)}개의 오디오 파일을 찾았습니다.")
        
        # 전처리기 초기화
        preprocessor = AudioPreprocessor()
        
        # 각 오디오 파일에서 스펙트로그램 생성 (최대 10개)
        created_count = 0
        for audio_file in audio_files[:10]:  # 최대 10개만 생성
            try:
                logger.info(f"처리 중: {audio_file.name}")
                
                # 스펙트로그램 생성 (노이즈 제거 없이 직접 생성)
                spectrogram_path = preprocessor.create_spectrogram(
                    str(audio_file),
                    output_dir=str(output_dir),
                    image_size=(256, 256),
                    colormap='magma'
                )
                
                if spectrogram_path:
                    created_count += 1
                    logger.info(f"✅ 생성 완료: {spectrogram_path}")
                    
            except Exception as e:
                logger.error(f"오디오 처리 실패 ({audio_file.name}): {e}")
                continue
        
        logger.info(f"총 {created_count}개의 스펙트로그램이 생성되었습니다.")
        logger.info(f"출력 디렉토리: {output_dir}")
        
    except ImportError as e:
        logger.error(f"필요한 모듈을 찾을 수 없습니다: {e}")
        logger.info("테스트용 더미 스펙트로그램을 생성합니다...")
        output_dir = Path("data/spectrograms")
        output_dir.mkdir(parents=True, exist_ok=True)
        create_dummy_spectrograms(output_dir)
    except Exception as e:
        logger.error(f"스펙트로그램 생성 실패: {e}")
        import traceback
        traceback.print_exc()


def create_dummy_spectrograms(output_dir: Path):
    """테스트용 더미 스펙트로그램 생성 (numpy, matplotlib만 사용)"""
    try:
        import numpy as np
        import matplotlib.pyplot as plt
        
        logger.info("테스트용 더미 스펙트로그램 생성 중...")
        
        # 5개의 더미 스펙트로그램 생성
        for i in range(5):
            # 랜덤 스펙트로그램 데이터 생성
            np.random.seed(42 + i)
            data = np.random.rand(128, 256)  # 멜 스펙트로그램 크기
            
            # 이미지 생성
            plt.figure(figsize=(10, 8))
            plt.imshow(data, cmap='magma', aspect='auto', origin='lower')
            plt.axis('off')
            plt.tight_layout(pad=0)
            
            # 저장
            output_path = output_dir / f"test_spectrogram_{i+1:03d}.png"
            plt.savefig(output_path, bbox_inches='tight', pad_inches=0, 
                       facecolor='black', edgecolor='none', dpi=100)
            plt.close()
            
            logger.info(f"✅ 더미 스펙트로그램 생성: {output_path}")
        
        logger.info(f"✅ 총 5개의 테스트용 스펙트로그램이 생성되었습니다.")
        logger.info(f"출력 디렉토리: {output_dir}")
        
    except Exception as e:
        logger.error(f"더미 스펙트로그램 생성 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("테스트용 스펙트로그램 생성")
    print("=" * 60)
    print("")
    
    generate_spectrograms_from_audio()
    
    print("")
    print("=" * 60)
    print("✅ 완료!")
    print("=" * 60)
    print("")
    print("이제 Streamlit에서 다음 경로를 사용하세요:")
    print("  data/spectrograms")
    print("")

