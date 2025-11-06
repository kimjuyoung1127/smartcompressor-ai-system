
---

# 🗂️ Static 디렉터리

이 디렉터리는 SignalCraft 웹 애플리케이션에서 사용하는 모든 정적 자산(static assets)을 포함하고 있습니다.

## 🧭 개요
Static 디렉터리는 브라우저에 직접 제공되는 클라이언트 측 자산을 포함하며, 여기에는 CSS 스타일시트, JavaScript 파일, 이미지, 기타 웹 인터페이스에 필요한 정적 리소스들이 포함됩니다.

## 📁 디렉터리 구조
- `admin/` - 관리자 인터페이스용 정적 자산  
- `css/` - 스타일링을 위한 CSS 파일  
- `dashboard-components/` - 대시보드 인터페이스 구성 요소  
- `images/` - 이미지 자산 (아이콘, 로고 등)  
- `js/` - 클라이언트 측 기능을 위한 JavaScript 파일  
- `landing-components/` - 랜딩 페이지 구성 요소  
- `pages/` - 정적 HTML 페이지 템플릿  
- `videos/` - 비디오 자산  

### 루트 파일
- `.env` - 환경 설정 파일  
- `app.js` - 메인 클라이언트 애플리케이션 파일  
- `app.js.backup`, `app_backup.js` - 백업용 애플리케이션 파일  
- `data_upload_interface.html` - 데이터 업로드 인터페이스  
- `favicon.ico` - 웹사이트 파비콘  
- `field_data_collection.html` - 현장 데이터 수집 인터페이스  
- `high_quality_labeling_tool.html` - 고품질 라벨링 도구  
- `integrated_interface.html` - 통합 시스템 인터페이스  
- `intelligent_labeling_interface.html` - 지능형 라벨링 인터페이스  
- `manifest.json` - PWA 기능을 위한 매니페스트 파일  
- `real_sound_labeling_tool.html` - 실제 사운드 라벨링 도구  
- `sound_data_manager.html` - 사운드 데이터 관리 인터페이스  
- `sound_labeling_tool.html` - 사운드 라벨링 도구  
- `styles.css` - 메인 CSS 스타일시트

## 🎨 UI 컴포넌트 흐름
```
정적 자산(CSS, JS, 이미지) → 브라우저 → UI 렌더링 → 사용자 상호작용 → API 통신 → 동적 업데이트
```

## 🎯 목적
이 디렉터리는 다음과 같은 정적 파일을 제공합니다:
- 클라이언트가 직접 접근 가능한 자산
- 스타일링 및 클라이언트 측 기능 구현에 사용
- 애플리케이션 UI 구성에 필수적인 요소
- 퍼블릭 및 관리자 인터페이스 모두에 필요

## 📦 자산 유형
- **CSS 파일**: 애플리케이션의 다양한 부분에 대한 스타일 정의  
- **JavaScript 파일**: 클라이언트 측 로직 및 상호작용 처리  
- **이미지**: 아이콘, 로고, 스크린샷 등 시각적 자산  
- **HTML 파일**: 정적 페이지 및 UI 인터페이스 구성 요소  
- **설정 파일**: 매니페스트 및 환경 설정 파일

## 🧱 UI 컴포넌트 아키텍처
```
컴포넌트 요청 → 정적 서버 → 자산 전달 → 브라우저 렌더링 → 사용자 상호작용 → 동적 업데이트
```

## 🧩 인터페이스 분류

### 🛠️ 관리자 인터페이스
```
관리자 요청 → 관리자 자산 → 대시보드 UI → 관리자 기능 → 데이터 관리
```

### 👤 사용자 인터페이스
```
사용자 요청 → 정적 자산 → 메인 UI → 오디오 분석 → 결과 표시
```

### 🏷️ 라벨링 도구
```
라벨링 요청 → 도구 자산 → 인터페이스 → 오디오 라벨링 → 결과 제출
```

