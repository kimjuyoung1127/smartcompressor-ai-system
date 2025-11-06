# 🔑 김주영님 SSH 키 교체 안내

## 작업 내용

1. ✅ 기존 SSH 공개키 제거 (juyoung@signalcraft로 끝나는 모든 키)
2. ✅ 새로운 SSH 공개키 추가
3. ✅ 키 등록 확인

## 실행 방법

### WSL 터미널에서 실행

```bash
cd ~/smartcompressor-ai-system
chmod +x update_juyoung_ssh_key.sh

# 키 파일 경로를 지정하거나 자동 감지
./update_juyoung_ssh_key.sh
# 또는
./update_juyoung_ssh_key.sh "/mnt/c/Signal_craft/음원라벨링도구/compressor-ai-diagnosis/src/signalcraft-new.pem"
```

## 변경되는 키

### 제거되는 키 (기존)
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCpAVjMIt8W7WZg8jhhu7xFqyMIZImoPqjA6L7LcVZJYCT1VA/JEg3U9jbbp5yh1ake8+/nrdJiATkP... juyoung@signalcraft
```

### 추가되는 키 (새로운)
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC2UdrEkhWjRmvJA4qykSMSq2J5/rhNml+g0PzrGWf9xLPzO5ykyKA8yj9KHwNIOMLNvaGuBgMT659/hZiIYysBHFHZ9bXn8uFz6oW7Z3Mo4ZSsTISpz6gjUerg4EaXwO9BljvcZiNf1Orcy7xZBq2bCFjwKczDBurewhy+1vazGRs3glyzxU2Dv8Mg8WEUbGKdVmPjVLImsFffMP9+kceDug5D1GL7MHt5MRlBcxofbSPsa+0YUtDaIgjzd49V8wMqCjND4vG44zSRO75Swfcgvc8yvM8uloWE73e4+bQrjER/wJE19RswMOLmn9HWUG8uI6eJNYEtAchmI/QH2K+tp3w8EJcqXlaYhyMIgOKk06UyJatO6adJjXz2lbACyIgG7DQL2fDSM754xa6BYaaWxzWkRyhmdJIsyX9jmj2hyLaBLuvc7xDc25zbv3C1q99Mp+IInhsHTyJ7W7+myvyLYEtAH5VPRHGm6axniKJgVfXQVWHvw4/2vHjbrASalrzxYlCAKPlu1ph0mm/yS372jcVt4O5vzsQzJj4Bjs1FLveQJkWQsSBhcQmU8lEi5UB6L4VB/+PS2F0QmBjDpkdIQHOj+Hwk3n1CqDB4b2m2J3pUm36GheIhkEi7Uzl16/pS4Kpg1ZWX2PQ9nkJo8WYnKCETXHQL7LmowFy51XqS9w== juyoung@signalcraft
```

## 주의사항

⚠️ **기존 키는 즉시 제거됩니다.** 새 키가 정상적으로 등록되기 전까지는 SSH 접속이 불가능할 수 있습니다.

✅ 스크립트는 백업을 생성하므로 문제 발생 시 복구 가능합니다.

## 확인 방법

교체 완료 후:

```bash
ssh ubuntu@3.39.124.0
```

새 키로 접속이 성공하면 교체가 완료된 것입니다.

