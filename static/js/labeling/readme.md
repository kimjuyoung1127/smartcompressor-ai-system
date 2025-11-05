# Audio Spectrogram Labeling Tool

## 개요
Audio Spectrogram Labeling Tool은 전문가용 2D 오디오 스펙트로그램 라벨링 도구입니다. 이 도구는 SignalCraft 프로젝트 내에서 오디오 파일의 스펙트로그램 이미지를 분석하고 이상 징후를 라벨링하는 데 사용됩니다.

## 파일 구조
```
static/
├── labeling/
│   └── audio_spectrogram_labeling.html
├── js/
│   └── labeling/
│       ├── audio_spectrogram_labeling.js
│       └── readme.md (이 파일)
```

## 기능

### 1. 3단계 UI 레이아웃
- **왼쪽 패널 (작업 큐)**: 라벨링할 오디오 파일 목록 표시
- **중앙 패널 (작업 공간)**: 스펙트로그램 이미지와 오디오 파형 표시
- **오른쪽 패널 (라벨링 도구)**: 라벨 선택, 신뢰도 조절, 메모 입력, 액션 버튼

### 2. 오디오/시각화 동기화
- 오디오 파형과 스펙트로그램 이미지를 완벽하게 동기화
- 재생 시간에 따라 수직 커서가 양쪽에 실시간 표시

### 3. 라벨링 기능
- 4가지 라벨 지원: normal, warning, critical, unknown
- 바운딩 박스를 통한 2D 영역 라벨링
- 신뢰도 설정 (0-100% 슬라이더)
- 라벨링 메모 입력

### 4. 전문가용 편의 기능
- **키보드 단축키**:
  - Space: 재생/일시정지
  - ← / →: 0.1초 단위 탐색
  - Shift + ← / →: 1초 단위 탐색
  - L: 선택된 영역 반복 재생
  - Shift + ↑ / ↓: 재생 속도 조절
  - 1, 2, 3, 4: 라벨 선택

- **자동 저장**: 3초 후 활동이 없을 시 localStorage에 자동 저장
- **되돌리기/다시실행**: 라벨링 작업 취소/재실행 기능

## 기술 스택
- **Wavesurfer.js**: 오디오 파형 렌더링 및 제어
- **Annotorious**: 스펙트로그램 이미지 위에 2D 애너테이션
- **HTML5/CSS3/JavaScript**: 사용자 인터페이스
- **SignalCraft 대시보드 스타일**: 일관된 UI/UX 제공

## 사용법

1. 왼쪽 패널에서 라벨링할 오디오 파일 선택
2. 중앙 패널에서 오디오 재생 및 스펙트로그램 분석
3. 오른쪽 패널에서 라벨 선택 및 신뢰도 설정
4. 스펙트로그램 이미지 위에 클릭하여 영역 라벨링
5. 저장 버튼 클릭으로 라벨링 결과 저장

## API 연동 (구현 예정)
- `/api/labeling/queue`: 라벨링할 오디오 목록 반환
- `/api/audio/file/{id}`: 원본 오디오 파일 반환
- `/api/audio/spectrogram-image/{id}`: 스펙트로그램 이미지 반환
- `/api/labeling/save-label`: 라벨링 결과 저장

## 커스터마이징
UI 스타일은 SignalCraft 대시보드와 일관성을 유지하도록 설계되었습니다. 스타일 변경이 필요한 경우 `dashboard_v3.css` 파일을 수정하거나 해당 스타일 정의를 오버라이드 하세요.