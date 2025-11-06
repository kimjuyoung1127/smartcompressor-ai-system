# 빠른 시작 가이드 (수정 버전)

## ⚠️ 현재 위치 확인

사용자가 홈 디렉토리(`~`)에서 실행하고 있습니다.
프로젝트 디렉토리로 먼저 이동해야 합니다!

---

## 🚀 올바른 실행 방법

### 1단계: 프로젝트 디렉토리로 이동

```bash
cd /root/smartcompressor-ai-system
# 또는
cd ~/smartcompressor-ai-system
```

### 2단계: 현재 위치 확인

```bash
pwd
# 출력: /root/smartcompressor-ai-system

ls ai/advanced_labeling_tool.py
# 파일이 보여야 합니다
```

### 3단계: 가상환경 활성화 (이미 만들었다면)

```bash
source venv/bin/activate
```

프롬프트에 `(venv)` 표시 확인!

### 4단계: 실행

```bash
streamlit run ai/advanced_labeling_tool.py
```

---

## 📁 전체 경로로 확인

파일이 있는지 확인:
```bash
ls -la /root/smartcompressor-ai-system/ai/advanced_labeling_tool.py
```

---

## 💡 작업 디렉토리 확인 방법

```bash
# 현재 위치 확인
pwd

# 프로젝트 디렉토리인지 확인
ls ai/advanced_labeling_tool.py
```

파일이 없다면 프로젝트 디렉토리가 아닙니다!

