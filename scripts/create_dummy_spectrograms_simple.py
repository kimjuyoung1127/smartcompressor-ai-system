#!/usr/bin/env python3
"""
간단한 테스트용 스펙트로그램 생성 (numpy, matplotlib만 필요)
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os

def create_dummy_spectrograms():
    """테스트용 더미 스펙트로그램 생성"""
    output_dir = Path("data/spectrograms")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"테스트용 스펙트로그램 생성 중...")
    print(f"출력 디렉토리: {output_dir}")
    
    # 10개의 더미 스펙트로그램 생성
    for i in range(10):
        # 랜덤 스펙트로그램 데이터 생성 (다양한 패턴)
        np.random.seed(42 + i)
        
        # 시간 축에 따른 변화 패턴
        time_points = 256
        freq_bins = 128
        
        # 기본 패턴 생성
        data = np.zeros((freq_bins, time_points))
        
        # 주파수별 패턴 (낮은 주파수에서 높은 주파수로)
        for freq_idx in range(freq_bins):
            # 시간에 따른 진동 패턴
            time_pattern = np.sin(2 * np.pi * freq_idx / 50 * np.arange(time_points)) * 0.5 + 0.5
            # 주파수 특성
            freq_pattern = np.exp(-freq_idx / 30)  # 고주파 감쇠
            data[freq_idx, :] = time_pattern * freq_pattern
        
        # 노이즈 추가
        noise = np.random.rand(freq_bins, time_points) * 0.1
        data = data + noise
        
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
        
        print(f"✅ 생성: {output_path.name}")
    
    print(f"\n✅ 총 10개의 테스트용 스펙트로그램이 생성되었습니다!")
    print(f"이제 Streamlit에서 'data/spectrograms' 경로를 사용하세요.")

if __name__ == "__main__":
    create_dummy_spectrograms()

