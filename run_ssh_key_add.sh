#!/bin/bash
# 김주영님 SSH 키 추가 - 간단 실행 스크립트

cd ~/smartcompressor-ai-system

# 실행 권한 부여
chmod +x quick_add_ssh_key.sh

# SSH 키 추가 스크립트 실행
./quick_add_ssh_key.sh "/mnt/c/Signal_craft/음원라벨링도구/compressor-ai-diagnosis/src/signalcraft-new.pem"

