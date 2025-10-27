# 🔧 WSL 파일 접근 오류 수정 가이드

## ❌ 잘못된 접근

### 문제
```
file://wls.localhost/ubuntu/root/smartcompressor-ai-system
```

**오류 원인**:
- ❌ `wls` → `wsl` (오타)
- ❌ `ubuntu` → `Ubuntu` (대소문자)
- ❌ `file://` 프로토콜은 네트워크 경로에 부적합

---

## ✅ 올바른 방법

### 방법 1: Windows 탐색기 (권장)

#### 올바른 경로
```
\\wsl.localhost\Ubuntu\root\smartcompressor-ai-system
```

#### 사용 방법
1. **Windows 탐색기** 열기 (Win + E)
2. **주소창**에 위 경로 입력
3. **Enter 키**

**주의**:
- `\\` (백슬래시 2개)로 시작
- `wsl` (소문자)
- `Ubuntu` (대문자 U)

---

### 방법 2: VS Code로 열기

#### 명령어
```powershell
code \\wsl.localhost\Ubuntu\root\smartcompressor-ai-system
```

#### 단계별
```powershell
# 1. PowerShell 열기
Win + X → Windows PowerShell

# 2. 명령어 실행
cd \\wsl.localhost\Ubuntu\root\smartcompressor-ai-system

# 3. VS Code로 열기
code .
```

---

### 방법 3: 파일 직접 열기

#### 파일 경로 (Windows 탐색기 주소창에 입력)
```
\\wsl.localhost\Ubuntu\root\smartcompressor-ai-system\기술자료_SmartCompressor_AI_시스템.md
```

#### 단계
1. Windows 탐색기 열기
2. 주소창에 위 경로 입력
3. Enter 키
4. 파일이 열립니다

---

## 🔍 경로 비교

### 잘못된 경로
```
file://wls.localhost/ubuntu/root/smartcompressor-ai-system
❌ wls → wsl (오타)
❌ ubuntu → Ubuntu (대소문자)
❌ file:// → \\ (네트워크 경로)
❌ / → \ (Windows 경로 구분자)
```

### 올바른 경로
```
\\wsl.localhost\Ubuntu\root\smartcompressor-ai-system
✅ wsl (소문자)
✅ Ubuntu (대문자 U)
✅ \\ (백슬래시 2개)
✅ \ (백슬래시)
```

---

## 📋 체크리스트

### 올바른 경로 사용
- ✅ `\\wsl.localhost\Ubuntu\...`
- ✅ Windows 탐색기 사용
- ✅ 파일 더블클릭으로 열기

### 피해야 할 것
- ❌ `file://` 사용
- ❌ `wls` (오타)
- ❌ `ubuntu` (소문자)
- ❌ `/` (슬래시)

---

## 🚀 빠른 해결책

### 지금 바로 하기

#### 1. Windows 탐색기 열기
```
Win + E
```

#### 2. 주소창에 입력
```
\\wsl.localhost\Ubuntu\root\smartcompressor-ai-system
```

#### 3. Enter 키

#### 4. .md 파일 확인
- 기술자료_SmartCompressor_AI_시스템.md
- 최종_진단_및_해결책.md
- 404_오류_해결_보고서.md
- 등등...

---

## 💡 추가 팁

### 북마크 추가
1. 위 경로로 접근 성공
2. 상단 **"즉시 액세스에 고정"** 클릭
3. 또는 즐겨찾기 추가

### 바로가기 만들기
1. 폴더 우클릭
2. **"바로가기 만들기"**
3. 데스크톱으로 드래그

---

## ✅ 최종 확인

### 성공 시 표시
- Windows 탐색기에서 `.md` 파일 목록이 보임
- 파일 더블클릭하면 열림
- VS Code로도 열 수 있음

### 실패 시
- 경로 확인: `wsl` vs `wls`
- 대소문자 확인: `Ubuntu` vs `ubuntu`
- 백슬래시 확인: `\\wsl.localhost\...`

---

**올바른 경로**: `\\wsl.localhost\Ubuntu\root\smartcompressor-ai-system`

**사용**: Windows 탐색기 주소창에 입력!

