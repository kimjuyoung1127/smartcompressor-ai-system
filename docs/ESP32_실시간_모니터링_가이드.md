# ESP32 실시간 모니터링 가이드

## 개요

ESP32에서 실시간으로 소리 데이터를 전송하여 자동 판단하는 시스템입니다.

---

## 판단 기준

### 1. 소리 입력 유무 판단
- **35~40 dB**: 소리 입력 없음 (No Input)
  - 알고리즘 판단 수행하지 않음
  - 상태: `no_input`

### 2. 판단 시작 임계값
- **40~48 dB**: 판단 임계값 미달
  - 알고리즘 판단 수행하지 않음
  - 상태: `below_threshold`

### 3. 알고리즘 판단
- **48 dB 이상**: 알고리즘 판단 시작
  - 실시간 고장 판단 수행
  - 상태: `auto` (자동 판단) 또는 `pending` (보류)

---

## API 사용

### POST /api/esp32/realtime/detect

ESP32에서 실시간 판단 요청

**Request:**
```json
{
  "audio_data": [0.1, 0.2, 0.3, ...],
  "decibel_level": 55.0,
  "device_id": "ESP32_001",
  "sample_rate": 16000,
  "metadata": {
    "temperature": 25.5,
    "humidity": 60.0
  }
}
```

**Response (소리 입력 없음):**
```json
{
  "success": true,
  "status": "no_input",
  "decibel_level": 37.5,
  "result": null,
  "message": "소리 입력 없음 (37.5 dB)",
  "timestamp": "2024-01-01T12:00:00"
}
```

**Response (자동 판단):**
```json
{
  "success": true,
  "status": "auto",
  "decibel_level": 55.0,
  "result": {
    "decision": "auto",
    "result": {
      "is_failure": false,
      "confidence": 0.92
    },
    "confidence": 0.92
  },
  "message": "자동 판단: 정상 (신뢰도: 92.0%)",
  "timestamp": "2024-01-01T12:00:00"
}
```

**Response (보류):**
```json
{
  "success": true,
  "status": "pending",
  "decibel_level": 55.0,
  "result": {
    "decision": "pending",
    "pending_item_id": "pending_000001_1234567890",
    "confidence": 0.65
  },
  "message": "보류 큐 추가: 신뢰도 65.0%",
  "timestamp": "2024-01-01T12:00:00"
}
```

---

## ESP32 연동 코드 예시

### Arduino/ESP32 코드

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";
const char* serverUrl = "http://your-server:5000/api/esp32/realtime/detect";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("WiFi 연결 중...");
  }
  
  Serial.println("WiFi 연결 완료");
}

void loop() {
  // 오디오 데이터 수집 (예: 2초 @ 16kHz = 32000 샘플)
  float audioData[32000];
  float decibelLevel = readDecibelLevel();  // 데시벨 레벨 읽기
  
  // 오디오 데이터 수집
  for (int i = 0; i < 32000; i++) {
    audioData[i] = readAudioSample();
    delayMicroseconds(62);  // 16kHz 샘플링
  }
  
  // 서버로 전송
  sendToServer(audioData, 32000, decibelLevel);
  
  delay(1000);  // 1초마다 전송
}

void sendToServer(float* audioData, int length, float decibel) {
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  
  // JSON 생성
  DynamicJsonDocument doc(102400);  // 충분한 크기
  doc["device_id"] = "ESP32_001";
  doc["decibel_level"] = decibel;
  doc["sample_rate"] = 16000;
  
  JsonArray audioArray = doc["audio_data"].to<JsonArray>();
  for (int i = 0; i < length; i++) {
    audioArray.add(audioData[i]);
  }
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // POST 요청
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("응답: " + response);
    
    // JSON 파싱
    DynamicJsonDocument responseDoc(2048);
    deserializeJson(responseDoc, response);
    
    String status = responseDoc["status"];
    String message = responseDoc["message"];
    
    Serial.println("상태: " + status);
    Serial.println("메시지: " + message);
    
    // 상태에 따른 처리
    if (status == "auto") {
      bool isFailure = responseDoc["result"]["result"]["is_failure"];
      if (isFailure) {
        Serial.println("⚠️ 고장 감지!");
        // 알림 처리
      }
    } else if (status == "pending") {
      Serial.println("📋 보류 큐 추가됨");
    }
  } else {
    Serial.println("오류: " + String(httpResponseCode));
  }
  
  http.end();
}

float readDecibelLevel() {
  // 실제 데시벨 센서에서 읽기
  // 예: I2S 마이크 또는 ADC
  return analogRead(A0) * 0.1;  // 예시
}

float readAudioSample() {
  // 실제 오디오 샘플 읽기
  // 예: I2S 마이크
  return analogRead(A0) / 1024.0 - 0.5;  // -0.5 ~ 0.5 범위
}
```

---

## 대시보드 접속

```
http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html
```

---

## 판단 흐름

```
[ESP32 데이터]
    ↓
[데시벨 레벨 확인]
    ├─ 35~40 dB → ✅ 소리 입력 없음 (No Input)
    ├─ 40~48 dB → ⏸️ 판단 임계값 미달
    └─ 48 dB 이상 → 🔍 알고리즘 판단 시작
                        ├─ 신뢰도 ≥ 70% → ✅ 자동 판단
                        └─ 신뢰도 < 70% → 📋 보류 큐 추가
```

---

## 설정 조정

### 임계값 변경

```python
from services.esp32_realtime_detector import ESP32RealtimeDetector

detector = ESP32RealtimeDetector(
    no_input_threshold=(35, 40),      # 소리 없음 범위
    detection_start_threshold=48.0,   # 판단 시작 임계값
    confidence_threshold=0.7          # 보류 임계값
)
```

---

## 통계 조회

### GET /api/esp32/realtime/statistics

```bash
curl http://localhost:5000/api/esp32/realtime/statistics
```

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_detections": 100,
    "auto_count": 85,
    "pending_count": 10,
    "failure_count": 5,
    "auto_rate": 0.85,
    "pending_rate": 0.10,
    "failure_rate": 0.05
  }
}
```

---

## 디바이스 상태 조회

### GET /api/esp32/realtime/status/<device_id>

```bash
curl http://localhost:5000/api/esp32/realtime/status/ESP32_001
```

**Response:**
```json
{
  "success": true,
  "status": {
    "device_id": "ESP32_001",
    "status": "auto",
    "last_detection": "2024-01-01T12:00:00",
    "total_detections": 50,
    "recent_status": "auto",
    "recent_confidence": 0.92,
    "recent_is_failure": false
  }
}
```

---

## 다음 단계

1. ✅ ESP32 실시간 판단 시스템 구현 완료
2. ✅ 대시보드 UI 구현 완료
3. 🔄 ESP32 하드웨어 연동
4. 📊 실제 데이터로 테스트

