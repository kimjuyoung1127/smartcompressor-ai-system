#include <Arduino.h>
#include <driver/i2s.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <esp_wifi.h>
#include <esp_sleep.h>

// ====== 설정 ======
#define SAMPLE_RATE 16000  // 샘플레이트 (AI 분석 표준 16kHz)
#define WINDOW_MS 500      // 윈도우 크기
#define BUFFER_SIZE 1024   // 버퍼 크기 (16kHz 최적화)
#define ANALYSIS_MS 10000  // 10초마다 분석
#define UPLOAD_MS 15000    // 15초마다 업로드
#define HEARTBEAT_MS 30000 // 30초마다 하트비트 전송
#define MAX_RETRY_COUNT 5  // 최대 재시도 횟수
#define RETRY_DELAY_MS 5000 // 재시도 간격

// ICS-43434 마이크 설정 (작동하는 핀 매핑)
#define I2S_WS_PIN 25      // Word Select (LR Clock)
#define I2S_BCK_PIN 27     // Bit Clock  
#define I2S_DATA_PIN 26    // Data

// 핀 설정
#define BOOT_BUTTON 0
#define LED_PIN 2
#define STATUS_LED 4

// WiFi 설정 (부평점)
const char* ssid = "U+NetDD5C";
const char* password = "4@HA2070A7";
const char* serverURL = "http://3.39.124.0:3000/api/esp32/features";
const char* heartbeatURL = "http://3.39.124.0:3000/api/esp32/heartbeat";
const char* statusURL = "http://3.39.124.0:3000/api/esp32/status";

// ====== 센서 설정 (부평점) ======
#define SENSOR_NUMBER "002"           // 부평점 센서 번호
#define STORE_TYPE "ice_cream_24h"    // 가게 유형
#define LOCATION "bupyeong_branch"    // 부평점 위치

// 오디오 특징 구조체 (ICS-43434 마이크 전용)
struct AudioFeatures {
    uint32_t timestamp;
    
    // 오디오 센서 (ICS43434) - I2S
    float rms_energy;
    float spectral_centroid;
    float zero_crossing_rate;
    float decibel_level;
    
    // 압축기 상태 감지
    float compressor_state;
    float anomaly_score;
    float efficiency_score;
    
    // 기본 분류
    float sound_type;  // 0: 정적, 1: 압축기, 2: 팬, 3: 이상음, 4: 기타
    float intensity_level;  // 0-1 강도
};

// ====== 전역 변수 ======
int16_t audioBuffer[BUFFER_SIZE];  // 16-bit 데이터용 int16_t
bool wifiConnected = false;
bool uploadEnabled = true;
bool systemHealthy = true;

unsigned long lastUpload = 0;
unsigned long lastAnalysis = 0;
unsigned long lastHeartbeat = 0;
unsigned long lastStatusCheck = 0;
unsigned long systemStartTime = 0;
unsigned long lastSuccessfulUpload = 0;

String deviceID = "ICE_STORE_24H_" + String(SENSOR_NUMBER);

// 버튼 제어
bool lastButtonState = HIGH;
unsigned long lastButtonPress = 0;

// LED 상태 표시
unsigned long lastLEDBlink = 0;
bool ledState = false;

// 에러 카운터
int uploadErrorCount = 0;
int wifiErrorCount = 0;
int i2sErrorCount = 0;
int totalRestartCount = 0;

// 시스템 상태
struct SystemStatus {
    bool wifi_connected;
    bool i2s_working;
    bool server_reachable;
    unsigned long uptime;
    int error_count;
    String last_error;
    unsigned long last_successful_upload;
};

SystemStatus systemStatus;

// I2S 설정
const i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,  // 16000Hz (AI 분석 표준)
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = (i2s_comm_format_t)(I2S_COMM_FORMAT_I2S | I2S_COMM_FORMAT_I2S_MSB),
    .intr_alloc_flags = 0,
    .dma_buf_count = 32,
    .dma_buf_len = 1024,
    .use_apll = true,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
};

const i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_BCK_PIN,
    .ws_io_num = I2S_WS_PIN,
    .data_out_num = I2S_PIN_NO_CHANGE, 
    .data_in_num = I2S_DATA_PIN
};

// ====== 개선된 함수들 ======

void printSystemStatus() {
    Serial.println("=== SYSTEM STATUS ===");
    Serial.println("Device ID: " + deviceID);
    Serial.println("Uptime: " + String((millis() - systemStartTime) / 1000) + " seconds");
    Serial.println("WiFi Connected: " + String(wifiConnected ? "YES" : "NO"));
    Serial.println("Upload Enabled: " + String(uploadEnabled ? "YES" : "NO"));
    Serial.println("System Healthy: " + String(systemHealthy ? "YES" : "NO"));
    Serial.println("Upload Errors: " + String(uploadErrorCount));
    Serial.println("WiFi Errors: " + String(wifiErrorCount));
    Serial.println("I2S Errors: " + String(i2sErrorCount));
    Serial.println("Total Restarts: " + String(totalRestartCount));
    Serial.println("Last Successful Upload: " + String((millis() - lastSuccessfulUpload) / 1000) + " seconds ago");
    Serial.println("=====================");
}

void updateSystemStatus() {
    systemStatus.wifi_connected = wifiConnected;
    systemStatus.i2s_working = (i2sErrorCount < 10);
    systemStatus.server_reachable = (uploadErrorCount < 5);
    systemStatus.uptime = millis() - systemStartTime;
    systemStatus.error_count = uploadErrorCount + wifiErrorCount + i2sErrorCount;
    systemStatus.last_successful_upload = lastSuccessfulUpload;
}

bool connectWiFiWithRetry() {
    Serial.println("=== WiFi Connection with Retry ===");
    
    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);
    WiFi.persistent(true);
    WiFi.disconnect();
    delay(500);
    
    int attempts = 0;
    int maxAttempts = 10;
    
    while (WiFi.status() != WL_CONNECTED && attempts < maxAttempts) {
        Serial.println("WiFi 연결 시도 " + String(attempts + 1) + "/" + String(maxAttempts));
        
        WiFi.begin(ssid, password);
        
        int waitTime = 0;
        while (WiFi.status() != WL_CONNECTED && waitTime < 10000) {
            delay(500);
            waitTime += 500;
            Serial.print(".");
        }
        
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println();
            Serial.println("✅ WiFi 연결 성공!");
            Serial.println("IP Address: " + WiFi.localIP().toString());
            Serial.println("Signal Strength: " + String(WiFi.RSSI()) + " dBm");
            wifiConnected = true;
            wifiErrorCount = 0;
            return true;
        } else {
            Serial.println();
            Serial.println("❌ WiFi 연결 실패");
            wifiErrorCount++;
            attempts++;
            delay(2000);
        }
    }
    
    Serial.println("❌ WiFi 연결 최종 실패");
    wifiConnected = false;
    return false;
}

bool sendHeartbeat() {
    if (!wifiConnected) return false;
    
    HTTPClient http;
    http.begin(heartbeatURL);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Device-ID", deviceID);
    http.addHeader("X-Location", LOCATION);
    
    // 하트비트 데이터 생성
    DynamicJsonDocument doc(1024);
    doc["device_id"] = deviceID;
    doc["timestamp"] = millis();
    doc["uptime"] = millis() - systemStartTime;
    doc["wifi_connected"] = wifiConnected;
    doc["upload_enabled"] = uploadEnabled;
    doc["system_healthy"] = systemHealthy;
    doc["error_counts"] = JsonObject();
    doc["error_counts"]["upload"] = uploadErrorCount;
    doc["error_counts"]["wifi"] = wifiErrorCount;
    doc["error_counts"]["i2s"] = i2sErrorCount;
    doc["last_successful_upload"] = lastSuccessfulUpload;
    doc["free_heap"] = ESP.getFreeHeap();
    doc["cpu_freq"] = ESP.getCpuFreqMHz();
    
    String jsonString;
    serializeJson(doc, jsonString);
    
    int code = http.POST(jsonString);
    http.end();
    
    if (code > 0) {
        Serial.println("✅ 하트비트 전송 성공: " + String(code));
        return true;
    } else {
        Serial.println("❌ 하트비트 전송 실패: " + String(code));
        return false;
    }
}

bool uploadFeaturesWithRetry(AudioFeatures features) {
    if (!wifiConnected) {
        Serial.println("❌ WiFi 연결 없음 - 업로드 건너뛰기");
        return false;
    }
    
    String jsonString = createJSON(features);
    int retryCount = 0;
    
    while (retryCount < MAX_RETRY_COUNT) {
        HTTPClient http;
        http.begin(serverURL);
        http.addHeader("Content-Type", "application/json");
        http.addHeader("X-Device-ID", deviceID);
        http.addHeader("X-Store-Type", STORE_TYPE);
        http.addHeader("X-Location", LOCATION);
        http.setTimeout(10000); // 10초 타임아웃
        
        int code = http.POST(jsonString);
        String response = http.getString();
        http.end();
        
        if (code > 0 && code < 400) {
            Serial.println("✅ 데이터 업로드 성공: " + String(code));
            Serial.println("응답: " + response);
            uploadErrorCount = 0;
            lastSuccessfulUpload = millis();
            return true;
        } else {
            Serial.println("❌ 업로드 실패: " + String(code));
            Serial.println("응답: " + response);
            uploadErrorCount++;
            retryCount++;
            
            if (retryCount < MAX_RETRY_COUNT) {
                Serial.println("재시도 " + String(retryCount) + "/" + String(MAX_RETRY_COUNT) + " - " + String(RETRY_DELAY_MS) + "ms 대기");
                delay(RETRY_DELAY_MS);
            }
        }
    }
    
    Serial.println("❌ 최대 재시도 횟수 초과 - 업로드 실패");
    return false;
}

bool checkServerStatus() {
    if (!wifiConnected) return false;
    
    HTTPClient http;
    http.begin(statusURL);
    http.setTimeout(5000);
    
    int code = http.GET();
    http.end();
    
    if (code > 0 && code < 400) {
        Serial.println("✅ 서버 상태 확인 성공: " + String(code));
        return true;
    } else {
        Serial.println("❌ 서버 상태 확인 실패: " + String(code));
        return false;
    }
}

void performSystemHealthCheck() {
    Serial.println("=== 시스템 건강 상태 점검 ===");
    
    // WiFi 상태 확인
    bool wifiStatus = (WiFi.status() == WL_CONNECTED);
    if (!wifiStatus && wifiConnected) {
        Serial.println("⚠️ WiFi 연결 끊어짐 감지");
        wifiConnected = false;
        wifiErrorCount++;
    }
    
    // 서버 연결 확인
    bool serverStatus = checkServerStatus();
    
    // 시스템 상태 업데이트
    systemHealthy = wifiStatus && serverStatus && (uploadErrorCount < 10);
    
    // 에러가 너무 많으면 시스템 재시작 고려
    if (uploadErrorCount > 20 || wifiErrorCount > 10 || i2sErrorCount > 20) {
        Serial.println("⚠️ 에러가 너무 많음 - 시스템 재시작 고려");
        systemHealthy = false;
    }
    
    // 마지막 성공적인 업로드가 너무 오래 전이면 경고
    if (millis() - lastSuccessfulUpload > 300000) { // 5분
        Serial.println("⚠️ 마지막 업로드가 너무 오래 전: " + String((millis() - lastSuccessfulUpload) / 1000) + "초 전");
    }
    
    printSystemStatus();
}

void emergencyRestart() {
    Serial.println("🚨 긴급 재시작 실행");
    totalRestartCount++;
    
    // WiFi 재연결
    WiFi.disconnect();
    delay(1000);
    connectWiFiWithRetry();
    
    // I2S 재초기화
    i2s_stop(I2S_NUM_0);
    delay(100);
    i2s_driver_uninstall(I2S_NUM_0);
    delay(100);
    setupI2S();
    
    // 에러 카운터 리셋
    uploadErrorCount = 0;
    wifiErrorCount = 0;
    i2sErrorCount = 0;
    
    Serial.println("✅ 긴급 재시작 완료");
}

void checkRebootCommand() {
    if (!wifiConnected) return;
    
    HTTPClient http;
    String url = String(serverURL) + "/device/" + deviceID + "/reboot/check";
    http.begin(url);
    http.addHeader("X-Device-ID", deviceID);
    
    int code = http.GET();
    
    if (code == 200) {
        String response = http.getString();
        DynamicJsonDocument doc(1024);
        deserializeJson(doc, response);
        
        if (doc["should_reboot"]) {
            Serial.println("🚨 리부트 명령 수신 - 5초 후 재시작");
            delay(5000);
            ESP.restart();
        }
    }
    
    http.end();
}

void checkConfigCommand() {
    if (!wifiConnected) return;
    
    HTTPClient http;
    String url = String(serverURL) + "/device/" + deviceID + "/config";
    http.begin(url);
    http.addHeader("X-Device-ID", deviceID);
    
    int code = http.GET();
    
    if (code == 200) {
        String response = http.getString();
        DynamicJsonDocument doc(1024);
        deserializeJson(doc, response);
        
        if (doc["config"]) {
            JsonObject config = doc["config"];
            
            if (config.containsKey("upload_interval")) {
                UPLOAD_MS = config["upload_interval"].as<unsigned long>();
                Serial.println("📝 업로드 간격 변경: " + String(UPLOAD_MS) + "ms");
            }
            
            if (config.containsKey("heartbeat_interval")) {
                HEARTBEAT_MS = config["heartbeat_interval"].as<unsigned long>();
                Serial.println("📝 하트비트 간격 변경: " + String(HEARTBEAT_MS) + "ms");
            }
            
            if (config.containsKey("enabled")) {
                uploadEnabled = config["enabled"].as<bool>();
                Serial.println("📝 업로드 상태: " + String(uploadEnabled ? "ENABLED" : "DISABLED"));
            }
        }
    }
    
    http.end();
}

// 기존 함수들 (간소화)
void setupI2S() {
    Serial.println("=== I2S SETUP ===");
    
    pinMode(I2S_WS_PIN, OUTPUT);
    pinMode(I2S_BCK_PIN, OUTPUT);
    pinMode(I2S_DATA_PIN, INPUT);
    
    esp_err_t result = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 드라이버 설치 실패: " + String(result));
        i2sErrorCount++;
        return;
    }
    
    result = i2s_set_pin(I2S_NUM_0, &pin_config);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 핀 설정 실패: " + String(result));
        i2sErrorCount++;
        return;
    }
    
    i2s_zero_dma_buffer(I2S_NUM_0);
    result = i2s_start(I2S_NUM_0);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 시작 실패: " + String(result));
        i2sErrorCount++;
        return;
    }
    
    Serial.println("✅ I2S 설정 완료");
}

bool collectAudio() {
    size_t bytes_read = 0;
    esp_err_t result = i2s_read(I2S_NUM_0, audioBuffer, BUFFER_SIZE * sizeof(int16_t), &bytes_read, 1000);
    
    if (result != ESP_OK || bytes_read == 0) {
        i2sErrorCount++;
        return false;
    }
    
    // 간단한 오디오 데이터 검증
    int16_t max_val = -32768;
    int16_t min_val = 32767;
    int non_zero_count = 0;
    
    for (int i = 0; i < BUFFER_SIZE; i++) {
        if (audioBuffer[i] > max_val) max_val = audioBuffer[i];
        if (audioBuffer[i] < min_val) min_val = audioBuffer[i];
        if (audioBuffer[i] != 0) non_zero_count++;
    }
    
    bool has_sufficient_samples = non_zero_count > 10;
    bool has_dynamic_range = (max_val - min_val) > 10;
    
    return has_sufficient_samples && has_dynamic_range;
}

// 기존 계산 함수들 (간소화)
float calculateRMS(int16_t* buffer, int length) {
    long sum = 0;
    for (int i = 0; i < length; i++) {
        sum += (long)buffer[i] * buffer[i];
    }
    return sqrt((float)sum / length);
}

float calculateDecibel(float rms) {
    if (rms <= 0) return 0;
    return 20 * log10(rms);
}

float calculateZeroCrossingRate(int16_t* buffer, int length) {
    int crossings = 0;
    for (int i = 1; i < length; i++) {
        if ((buffer[i] >= 0) != (buffer[i-1] >= 0)) {
            crossings++;
        }
    }
    return (float)crossings / (length - 1);
}

float calculateSpectralCentroid(int16_t* buffer, int length) {
    float weighted_sum = 0.0f;
    float magnitude_sum = 0.0f;
    
    for (int i = 0; i < length; i++) {
        float magnitude = abs(buffer[i]);
        float frequency = (float)i * SAMPLE_RATE / length;
        weighted_sum += magnitude * frequency;
        magnitude_sum += magnitude;
    }
    
    return magnitude_sum > 0 ? weighted_sum / magnitude_sum : 0.0f;
}

bool detectCompressorState(float rms, float spectralCentroid, float zeroCrossingRate) {
    return (rms > 500.0f) && (spectralCentroid > 3000.0f && spectralCentroid < 8000.0f) && (zeroCrossingRate < 0.2f);
}

float calculateAnomalyScore(float rms, float spectralCentroid, float zeroCrossingRate, bool compressorState) {
    float anomaly = 0.0f;
    
    if (rms > 3000.0f) anomaly += 0.3f;
    if (spectralCentroid > 15000.0f) anomaly += 0.2f;
    if (zeroCrossingRate > 0.6f) anomaly += 0.2f;
    
    if (compressorState && rms < 200.0f) anomaly += 0.3f;
    if (!compressorState && rms > 1500.0f) anomaly += 0.3f;
    
    return (anomaly > 1.0f) ? 1.0f : anomaly;
}

float calculateEfficiencyScore(bool compressorState, float rms, float spectralCentroid) {
    if (!compressorState) return 1.0f;
    
    float efficiency = 1.0f;
    if (rms > 3000.0f) efficiency -= 0.2f;
    if (spectralCentroid > 12000.0f) efficiency -= 0.3f;
    
    return (efficiency < 0.0f) ? 0.0f : efficiency;
}

AudioFeatures extractAudioFeatures() {
    AudioFeatures features;
    features.timestamp = millis();
    
    if (collectAudio()) {
        // 실제 오디오 데이터 처리
        features.rms_energy = calculateRMS(audioBuffer, BUFFER_SIZE);
        features.spectral_centroid = calculateSpectralCentroid(audioBuffer, BUFFER_SIZE);
        features.zero_crossing_rate = calculateZeroCrossingRate(audioBuffer, BUFFER_SIZE);
        features.decibel_level = calculateDecibel(features.rms_energy);
        
        features.compressor_state = detectCompressorState(features.rms_energy, features.spectral_centroid, features.zero_crossing_rate) ? 1.0f : 0.0f;
        features.anomaly_score = calculateAnomalyScore(features.rms_energy, features.spectral_centroid, features.zero_crossing_rate, features.compressor_state > 0.5);
        features.efficiency_score = calculateEfficiencyScore(features.compressor_state > 0.5, features.rms_energy, features.spectral_centroid);
        
        features.sound_type = (features.rms_energy < 100.0f) ? 0.0f : 
                             (features.rms_energy > 1000.0f && features.spectral_centroid > 3000.0f && features.spectral_centroid < 8000.0f) ? 1.0f : 4.0f;
        features.intensity_level = (features.rms_energy < 50.0f) ? 0.0f : 
                                  (features.rms_energy > 5000.0f) ? 1.0f : (features.rms_energy - 50.0f) / 4950.0f;
        
        Serial.println("✅ 실제 오디오 데이터 처리 완료");
    } else {
        // 시뮬레이션 데이터
        unsigned long time = millis() / 1000;
        float time_factor = sin(time * 0.1) * 0.3 + 0.7;
        float noise_factor = (random(0, 100) / 100.0) * 0.2;
        
        features.rms_energy = 20.0 + (sin(time * 0.05) * 10.0) + noise_factor;
        features.spectral_centroid = 3000.0 + (sin(time * 0.03) * 2000.0) + (noise_factor * 1000.0);
        features.zero_crossing_rate = 0.1 + (sin(time * 0.04) * 0.05) + noise_factor * 0.02;
        features.decibel_level = calculateDecibel(features.rms_energy);
        
        features.compressor_state = (sin(time * 0.02) > 0.3) ? 1.0 : 0.0;
        features.anomaly_score = 0.1 + (sin(time * 0.19) * 0.1) + noise_factor * 0.05;
        features.efficiency_score = 0.8 + (sin(time * 0.21) * 0.2) + noise_factor * 0.1;
        
        features.sound_type = (int)(sin(time * 0.22) * 2.5 + 2.5) % 5;
        features.intensity_level = 0.5 + (sin(time * 0.23) * 0.4) + noise_factor * 0.1;
        
        Serial.println("⚠️ 시뮬레이션 데이터 사용");
    }
    
    return features;
}

String createJSON(AudioFeatures features) {
    DynamicJsonDocument doc(1024);
    doc["device_id"] = deviceID;
    doc["timestamp"] = features.timestamp;
    doc["sensor_number"] = SENSOR_NUMBER;
    doc["store_type"] = STORE_TYPE;
    doc["location"] = LOCATION;
    doc["rms_energy"] = features.rms_energy;
    doc["spectral_centroid"] = features.spectral_centroid;
    doc["zero_crossing_rate"] = features.zero_crossing_rate;
    doc["decibel_level"] = features.decibel_level;
    doc["compressor_state"] = features.compressor_state;
    doc["anomaly_score"] = features.anomaly_score;
    doc["efficiency_score"] = features.efficiency_score;
    doc["sound_type"] = features.sound_type;
    doc["intensity_level"] = features.intensity_level;
    
    String jsonString;
    serializeJson(doc, jsonString);
    return jsonString;
}

void updateLEDStatus() {
    unsigned long currentTime = millis();
    
    if (systemHealthy && wifiConnected && uploadEnabled) {
        // 시스템 정상: 빠른 깜빡임 (0.3초)
        if (currentTime - lastLEDBlink > 300) {
            ledState = !ledState;
            digitalWrite(LED_PIN, ledState);
            lastLEDBlink = currentTime;
        }
    } else if (wifiConnected && !uploadEnabled) {
        // WiFi 연결됨 + 업로드 비활성화: 중간 깜빡임 (1초)
        if (currentTime - lastLEDBlink > 1000) {
            ledState = !ledState;
            digitalWrite(LED_PIN, ledState);
            lastLEDBlink = currentTime;
        }
    } else if (!systemHealthy) {
        // 시스템 비정상: 느린 깜빡임 (2초)
        if (currentTime - lastLEDBlink > 2000) {
            ledState = !ledState;
            digitalWrite(LED_PIN, ledState);
            lastLEDBlink = currentTime;
        }
    } else {
        // WiFi 연결 안됨: 매우 느린 깜빡임 (3초)
        if (currentTime - lastLEDBlink > 3000) {
            ledState = !ledState;
            digitalWrite(LED_PIN, ledState);
            lastLEDBlink = currentTime;
        }
    }
}

void handleBootButton() {
    int currentButtonState = digitalRead(BOOT_BUTTON);
    
    if (currentButtonState == LOW && lastButtonState == HIGH) {
        lastButtonPress = millis();
    }
    
    if (currentButtonState == HIGH && lastButtonState == LOW) {
        unsigned long pressDuration = millis() - lastButtonPress;
        
        if (pressDuration >= 100 && pressDuration < 3000) {
            uploadEnabled = !uploadEnabled;
            Serial.println("=== Upload " + String(uploadEnabled ? "ENABLED" : "DISABLED") + " ===");
        } else if (pressDuration >= 3000 && pressDuration < 10000) {
            Serial.println("=== WiFi 재연결 ===");
            WiFi.disconnect();
            delay(1000);
            connectWiFiWithRetry();
        } else if (pressDuration >= 10000) {
            Serial.println("=== 긴급 재시작 ===");
            emergencyRestart();
        }
    }
    
    lastButtonState = currentButtonState;
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    systemStartTime = millis();
    lastSuccessfulUpload = millis();
    
    pinMode(BOOT_BUTTON, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);
    pinMode(STATUS_LED, OUTPUT);
    
    Serial.println("=== 24H Ice Cream Store Monitoring System v2.0 ===");
    Serial.println("📍 Location: BUPYEONG BRANCH");
    Serial.println("Device: " + deviceID);
    Serial.println("Store Type: " + String(STORE_TYPE));
    Serial.println("Enhanced stability and monitoring features");
    Serial.println("Auto-recovery and error handling enabled");
    
    setupI2S();
    connectWiFiWithRetry();
    
    Serial.println("=== System Ready ===");
    printSystemStatus();
}

void loop() {
    handleBootButton();
    updateLEDStatus();
    
    // 시스템 건강 상태 점검 (1분마다)
    static unsigned long lastHealthCheck = 0;
    if (millis() - lastHealthCheck > 60000) {
        lastHealthCheck = millis();
        performSystemHealthCheck();
    }
    
    // 하트비트 전송 (30초마다)
    if (millis() - lastHeartbeat >= HEARTBEAT_MS) {
        lastHeartbeat = millis();
        if (wifiConnected) {
            sendHeartbeat();
            checkRebootCommand(); // 리부트 명령 확인
            checkConfigCommand(); // 설정 변경 명령 확인
        }
    }
    
    // WiFi 상태 확인 및 재연결 (10초마다)
    static unsigned long lastWiFiCheck = 0;
    if (millis() - lastWiFiCheck > 10000) {
        lastWiFiCheck = millis();
        
        bool wasConnected = wifiConnected;
        wifiConnected = (WiFi.status() == WL_CONNECTED);
        
        if (!wifiConnected && wasConnected) {
            Serial.println("⚠️ WiFi 연결 끊어짐! 재연결 시도...");
            connectWiFiWithRetry();
        } else if (wifiConnected && !wasConnected) {
            Serial.println("✅ WiFi 재연결 성공!");
        }
    }
    
    // 오디오 수집 및 분석
    if (collectAudio()) {
        // 10초마다 특징 분석
        if (millis() - lastAnalysis >= ANALYSIS_MS) {
            lastAnalysis = millis();
            
            AudioFeatures features = extractAudioFeatures();
            
            Serial.println("=== AUDIO FEATURES ===");
            Serial.println("RMS: " + String(features.rms_energy, 2));
            Serial.println("Decibel: " + String(features.decibel_level, 1) + " dB");
            Serial.println("Compressor: " + String(features.compressor_state > 0.5 ? "ON" : "OFF"));
            Serial.println("Anomaly: " + String(features.anomaly_score, 3));
            
            // 15초마다 업로드
            if (uploadEnabled && millis() - lastUpload >= UPLOAD_MS) {
                lastUpload = millis();
                Serial.println("=== 데이터 업로드 시작 ===");
                bool success = uploadFeaturesWithRetry(features);
                if (success) {
                    Serial.println("✅ 데이터 업로드 성공");
                } else {
                    Serial.println("❌ 데이터 업로드 실패");
                }
                Serial.println("=== 데이터 업로드 완료 ===");
            }
        }
    }
    
    // 시스템이 비정상이면 긴급 재시작 고려
    if (!systemHealthy && millis() - lastSuccessfulUpload > 300000) { // 5분간 성공 없음
        Serial.println("🚨 시스템 비정상 상태 - 긴급 재시작 실행");
        emergencyRestart();
    }
    
    delay(100);
}
