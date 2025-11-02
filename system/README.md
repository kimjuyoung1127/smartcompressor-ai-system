# system/ 디렉토리

이 디렉토리는 시스템 및 서비스 구성 파일을 포함합니다. 서버 운영 및 배포에 필요한 구성 파일들이 위치합니다.

## 포함된 파일

- `Dockerfile` - Docker 컨테이너 설정
- `docker-compose.yml` - Docker Compose 구성
- `nginx_https_config.conf`, `nginx_proxy_config.conf`, `nginx_signalcraft_config.conf`, `nginx_signalcraft_http.conf`, `signalcraft_nginx.conf` - Nginx 서버 구성 파일들
- `signalcraft-nodejs.service`, `signalcraft-python.service` - systemd 서비스 정의 파일

## 목적

이 디렉토리는 시스템 수준의 구성 파일들을 모아두어, 애플리케이션 코드와 시스템 설정을 분리 관리하기 위함입니다. 이는 배포, 운영 및 유지보수를 보다 효율적으로 하기 위한 조직화입니다.