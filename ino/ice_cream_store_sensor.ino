#include <Arduino.h>
#include <driver/i2s.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <time.h>

// ====== 설정 ======
#define SAMPLE_RATE 10000
#define WINDOW_MS 2000
#define UPLOAD_MS 10000  // 10초마다 업로드 (에너지 절약)
#define BUFFER_SIZE (SAMPLE_RATE * 2)  // 2초

// 핀 설정
#define BOOT_BUTTON 0
#define LED_PIN 2
#define STATUS_LED 4

// WiFi 설정 (현장에서 변경 필요)
const char* ssid = "U+Net98A4";
const char* password = "EF#AE96H86";
const char* serverURL = "http://3.39.124.0:3000/api/esp32/audio/upload";

// 운영 시간 설정 (24시간 형식)
const int OPEN_HOUR = 8;   // 오전 8시
const int CLOSE_HOUR = 22; // 오후 10시

// ====== 전역 변수 ======
int16_t audioBuffer[BUFFER_SIZE];
int bufferIndex = 0;
bool wifiConnected = false;
bool uploadEnabled = true;
bool isOperatingHours = true;
unsigned long lastUpload = 0;
unsigned long lastTimeCheck = 0;
String deviceID = "ICE_STORE_" + String(random(1000, 9999));

// 버튼 제어
bool lastButtonState = HIGH;
unsigned long lastButtonPress = 0;
int buttonPressCount = 0;

// 상태 표시
enum SystemState {
    NORMAL,      // 정상 작동
    WARNING,     // 주의 (소음 감지)
    ERROR,       // 오류 (WiFi 연결 실패)
    SLEEP        // 대기 모드 (영업시간 외)
};
SystemState currentState = NORMAL;

// I2S 설정
const i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = (i2s_comm_format_t)(I2S_COMM_FORMAT_I2S | I2S_COMM_FORMAT_I2S_MSB),
    .intr_alloc_flags = 0,
    .dma_buf_count = 8,
    .dma_buf_len = 256,
    .use_apll = true,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
};

const i2s_pin_config_t pin_config = {
    .bck_io_num = 27, .ws_io_num = 25, .data_out_num = I2S_PIN_NO_CHANGE, .data_in_num = 26
};

// ====== 함수들 ======
void setupI2S() {
    pinMode(26, INPUT); pinMode(25, OUTPUT); pinMode(27, OUTPUT);
    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pin_config);
    i2s_zero_dma_buffer(I2S_NUM_0);
    Serial.println("I2S ready");
}

void connectWiFi() {
    Serial.println("WiFi connecting...");
    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);
    WiFi.persistent(true);
    WiFi.disconnect();
    delay(100);
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(1000);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected! IP: " + WiFi.localIP().toString());
        wifiConnected = true;
        currentState = NORMAL;
    } else {
        Serial.println("\nWiFi failed!");
        wifiConnected = false;
        currentState = ERROR;
    }
}

float readdB() {
    const int N = (SAMPLE_RATE * WINDOW_MS) / 1000;
    static int16_t buf[2000];
    size_t bytes_read = 0;
    
    if (i2s_read(I2S_NUM_0, buf, N * sizeof(int16_t), &bytes_read, portMAX_DELAY) != ESP_OK) return NAN;
    
    int got = bytes_read / sizeof(int16_t);
    if (got <= 0) return NAN;
    
    // RMS 계산
    long sum = 0;
    for (int i = 0; i < got; i++) sum += buf[i];
    double mean = (double)sum / got;
    
    double sumsq = 0.0;
    for (int i = 0; i < got; i++) {
        double v = (double)buf[i] - mean;
        sumsq += v * v;
    }
    
    double rms = sqrt(sumsq / got);
    if (!(rms > 0.0) || isinf(rms) || isnan(rms)) return NAN;
    
    return 94.0 + 20.0 * log10(rms / 32767.0) - (-26.0) + (-3.0);
}

void collectAudio() {
    const int N = (SAMPLE_RATE * WINDOW_MS) / 1000;
    static int16_t buf[2000];
    size_t bytes_read = 0;
    
    if (i2s_read(I2S_NUM_0, buf, N * sizeof(int16_t), &bytes_read, portMAX_DELAY) == ESP_OK && bytes_read > 0) {
        int got = bytes_read / sizeof(int16_t);
        for (int i = 0; i < got && bufferIndex < BUFFER_SIZE; i++) {
            audioBuffer[bufferIndex++] = buf[i];
        }
        
        if (bufferIndex >= BUFFER_SIZE) {
            Serial.println("🎉 Audio ready!");
        }
    }
}

void uploadAudio() {
    if (!uploadEnabled || !wifiConnected) return;
    
    Serial.println("=== UPLOAD START ===");
    
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/octet-stream");
    http.addHeader("X-Device-ID", deviceID);
    http.addHeader("X-Timestamp", String(millis()));
    http.addHeader("X-Sample-Rate", String(SAMPLE_RATE));
    http.addHeader("X-Store-Type", "ice_cream");
    http.addHeader("X-Operating-Hours", String(isOperatingHours));
    
    int code = http.POST((uint8_t*)audioBuffer, BUFFER_SIZE * sizeof(int16_t));
    
    if (code > 0) {
        Serial.println("✅ SUCCESS: " + String(code));
        currentState = NORMAL;
    } else {
        Serial.println("❌ FAILED: " + String(code));
        currentState = ERROR;
    }
    
    http.end();
    Serial.println("=== UPLOAD END ===");
    
    bufferIndex = 0;
}

void checkOperatingHours() {
    // 현재 시간 확인 (NTP 서버 사용 권장)
    struct tm timeinfo;
    if (getLocalTime(&timeinfo)) {
        int currentHour = timeinfo.tm_hour;
        isOperatingHours = (currentHour >= OPEN_HOUR && currentHour < CLOSE_HOUR);
        
        if (!isOperatingHours && currentState != SLEEP) {
            Serial.println("🌙 영업시간 외 - 대기 모드");
            currentState = SLEEP;
        } else if (isOperatingHours && currentState == SLEEP) {
            Serial.println("🌅 영업시간 시작 - 모니터링 재개");
            currentState = NORMAL;
        }
    }
}

void handleBootButton() {
    bool currentButtonState = digitalRead(BOOT_BUTTON);
    
    if (currentButtonState == LOW && lastButtonState == HIGH) {
        lastButtonPress = millis();
        buttonPressCount++;
        Serial.println("버튼 눌림 - 카운트: " + String(buttonPressCount));
    }
    
    if (currentButtonState == HIGH && lastButtonState == LOW) {
        unsigned long pressDuration = millis() - lastButtonPress;
        
        if (pressDuration < 2000) {
            // 짧게 누르기: 업로드 토글
            uploadEnabled = !uploadEnabled;
            Serial.println("=== 업로드 " + String(uploadEnabled ? "활성화" : "비활성화") + " ===");
            
        } else if (pressDuration >= 3000) {
            // 길게 누르기: WiFi 재연결
            Serial.println("=== WiFi 재연결 중 ===");
            WiFi.disconnect();
            delay(1000);
            connectWiFi();
        }
        
        buttonPressCount = 0;
    }
    
    lastButtonState = currentButtonState;
}

void updateStatusLED() {
    switch (currentState) {
        case NORMAL:
            digitalWrite(LED_PIN, uploadEnabled ? HIGH : LOW);
            digitalWrite(STATUS_LED, LOW);
            break;
        case WARNING:
            digitalWrite(LED_PIN, HIGH);
            digitalWrite(STATUS_LED, HIGH);
            break;
        case ERROR:
            digitalWrite(LED_PIN, LOW);
            digitalWrite(STATUS_LED, HIGH);
            break;
        case SLEEP:
            digitalWrite(LED_PIN, LOW);
            digitalWrite(STATUS_LED, LOW);
            break;
    }
}

void analyzeSound(float dB) {
    if (isnan(dB)) return;
    
    // 아이스크림 가게 특화 분석
    if (dB > 60) {
        currentState = WARNING;
        Serial.println("⚠️ 주의: 높은 소음 감지 (" + String(dB, 1) + "dB)");
    } else if (dB < 30) {
        Serial.println("✅ 정상: 낮은 소음 (" + String(dB, 1) + "dB)");
        if (currentState == WARNING) currentState = NORMAL;
    } else {
        Serial.println("📊 보통: " + String(dB, 1) + "dB");
    }
}

// ====== Arduino 필수 함수들 ======
void setup() {
    Serial.begin(115200);
    delay(2000);
    
    // 핀 설정
    pinMode(BOOT_BUTTON, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);
    pinMode(STATUS_LED, OUTPUT);
    
    Serial.println("=== 아이스크림 가게 냉동고 모니터링 시스템 ===");
    Serial.println("Device: " + deviceID);
    Serial.println("영업시간: " + String(OPEN_HOUR) + ":00 - " + String(CLOSE_HOUR) + ":00");
    Serial.println("부트 버튼: 짧게(업로드 토글), 길게(WiFi 재연결)");
    
    setupI2S();
    connectWiFi();
    
    // NTP 서버 설정 (시간 동기화)
    configTime(9 * 3600, 0, "pool.ntp.org", "time.nist.gov");
    
    Serial.println("System ready");
}

void loop() {
    // 부트 버튼 처리
    handleBootButton();
    
    // WiFi 상태 확인
    wifiConnected = (WiFi.status() == WL_CONNECTED);
    if (!wifiConnected) {
        connectWiFi();
    }
    
    // 운영 시간 확인 (1분마다)
    if (millis() - lastTimeCheck >= 60000) {
        checkOperatingHours();
        lastTimeCheck = millis();
    }
    
    // 영업시간 외에는 대기
    if (!isOperatingHours) {
        updateStatusLED();
        delay(1000);
        return;
    }
    
    // 오디오 수집
    collectAudio();
    
    // dB 분석
    static uint32_t t0 = 0;
    float dB = readdB();
    if (!isnan(dB) && millis() - t0 >= 1000) {
        t0 = millis();
        analyzeSound(dB);
    }
    
    // 업로드
    if (millis() - lastUpload >= UPLOAD_MS) {
        if (uploadEnabled && wifiConnected && bufferIndex >= BUFFER_SIZE) {
            uploadAudio();
            lastUpload = millis();
        } else if (!uploadEnabled) {
            Serial.println("업로드 비활성화됨");
            lastUpload = millis();
        }
    }
    
    // 상태 LED 업데이트
    updateStatusLED();
    
    delay(10);
}
