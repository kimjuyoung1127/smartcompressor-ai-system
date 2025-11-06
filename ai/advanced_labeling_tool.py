#!/usr/bin/env python3
"""
고급 스펙트로그램 라벨링 도구 (Advanced Labeling Tool)
'전문가의 직감'을 'AI가 학습 가능한 좌표'로 변환하는 포토샵 스타일 툴

시스템 1: 스펙트로그램 포토샵 툴 (로드맵 2단계 핵심 투자)
"""

import streamlit as st
import os
import json
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import io
import base64

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AdvancedLabelingTool:
    """고급 스펙트로그램 라벨링 도구 - 영역 선택 및 좌표 저장 기능"""
    
    def __init__(self):
        self.labels = {
            "정상 가동음": "normal",
            "냉매 누설": "leak", 
            "과부하": "overload",
            "기타 이상": "anomaly"
        }
        self.labeled_dir = Path("labeled_data")
        self.annotations_dir = Path("annotations")  # 좌표 데이터 저장
        self.current_image_index = 0
        self.image_files = []
        self.current_image_path = None
        self.annotations = {}  # {image_path: [regions]}
        
        # Streamlit 세션 상태 초기화
        if 'selected_regions' not in st.session_state:
            st.session_state.selected_regions = []
        if 'current_label' not in st.session_state:
            st.session_state.current_label = None
        
    def setup_directories(self):
        """라벨링 디렉토리 구조 설정"""
        # 라벨별 디렉토리 생성
        for label_name in self.labels.keys():
            label_dir = self.labeled_dir / self.labels[label_name]
            label_dir.mkdir(parents=True, exist_ok=True)
        
        # 어노테이션(좌표) 데이터 저장 디렉토리
        self.annotations_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("라벨링 디렉토리 구조 설정 완료")
    
    def load_images(self, input_dir):
        """이미지 파일들을 로드합니다."""
        self.unlabeled_dir = Path(input_dir)
        
        if not self.unlabeled_dir.exists():
            st.error(f"입력 디렉토리를 찾을 수 없습니다: {input_dir}")
            return False
        
        # 지원하는 이미지 확장자
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        
        # 이미지 파일 목록 생성
        self.image_files = []
        for ext in image_extensions:
            self.image_files.extend(list(self.unlabeled_dir.glob(f"*{ext}")))
            self.image_files.extend(list(self.unlabeled_dir.glob(f"*{ext.upper()}")))
        
        self.image_files.sort()
        
        if not self.image_files:
            st.error(f"입력 디렉토리에 이미지 파일이 없습니다: {input_dir}")
            return False
        
        logger.info(f"총 {len(self.image_files)}개의 이미지를 로드했습니다.")
        return True
    
    def load_annotations(self, image_path):
        """이미지에 대한 기존 어노테이션 로드"""
        annotation_file = self.annotations_dir / f"{image_path.stem}.json"
        if annotation_file.exists():
            with open(annotation_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"regions": [], "labeled_at": None}
    
    def save_annotations(self, image_path, regions, label):
        """어노테이션(좌표 데이터)을 JSON으로 저장"""
        annotation_file = self.annotations_dir / f"{image_path.stem}.json"
        
        annotation_data = {
            "image_path": str(image_path),
            "image_name": image_path.name,
            "label": label,
            "regions": regions,  # [{x, y, width, height, label}]
            "labeled_at": datetime.now().isoformat(),
            "labeled_by": "expert"  # 추후 사용자 정보 추가 가능
        }
        
        with open(annotation_file, 'w', encoding='utf-8') as f:
            json.dump(annotation_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"어노테이션 저장 완료: {annotation_file}")
    
    def draw_regions_on_image(self, image_path, regions):
        """스펙트로그램 이미지에 선택된 영역을 그려서 표시"""
        try:
            img = Image.open(image_path)
            img_array = np.array(img)
            
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.imshow(img_array, cmap='magma')
            ax.set_title(f"스펙트로그램: {Path(image_path).name}", fontsize=16, fontweight='bold')
            ax.axis('off')
            
            # 선택된 영역 그리기
            colors = {'normal': 'green', 'leak': 'red', 'overload': 'orange', 'anomaly': 'yellow'}
            for i, region in enumerate(regions):
                x = region['x']
                y = region['y']
                width = region['width']
                height = region['height']
                label = region['label']
                
                rect = Rectangle(
                    (x, y), width, height,
                    linewidth=2,
                    edgecolor=colors.get(label, 'blue'),
                    facecolor='none',
                    label=f"{label} ({i+1})"
                )
                ax.add_patch(rect)
                
                # 라벨 텍스트 추가
                ax.text(x, y - 5, f"{label} #{i+1}", 
                       color=colors.get(label, 'blue'),
                       fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
            
            if regions:
                ax.legend(loc='upper right')
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            st.error(f"이미지 처리 중 오류 발생: {e}")
            logger.error(f"이미지 처리 오류: {e}")
            return None
    
    def add_region_interactive(self):
        """인터랙티브 영역 추가 인터페이스"""
        st.subheader("🎯 영역 선택 도구")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**영역 좌표 입력**")
            x = st.number_input("X 좌표 (시작)", min_value=0, value=0, step=10, key="region_x")
            y = st.number_input("Y 좌표 (시작)", min_value=0, value=0, step=10, key="region_y")
            width = st.number_input("너비", min_value=10, value=50, step=10, key="region_width")
            height = st.number_input("높이", min_value=10, value=50, step=10, key="region_height")
        
        with col2:
            st.write("**영역 라벨 선택**")
            selected_label = st.selectbox(
                "이 영역의 라벨을 선택하세요:",
                options=list(self.labels.keys()),
                key="region_label_select"
            )
            
            if st.button("➕ 영역 추가", type="primary", use_container_width=True):
                new_region = {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "label": self.labels[selected_label],
                    "label_name": selected_label
                }
                st.session_state.selected_regions.append(new_region)
                st.success(f"'{selected_label}' 영역이 추가되었습니다!")
                # rerun 없이 계속 작업 가능하도록 주석 처리
                # st.rerun()
        
        # 현재 선택된 영역 목록
        if st.session_state.selected_regions:
            st.write("**선택된 영역 목록:**")
            for i, region in enumerate(st.session_state.selected_regions):
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a:
                    st.write(f"#{i+1}: {region['label_name']} - ({region['x']}, {region['y']}) 크기: {region['width']}x{region['height']}")
                with col_b:
                    if st.button("🗑️ 삭제", key=f"delete_{i}"):
                        st.session_state.selected_regions.pop(i)
                        st.success(f"영역 #{i+1}이 삭제되었습니다.")
                        st.rerun()
    
    def save_labeled_image(self, image_path, regions, label):
        """라벨링된 이미지와 어노테이션을 저장"""
        try:
            # 1. 어노테이션 JSON 저장
            self.save_annotations(image_path, regions, label)
            
            # 2. 이미지를 라벨별 폴더로 복사 (선택적)
            target_dir = self.labeled_dir / self.labels[label]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{timestamp}_{image_path.name}"
            target_path = target_dir / new_filename
            
            import shutil
            shutil.copy2(image_path, target_path)
            
            logger.info(f"라벨링 완료: {image_path.name} -> {label}")
            return True
            
        except Exception as e:
            st.error(f"저장 중 오류 발생: {e}")
            logger.error(f"저장 오류: {e}")
            return False
    
    def run_labeling_interface(self, input_dir):
        """고급 라벨링 인터페이스 실행"""
        st.set_page_config(
            page_title="고급 스펙트로그램 라벨링 도구",
            page_icon="🎨",
            layout="wide"
        )
        
        st.title("🎨 고급 스펙트로그램 전문가 라벨링 도구")
        st.markdown("**'전문가의 직감'을 'AI가 학습 가능한 좌표'로 변환하는 도구**")
        st.markdown("---")
        
        # 디렉토리 설정
        self.setup_directories()
        
        # 이미지 로드
        if not self.load_images(input_dir):
            return
        
        # 사이드바
        with st.sidebar:
            st.header("📊 진행 상황")
            total_images = len(self.image_files)
            remaining_images = len([f for f in self.image_files if f.exists()])
            progress = (total_images - remaining_images) / total_images if total_images > 0 else 0
            
            st.progress(progress)
            st.metric("전체 이미지", total_images)
            st.metric("남은 이미지", remaining_images)
            st.metric("완료율", f"{progress:.1%}")
            
            st.markdown("---")
            st.header("🏷️ 라벨 설명")
            for label_name, label_key in self.labels.items():
                st.write(f"**{label_name}** ({label_key})")
        
        # 현재 이미지 찾기
        current_image = None
        for i, img_path in enumerate(self.image_files):
            if img_path.exists():
                current_image = img_path
                self.current_image_index = i
                break
        
        if current_image is None:
            st.success("🎉 모든 이미지 라벨링이 완료되었습니다!")
            return
        
        self.current_image_path = current_image
        
        # 기존 어노테이션 로드
        existing_annotations = self.load_annotations(current_image)
        if existing_annotations.get("regions") and not st.session_state.selected_regions:
            st.session_state.selected_regions = existing_annotations["regions"]
        
        # 메인 영역
        st.header(f"📸 현재 이미지: {current_image.name}")
        st.caption(f"진행률: {self.current_image_index + 1}/{total_images}")
        
        # 이미지 표시 (선택된 영역과 함께)
        fig = self.draw_regions_on_image(current_image, st.session_state.selected_regions)
        if fig:
            st.pyplot(fig)
            plt.close(fig)
        
        # 영역 선택 도구
        st.markdown("---")
        self.add_region_interactive()
        
        # 최종 라벨 선택 및 저장
        st.markdown("---")
        st.subheader("💾 라벨링 저장")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("✅ 정상 가동음으로 저장", use_container_width=True, type="primary"):
                if self.save_labeled_image(current_image, st.session_state.selected_regions, "정상 가동음"):
                    st.session_state.selected_regions = []
                    st.success("✅ 정상 가동음으로 저장되었습니다!")
                    st.rerun()
        
        with col2:
            if st.button("⚠️ 냉매 누설로 저장", use_container_width=True):
                if self.save_labeled_image(current_image, st.session_state.selected_regions, "냉매 누설"):
                    st.session_state.selected_regions = []
                    st.success("✅ 냉매 누설로 저장되었습니다!")
                    st.rerun()
        
        with col3:
            if st.button("🚨 과부하로 저장", use_container_width=True):
                if self.save_labeled_image(current_image, st.session_state.selected_regions, "과부하"):
                    st.session_state.selected_regions = []
                    st.success("✅ 과부하로 저장되었습니다!")
                    st.rerun()
        
        with col4:
            if st.button("⏭️ 건너뛰기", use_container_width=True):
                st.session_state.selected_regions = []
                st.info("이미지를 건너뛰었습니다.")
                st.rerun()
        
        with col5:
            if st.button("🏠 초기화면으로", use_container_width=True):
                st.session_state.labeling_started = False
                st.session_state.selected_regions = []
                st.rerun()
        
        # 사용 가이드
        with st.expander("📖 사용 가이드"):
            st.markdown("""
            ### 영역 선택 방법:
            1. **좌표 입력**: 스펙트로그램에서 이상 패턴이 보이는 영역의 X, Y 좌표와 크기를 입력하세요
            2. **라벨 선택**: 해당 영역이 어떤 이상인지 선택하세요
            3. **영역 추가**: '영역 추가' 버튼을 클릭하여 여러 영역을 선택할 수 있습니다
            4. **저장**: 최종적으로 전체 이미지의 라벨을 선택하고 저장하세요
            
            ### 저장되는 데이터:
            - **이미지**: 라벨별 폴더에 복사됨
            - **좌표 데이터**: `annotations/` 폴더에 JSON 형식으로 저장됨
            - AI 모델 학습 시 이 좌표 데이터를 활용하여 정확한 영역 학습 가능
            """)


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='고급 스펙트로그램 라벨링 도구')
    parser.add_argument('--input-dir', default='data/spectrograms', 
                       help='라벨링할 스펙트로그램 이미지 디렉토리')
    
    args = parser.parse_args()
    
    labeling_tool = AdvancedLabelingTool()
    labeling_tool.run_labeling_interface(args.input_dir)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        main()
    else:
        # 세션 상태 초기화
        if 'labeling_started' not in st.session_state:
            st.session_state.labeling_started = False
        if 'input_directory' not in st.session_state:
            st.session_state.input_directory = "data/spectrograms"
        
        labeling_tool = AdvancedLabelingTool()
        
        st.set_page_config(
            page_title="고급 스펙트로그램 라벨링 도구",
            page_icon="🎨",
            layout="wide"
        )
        
        # 라벨링이 시작되지 않았거나 초기화면으로 돌아가야 하는 경우
        if not st.session_state.labeling_started:
            st.title("🎨 고급 스펙트로그램 전문가 라벨링 도구")
            
            input_dir = st.text_input(
                "라벨링할 스펙트로그램 이미지 디렉토리를 입력하세요:",
                value=st.session_state.input_directory,
                help="스펙트로그램 이미지 파일들이 있는 디렉토리 경로"
            )
            
            if st.button("라벨링 시작", type="primary"):
                if input_dir and os.path.exists(input_dir):
                    st.session_state.labeling_started = True
                    st.session_state.input_directory = input_dir
                    st.rerun()
                else:
                    st.error(f"디렉토리를 찾을 수 없습니다: {input_dir}")
        else:
            # 라벨링 인터페이스 실행
            labeling_tool.run_labeling_interface(st.session_state.input_directory)

