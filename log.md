🚀 AI 작업 지시서 v2.0: 2D 오디오 스펙트로그램 라벨링 툴 구현 (전문가용)1. 당신의 임무 (Your Task)당신은 SignalCraft 프로젝트의 시니어 풀스택 엔지니어입니다. 당신의 임무는 'Phase 1'에서 구축된 인증 시스템(RBAC)을 기반으로, 전문가용 **'2D 오디오 스펙트로그램 라벨링 툴'**을 구현하는 것입니다.이 툴은 "가끔 쓰는 뷰어"가 아닌, **"라벨러가 매일 8시간 동안 사용하는 생산성 도구"**가 되어야 합니다. 따라서 속도, 정확성, 피로도 감소를 최우선으로 고려해야 합니다.최종 결과물은 **static/labeling/audio_spectrogram_labeling.html**과 static/js/labeling/audio_spectrogram_labeling.js 두 개의 파일로 생성되어야 합니다.2. 핵심 아키텍처 (The Architecture)이 툴은 **'오디오'**와 **'시각화'**가 완벽하게 동기화되어야 합니다.백엔드 (Python/Flask) 역할:GET /api/labeling/queue: 라벨링할 오디오 목록 반환 (DB 스키마 audio_files 참조)GET /api/audio/file/{id}: 원본 오디오 파일 반환GET /api/audio/spectrogram-image/{id}: (신규) librosa 또는 audiowaveform을 사용해 오디오의 **'스펙트로그램 PNG 이미지'**를 미리 생성하여 반환합니다. (이것이 2D 라벨링의 '배경'이 됩니다.)POST /api/labeling/save-label: 라벨링 결과를 DB labels 테이블에 저장합니다.프론트엔드 (HTML/JS) 역할:wavesurfer.js: 오디오 파형(Waveform) 렌더링 및 재생/정지/탐색/루핑 등 오디오 제어 전반을 담당합니다.Annotorious: 백엔드에서 받은 '스펙트로그램 이미지' 위에 2D 바운딩 박스를 그리고, 라벨을 달 수 있게 합니다.audio_spectrogram_labeling.js: wavesurfer.js의 재생 시간(timeupdate)과 Annotorious 뷰의 수직 커서를 동기화하는 '접착제' 역할을 합니다.3. UI/UX 레이아웃 (3단 구성)왼쪽 패널 (작업 큐):GET /api/labeling/queue로 받은 오디오 목록 (is_processed=false 필터)파일 클릭 시 중앙 패널에 로드.중앙 패널 (작업 공간):(상단) <img> 태그로 스펙트로그램 이미지를 표시. 이 <img>를 Annotorious가 초기화합니다.수직 커서 오버레이: <audio> 재생 시간에 맞춰 스펙트로그램과 파형 위를 움직이는 수직선 (<div>).(하단) wavesurfer.js가 렌더링하는 파형(Waveform) 및 타임라인.(최하단) HTML5 <audio> 컨트롤러 (재생속도, 볼륨 조절).오른쪽 패널 (라벨링 도구):라벨 선택: DB labels.label의 ENUM 값(normal, warning, critical, unknown) 버튼. (단축키 1, 2, 3, 4 표기)신뢰도: labels.confidence 저장을 위한 슬라이더 (기본값 자동 설정, 예: critical=90)메모: labels.notes 저장을 위한 textarea (최근 입력 자동 완성)액션 버튼: [저장], [되돌리기 (Undo)], [다시 실행 (Redo)]4. 필수 편의 기능 (전문가용 UX)아래 "최우선" 기능들은 반드시 구현되어야 합니다.키보드 단축키 (Hotkeys):Space: 재생/일시정지← / →: 0.1초 단위 탐색Shift + ← / →: 1초 단위 탐색L: wavesurfer.js Regions 플러그인으로 선택된 영역 반복 재생(Loop)Shift + ↑ / ↓: 재생 속도 조절자동 저장 (Autosave):라벨링 작업(박스 생성/수정)이 발생하면, 3초 뒤(debounce)에 localStorage에 임시 저장하여 브라우저가 종료되어도 작업물이 날아가지 않게 합니다.낙관적 UI (Optimistic UI):[저장] 버튼 클릭 시, API 응답을 기다리지 않고 **즉시 "저장 완료"**로 UI를 변경한 뒤, 백그라운드에서 API를 호출합니다. 만약 API 호출이 실패하면 "저장 실패" 토스트(Toast) 알림을 띄웁니다.프리페치 (Prefetch):현재 1번 파일을 작업 중일 때, 백그라운드에서 2번 파일의 오디오와 스펙트로그램 이미지를 미리 로드(preload)하여 작업 간 대기 시간을 0으로 만듭니다.정확도 향상 (Snapping & Guides):Annotorious가 생성하는 박스의 모서리가 타임라인의 시간 그리드(예: 100ms)에 "자석처럼" 붙도록(snap) 설정합니다.마우스 커서 위치에 따라 스펙트로그램과 파형 위에 **수직/수평 십자선(Crosshair)**을 표시하여 시간과 주파수(Frequency)를 쉽게 읽을 수 있도록 합니다.5. API 상호작용 (API Endpoints)audio_spectrogram_labeling.js가 호출해야 할 API 목록입니다.GET /api/labeling/queue: (인증 필요: requireLabeler)응답: [{ "id": 1, "file_name": "audio1.wav", "audio_url": "/api/audio/file/1", "spectrogram_url": "/api/audio/spectrogram-image/1", "peaks_url": "/api/audio/peaks/1", ... }, ...]POST /api/labeling/save-label: (인증 필요: requireLabeler)역할: 라벨링 결과를 labels 테이블에 저장합니다.백엔드 처리: 이 API는 req.session.user.id를 자동으로 가져와 labeler_user_id로 저장해야 합니다.요청(Body) (보고서 제안 반영):{
  "audio_file_id": 1,
  "label": "critical", // 가장 심각한 대표 라벨 1개
  "confidence": 92,
  "notes": "2차 하모닉 발생",
  "metadata": {
    "regions": [
      {"type":"region","start_time":10.5,"end_time":12.1,"label":"critical","confidence":92}
    ],
    "boxes": [
      {"type":"box", "time":{"start":10.8,"end":11.3},
       "freq":{"min":450,"max":1200},
       "label":"critical"}
    ],
    "ui_state":{"zoom":1.6,"playbackRate":0.8}
  }
}
