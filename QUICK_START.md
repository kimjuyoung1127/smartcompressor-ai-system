# 빠른 시작 가이드

## ⚠️ 오류 해결: externally-managed-environment

Python 3.12+ 시스템에서는 가상환경을 사용해야 합니다.

---

## 🚀 3단계로 시작하기

### 1단계: 가상환경 생성

```bash
cd /root/smartcompressor-ai-system
python3 -m venv venv
```

만약 오류가 나면:
```bash
sudo apt update
sudo apt install python3-venv python3-full
```

### 2단계: 가상환경 활성화

```bash
source venv/bin/activate
```

프롬프트 앞에 `(venv)`가 표시되면 성공!

### 3단계: 패키지 설치

```bash
pip install streamlit>=1.28.0 Pillow>=10.0.0 pandas numpy matplotlib scipy scikit-learn
```

---

## 🎯 실행하기

가상환경이 활성화된 상태(`(venv)` 표시)에서:

```bash
# 시스템 1 실행
streamlit run ai/advanced_labeling_tool.py

# 또는 시스템 2 데모
python scripts/run_system1_system2_demo.py
```

---

## 📝 자동 설치 스크립트 사용

```bash
bash scripts/quick_setup.sh
```

또는

```bash
bash scripts/install_system1_system2.sh
```

---

## 💡 매번 작업할 때

**새 터미널 창을 열 때마다:**
```bash
cd /root/smartcompressor-ai-system
source venv/bin/activate
```

프롬프트에 `(venv)`가 보이면 준비 완료!

---

## ❓ 문제 해결

### 가상환경이 활성화되지 않음
```bash
# 경로 확인
pwd
# 출력: /root/smartcompressor-ai-system

# 가상환경 확인
ls -la venv/
```

### 패키지를 찾을 수 없음
```bash
# 가상환경이 활성화되었는지 확인
which python
# 출력: /root/smartcompressor-ai-system/venv/bin/python

# 다시 활성화
source venv/bin/activate
```

