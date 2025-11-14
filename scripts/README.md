

# 📜 Scripts 디렉터리

이 디렉터리는 SignalCraft 시스템을 위한 다양한 유틸리티 및 배포 스크립트를 포함하고 있습니다.

## 🧭 개요
Scripts 디렉터리는 배포, 서버 관리, 데이터 처리, 시스템 유지보수 등 다양한 작업을 자동화하는 셸(Shell), 파워셸(PowerShell), 파이썬(Python) 스크립트를 포함합니다.

## 📄 파일 목록
- `auto_upload.js` - 자동 파일 업로드용 JavaScript 스크립트  
- `check-server-status.sh` - 서버 상태 확인용 셸 스크립트  
- `debug-502-error.sh` - 502 오류 디버깅용 셸 스크립트  
- `deploy-ec2-pm2.ps1` - EC2에 PM2로 배포하는 PowerShell 스크립트  
- `deploy-ec2-pm2.sh` - EC2에 PM2로 배포하는 셸 스크립트  
- `download_mimii.py` - MIMII 데이터셋 다운로드용 파이썬 스크립트  
- `fix-502-complete.sh` - 502 오류를 완전히 해결하는 셸 스크립트  
- `fix-502-error.sh` - 502 오류 수정용 셸 스크립트  
- `install_python_deps.py` - 파이썬 의존성 설치 스크립트  
- `migrate_to_postgres.py` - PostgreSQL로 마이그레이션하는 파이썬 스크립트  
- `pm2-restart.sh` - PM2 프로세스 재시작 스크립트  
- `pm2-setup.ps1` - PM2 설정용 PowerShell 스크립트  
- `pm2-setup.sh` - PM2 설정용 셸 스크립트  
- `pm2-start.ps1` - PM2 프로세스 시작용 PowerShell 스크립트  
- `pm2-start.sh` - PM2 프로세스 시작용 셸 스크립트  
- `pm2-stop.sh` - PM2 프로세스 중지용 셸 스크립트  
- `pm2-test.ps1` - PM2 설정 테스트용 PowerShell 스크립트  
- `pm2-test.sh` - PM2 설정 테스트용 셸 스크립트  
- `restart-server.sh` - 서버 재시작용 셸 스크립트  
- `setup-crontab.sh` - 크론 작업 설정용 셸 스크립트  
- `setup-pm2-autostart.sh` - PM2 자동 시작 설정용 셸 스크립트  
- `setup-pm2.sh` - PM2 설정용 셸 스크립트  
- `setup-systemd-service.sh` - systemd 서비스 설정용 셸 스크립트  
- `simple-deploy.sh` - 간단한 배포용 셸 스크립트  

## 🚀 배포 파이프라인 흐름
```
코드 준비 완료 → 배포 스크립트 실행 → 서버 프로비저닝 → 애플리케이션 배포 → 서비스 시작 → 상태 확인 → 모니터링
```

## 🎯 목적
이 디렉터리는 다음과 같은 자동화 작업을 지원합니다:
- 서버 배포 및 설정
- PM2를 통한 프로세스 관리
- 시스템 모니터링 및 진단
- 데이터 처리 작업
- 시스템 유지보수
- 오류 수정 절차

## 📂 스크립트 분류
- **배포 스크립트**: 애플리케이션을 서버에 배포
- **PM2 스크립트**: Node.js 프로세스를 PM2로 관리
- **서버 관리**: 서버 상태 확인 및 유지보수
- **데이터 스크립트**: 데이터셋 다운로드 및 처리
- **시스템 설정**: 시스템 서비스 및 크론 작업 설정

## 🔄 배포 워크플로우
```
개발 완료 → 빌드 결과물 생성 → 배포 스크립트 실행 → 서버 설정 → 애플리케이션 시작 → 서비스 검증
```

## ⚙️ 스크립트 실행 흐름
```
트리거 이벤트 → 스크립트 실행 → 작업 처리 → 로그 기록 → 상태 보고 → 정리 작업
```

## 🛠️ 시스템 관리 흐름
```
서버 모니터링 → 문제 감지 → 진단 스크립트 실행 → 문제 해결 → 상태 확인 → 알림 전송
```

-\