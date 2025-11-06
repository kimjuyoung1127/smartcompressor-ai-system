# SignalCraft Gunicorn 도입 설계 플랜 (v3 - 최종안)

## 1. 개요 및 목표
이 문서는 **GitHub Actions 워크플로우(`auto-deploy.yml`) 분석**을 통해 확인된 사실, 즉 **"Python 서버가 관리되지 않는 백그라운드 프로세스로 실행되고 있음"**을 해결하기 위한 최종 Gunicorn 도입 계획을 정의합니다.

**현황 진단:**
- Node.js 서버는 `ecosystem.config.js`를 통해 PM2로 안정적으로 관리되고 있습니다.
- Python 서버는 배포 시 `pkill`로 종료된 후, 단순 백그라운드 프로세스(`&`)로 실행되어 **자동 복구, 로그 관리, 상태 모니터링이 불가능한 매우 불안정한 상태**입니다.

**최종 목표:**
- 불안정한 Python 프로세스를 **PM2를 통해 Gunicorn으로 실행**하도록 전환합니다.
- Node.js와 Python 프로세스를 **하나의 `ecosystem.config.js` 파일로 통합 관리**하여, 프로세스 관리의 일관성과 안정성을 확보합니다.

---

## 2. 단계별 실행 계획

### 1단계: Gunicorn 설치 및 의존성 관리
- **Action:**
    1.  프로젝트의 Python 가상 환경에 Gunicorn을 설치합니다.
        ```bash
        pip install gunicorn
        ```
    2.  설치된 Gunicorn 버전을 `requirements.txt`에 동기화합니다.
        ```bash
        pip freeze > requirements.txt
        ```
- **기대 결과:** `requirements.txt` 파일에 `gunicorn==x.x.x` 라인이 추가됩니다.

### 2단계: Gunicorn 실행 설정 파일 작성
- **Action:**
    1.  프로젝트 루트에 `gunicorn.conf.py` 파일을 생성합니다.
- **`gunicorn.conf.py`:**
    ```python
    # gunicorn.conf.py
    import multiprocessing

    # Nginx와 내부 통신을 위한 소켓 바인딩 (충돌 방지를 위해 8001 포트 사용)
    bind = "127.0.0.1:8001"

    # 워커(Worker) 프로세스 설정
    workers = multiprocessing.cpu_count() * 2 + 1
    worker_class = "sync"

    # 로그를 표준 출력으로 보내 PM2가 관리하도록 설정
    accesslog = "-"
    errorlog = "-"

    # 타임아웃 설정 (120초)
    timeout = 120

    # Gunicorn이 실행할 Flask 애플리케이션 지정
    # app.py 모듈의 create_app() 팩토리 함수를 호출
    wsgi_app = "app:create_app()"
    ```
- **기대 결과:** Gunicorn 실행 옵션을 중앙에서 관리할 수 있는 `gunicorn.conf.py` 파일이 생성됩니다.

### 3단계: PM2 설정 파일 (`ecosystem.config.js`) 통합
- **Action:**
    1.  `ecosystem.config.js` 파일을 열어, 기존 `signalcraft-nodejs` 설정에 **`signalcraft-python` 설정을 추가**합니다.
- **`ecosystem.config.js` (수정):**
    ```javascript
    module.exports = {
      apps: [
        {
          name: 'signalcraft-nodejs',
          script: 'server.js',
          // ... 기존 Node.js 설정 ...
          env_production: {
            NODE_ENV: 'production',
            PORT: 3000
          }
        },
        // --- Python 서버 설정 추가 ---
        {
          name: 'signalcraft-python',
          script: 'gunicorn',
          args: '-c gunicorn.conf.py',
          interpreter: '/home/ubuntu/smartcompressor_env/bin/python', // **중요: 가상환경의 Python 경로를 정확히 지정**
          exec_mode: 'fork',
          autorestart: true,
          watch: false,
          max_memory_restart: '512M',
          env_production: {
            // Python 앱에서 사용할 환경 변수 (필요시)
          }
        }
        // --- 추가 완료 ---
      ]
    };
    ```
- **기대 결과:** `pm2 start ecosystem.config.js` 명령 하나로 Node.js와 Python 서버를 모두 안정적으로 실행할 수 있게 됩니다.

### 4단계: Nginx 리버스 프록시 설정 확인
- **Action:**
    1.  Nginx 설정 파일에서 Python 백엔드로 요청을 전달하는 `proxy_pass`의 포트가 Gunicorn 포트(`8001`)와 일치하는지 확인합니다.
- **Nginx 설정 (확인):**
    ```nginx
    # ...
    location ~ ^/(api/ai|api/iot|api/lightweight-analyze|api/flask) {
        proxy_pass http://127.0.0.1:8001; # Gunicorn 포트와 일치하는지 확인
        # ...
    }
    # ...
    ```
- **기대 결과:** Nginx가 외부 요청을 Gunicorn 서버로 올바르게 전달합니다.

### 5단계: 배포 스크립트 (`auto-deploy.yml`) 수정
- **Action:**
    1.  `.github/workflows/auto-deploy.yml` 파일을 수정합니다.
    2.  불안정한 `pkill` 및 개별 실행 스크립트 호출 부분을 **`pm2 reload` 또는 `pm2 start` 명령으로 교체**합니다.
- **`auto-deploy.yml` (수정 부분):**
    ```yaml
    # ... (기존 서비스 완전 종료 섹션)
    - name: Deploy to EC2
      # ...
      script: |
        # ... (git pull, npm install 등)

        echo "🛑 기존 서비스 중지 및 재시작..."
        # --- 변경 시작 ---
        # 기존: pkill -f "python.*app.py" || true
        # 변경: PM2가 모든 것을 관리하므로 reload 명령 하나로 충분
        pm2 reload ecosystem.config.js --env production || pm2 start ecosystem.config.js --env production
        # --- 변경 완료 ---

        # ... (서버 시작 대기 및 상태 확인)
        echo "📊 PM2 프로세스 상태 확인..."
        pm2 status

        # ... (Nginx 재시작 등)
    ```
- **기대 결과:** 배포 과정이 단순화되고, 중단 없는 서비스(Zero-downtime) 재시작이 가능해지며, Python 서버가 안정적으로 PM2의 관리하에 놓이게 됩니다.
