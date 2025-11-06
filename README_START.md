# 시스템 1 실행 가이드

## 현재 상황

`data/spectrograms` 디렉토리가 비어있습니다. 테스트용 스펙트로그램을 생성해야 합니다.

---

## 해결 방법

### 방법 1: 간단한 테스트 이미지 생성 (권장)

**WSL 터미널에서 실행:**

```bash
# 가상환경 활성화 (이미 했다면 생략)
source venv/bin/activate

# 테스트용 스펙트로그램 생성
python scripts/create_dummy_spectrograms_simple.py
```

이 명령어는 10개의 테스트용 스펙트로그램 이미지를 생성합니다.

### 방법 2: 기존 오디오 파일에서 생성

```bash
# 가상환경 활성화
source venv/bin/activate

# 오디오 파일에서 스펙트로그램 생성
python scripts/generate_test_spectrograms.py
```

---

## Streamlit 실행

테스트 이미지 생성 후:

1. **Streamlit 실행** (이미 실행 중이라면 새로고침):
   ```bash
   streamlit run ai/advanced_labeling_tool.py
   ```

2. **브라우저에서 접속**:
   - URL: `http://localhost:8501`

3. **디렉토리 경로 입력**:
   - `data/spectrograms` 입력

4. **"라벨링 시작" 버튼 클릭**

---

## 디렉토리 구조 확인

```bash
# 스펙트로그램 디렉토리 확인
ls data/spectrograms/

# 파일이 있어야 합니다:
# test_spectrogram_001.png
# test_spectrogram_002.png
# ...
```

---

## 문제 해결

### 스크립트 실행 오류

```bash
# Python 버전 확인
python --version

# 가상환경 활성화 확인
which python
# 출력: /root/smartcompressor-ai-system/venv/bin/python

# 필요한 패키지 확인
python -c "import numpy, matplotlib; print('OK')"
```

### 파일이 생성되지 않음

```bash
# 디렉토리 권한 확인
ls -la data/

# 수동으로 디렉토리 생성
mkdir -p data/spectrograms
```

---

## 다음 단계

1. ✅ 테스트 스펙트로그램 생성
2. ✅ Streamlit 실행
3. ✅ 라벨링 도구 사용 시작

