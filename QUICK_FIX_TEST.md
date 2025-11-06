# 빠른 테스트 수정 가이드

## 문제 1: seaborn 모듈 없음

### 해결 방법

**WSL 터미널에서 실행:**

```bash
source venv/bin/activate
pip install seaborn
```

또는:

```bash
bash scripts/fix_test_issues.sh
```

---

## 문제 2: MIMII 모델 특징 개수 불일치

**해결됨**: `ai/realtime_anomaly_detector_with_mimii.py` 파일을 수정하여 44개 특징을 추출하도록 변경했습니다.

---

## 테스트 재실행

```bash
source venv/bin/activate
python scripts/test_smart_detection_system.py
```

---

## 예상 결과

모든 테스트가 통과해야 합니다:

```
총 테스트: 11개
✅ 성공: 11개
❌ 실패: 0개
성공률: 100.0%

🎉 모든 테스트 통과!
```

