
# 🏭 SignalCraft Web Platform
### Intelligent Industrial Audio Analysis & Management System
**산업용 압축기 통합 관제 및 AI 데이터 라벨링 플랫폼**

![Project Status](https://img.shields.io/badge/Status-Stable_v1.0-00FF9D?style=for-the-badge)
![Backend](https://img.shields.io/badge/Node.js-Express-339933?style=for-the-badge&logo=node.js)
![AI Engine](https://img.shields.io/badge/Python-Flask_%26_PyTorch-3776AB?style=for-the-badge&logo=python)
![Database](https://img.shields.io/badge/Database-PostgreSQL-4169E1?style=for-the-badge&logo=postgresql)

---

## 📖 Overview


https://signalcraft.kr/

**SignalCraft Web**은 산업 현장의 수많은 압축기(Compressor)에서 수집된 소리 데이터를 통합 관리하고 분석하는 **중앙 관제 시스템(Command Center)**입니다.
단순한 모니터링을 넘어, 전문가가 직접 AI 학습용 데이터를 가공할 수 있는 **고도화된 라벨링 툴**을 내장하고 있으며, Node.js와 Python의 강력한 하이브리드 아키텍처를 기반으로 대규모 데이터를 안정적으로 처리합니다.

### 💡 Key Value
- **Centralized Control:** 모든 공장과 장비의 상태를 한곳에서 실시간 모니터링.
- **Expert-in-the-Loop:** 전문가가 시각화된 스펙트로그램을 보며 AI 진단 결과를 검증 및 수정.
- **Hybrid Performance:** Node.js의 빠른 I/O와 Python의 강력한 AI 연산 능력을 결합.

---

## ✨ Core Features

### 1. Unified Dashboard 📊
- **실시간 통합 관제:** 등록된 모든 IoT 센서의 상태(진동, 소음 레벨)를 실시간 차트로 시각화.
- **Industrial Cyberpunk UI:** 어두운 현장에서도 눈이 편안하고 직관적인 다크 모드 기반 디자인.

### 2. Pro AI Labeling Tool 🎧
- **Wavesurfer.js & Annotorious:** 웹 브라우저에서 스펙트로그램을 직접 보며 구간(Region)을 설정하고 라벨링.
- **스펙트로그램 시각화:** 오디오 파형(Waveform)과 주파수 스펙트럼을 동시에 분석하여 미세한 고장음 포착.
- **단축키 지원:** 전문가의 작업 속도를 극대화하기 위한 키보드 단축키 및 자동 저장 기능.

### 3. Asynchronous AI Analysis ⚡
- **Celery + Redis:** 대용량 오디오 분석 작업을 백그라운드 큐(Queue)로 처리하여 서버 지연(Blocking) 방지.
- **On-Demand Diagnosis:** 사용자가 원할 때 즉시 정밀 분석을 요청하고 결과 리포트 생성.

### 4. RBAC Security System 🔐
- **Role-Based Access Control:** 관리자(Admin), 전문가(Labeler), 일반 사용자(User)별 권한 분리.
- **Hybrid Auth:** Node.js가 인증을 전담하고, 검증된 요청만 Python AI 서버로 전달하는 보안 구조.

---

## 🏗️ System Architecture



## 🛠️ Tech Stack

| Category | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5, EJS, Jinja2 | Server-Side Rendering (SSR) |
| **Visualization** | Wavesurfer.js, Chart.js | Spectrogram & Real-time Charts |
| **Main Backend** | **Node.js (Express)** | User Auth, File Upload, WebSocket |
| **AI Backend** | **Python (Flask)** | AI API, Audio Processing (Librosa) |
| **Database** | **PostgreSQL** | Relational Data Storage (AWS RDS) |
| **Queue/Cache** | **Redis** | Task Queue & Session Store |
| **Process Mgt** | **PM2** | Process Keep-alive & Monitoring |
| **Infra** | AWS EC2, Nginx | Production Environment |

-----

## 🚀 Getting Started

이 프로젝트는 Node.js와 Python 환경이 모두 필요합니다.

### 1\. Prerequisites

  - Node.js (v18+)
  - Python (v3.10+)
  - PostgreSQL & Redis Server

### 2\. Installation

#### A. Node.js Setup (Main Server)

```bash
npm install
cp .env.example .env  # 환경변수 설정
node server.js
```

#### B. Python Setup (AI Engine)

```bash
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
python app.py
```

#### C. Worker Setup (Async Tasks)

```bash
# In separate terminal
celery -A celery_worker.celery_app worker --loglevel=info
```

### 3\. Environment Variables (.env)

```ini
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password

# JWT & Session
SESSION_SECRET=signalcraft_secret_key

# Redis
REDIS_URL=redis://localhost:6379/0
```

-----

## 📂 Project Structure

```
signalcraft-web/
├── server/             # Node.js Logic (Auth, API)
├── ai/                 # Python Logic (Models, Analysis)
│   ├── models/         # Pre-trained Models (.pth, .pkl)
│   └── labeling/       # Labeling Tool Backend
├── web/                # Frontend Views
│   ├── static/         # CSS, JS, Images (Cyberpunk Theme)
│   └── templates/      # HTML Templates (Labeling Tool)
├── routes/             # Express & Flask Routes
├── config/             # DB & System Config
└── ecosystem.config.js # PM2 Deployment Config
```

-----

## 🔗 Related Repositories

  - **[SignalCraft Mobile App](https://github.com/kimjuyoung1127/signalcraftapp)** : 현장 관리자용 모바일 앱 (React Native)

-----

## 📞 Contact

  - **Project Lead:** [Your Name]
  - **Email:** [Your Email]




```



