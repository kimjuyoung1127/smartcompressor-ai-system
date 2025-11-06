#include <Arduino.h>
#include <driver/i2s.h>
#include <WiFi.h>
#include <HTTPClient.h>

// ====== 설정 ======
#define SAMPLE_RATE 16000  // 샘플레이트 (AI 분석 표준 16kHz)
#define WINDOW_MS 500      // 윈도우 크기
#define BUFFER_SIZE 1024   // 버퍼 크기 (16kHz 최적화)
#define ANALYSIS_MS 10000  // 10초마다 분석
#define UPLOAD_MS 15000    // 15초마다 업로드

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
    
    // 고급 오디오 특징
    float spectral_rolloff;
    float spectral_bandwidth;
    float spectral_contrast;
    float spectral_flatness;
    float spectral_skewness;
    float spectral_kurtosis;
    float harmonic_ratio;
    float inharmonicity;
    
    // ADSR 특징
    float attack_time;
    float decay_time;
    float sustain_level;
    float release_time;
    
    // 소리 분류
    float frequency_dominance;
};

// ====== 전역 변수 ======
int16_t audioBuffer[BUFFER_SIZE];  // 16-bit 데이터용 int16_t
bool wifiConnected = false;
bool uploadEnabled = true;

unsigned long lastUpload = 0;
unsigned long lastAnalysis = 0;
String deviceID = "ICE_STORE_24H_" + String(SENSOR_NUMBER);

// 버튼 제어
bool lastButtonState = HIGH;
unsigned long lastButtonPress = 0;

// LED 상태 표시
unsigned long lastLEDBlink = 0;
bool ledState = false;

// I2S 설정
const i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,  // 16000Hz (AI 분석 표준)
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = (i2s_comm_format_t)(I2S_COMM_FORMAT_I2S | I2S_COMM_FORMAT_I2S_MSB),  // 작동하는 포맷
    .intr_alloc_flags = 0,  // 작동하는 설정
    .dma_buf_count = 32,    // 작동하는 설정
    .dma_buf_len = 1024,    // 작동하는 설정
    .use_apll = true,       // 고정밀 클록 사용
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
};

const i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_BCK_PIN,  // BCK 핀 (27)
    .ws_io_num = I2S_WS_PIN,    // WS 핀 (25)
    .data_out_num = I2S_PIN_NO_CHANGE, 
    .data_in_num = I2S_DATA_PIN // DATA 핀 (26)
};

// ====== 함수들 ======
void printWiFiInfo() {
    Serial.println("=== WiFi Information (BUPYEONG) ===");
    Serial.println("SSID: " + String(ssid));
    Serial.println("Password: " + String(password));
    Serial.println("Server URL: " + String(serverURL));
    Serial.println("Device ID: " + deviceID);
    Serial.println("Location: " + String(LOCATION));
    Serial.println("WiFi Status: " + String(WiFi.status()));
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("IP Address: " + WiFi.localIP().toString());
        Serial.println("Gateway: " + WiFi.gatewayIP().toString());
        Serial.println("DNS: " + WiFi.dnsIP().toString());
        Serial.println("Signal Strength: " + String(WiFi.RSSI()) + " dBm");
        Serial.println("✅ Ready for data transmission to server");
    }
    Serial.println("=====================================");
}

void setupI2S() {
    Serial.println("=== I2S SETUP (ENHANCED DEBUG) ===");
    Serial.println("Target Sample Rate: " + String(SAMPLE_RATE) + " Hz");
    Serial.println("Buffer Size: " + String(BUFFER_SIZE));
    Serial.println("Bits per Sample: 16");
    Serial.println("Channels: 1 (Mono)");
    
    // 핀 모드 설정
    pinMode(I2S_WS_PIN, OUTPUT);   // WS (25)
    pinMode(I2S_BCK_PIN, OUTPUT);  // BCK (27)
    pinMode(I2S_DATA_PIN, INPUT);  // DATA (26)
    Serial.println("✅ Pin modes configured");
    Serial.println("  WS (Word Select): GPIO " + String(I2S_WS_PIN) + " (OUTPUT)");
    Serial.println("  BCK (Bit Clock): GPIO " + String(I2S_BCK_PIN) + " (OUTPUT)");
    Serial.println("  DATA: GPIO " + String(I2S_DATA_PIN) + " (INPUT)");
    
    // I2S 드라이버 설치
    Serial.println("Installing I2S driver...");
    esp_err_t result = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (result != ESP_OK) {
        Serial.println("❌ I2S driver install FAILED!");
        Serial.println("Error Code: " + String(result));
        Serial.println("Possible causes:");
        Serial.println("  - Invalid I2S configuration");
        Serial.println("  - Hardware not properly connected");
        Serial.println("  - Insufficient memory");
        Serial.println("Continuing without I2S (will use simulation mode)");
        return;
    }
    Serial.println("✅ I2S driver installed successfully");
    
    // 핀 설정
    Serial.println("Configuring I2S pins...");
    result = i2s_set_pin(I2S_NUM_0, &pin_config);
    if (result != ESP_OK) {
        Serial.println("❌ I2S pin config FAILED!");
        Serial.println("Error Code: " + String(result));
        Serial.println("Check pin connections:");
        Serial.println("  WS → GPIO " + String(I2S_WS_PIN));
        Serial.println("  BCK → GPIO " + String(I2S_BCK_PIN));
        Serial.println("  DATA → GPIO " + String(I2S_DATA_PIN));
        return;
    }
    Serial.println("✅ I2S pin configuration successful");
    
    // DMA 버퍼 초기화
    i2s_zero_dma_buffer(I2S_NUM_0);
    Serial.println("✅ DMA buffer zeroed");
    
    // I2S 시작
    Serial.println("Starting I2S...");
    result = i2s_start(I2S_NUM_0);
    if (result != ESP_OK) {
        Serial.println("❌ I2S start FAILED!");
        Serial.println("Error Code: " + String(result));
        return;
    }
    Serial.println("✅ I2S started successfully");
    
    // 최종 설정 확인
    Serial.println("=== I2S CONFIGURATION SUMMARY ===");
    Serial.println("Sample Rate: " + String(SAMPLE_RATE) + " Hz");
    Serial.println("Buffer Count: 8");
    Serial.println("Buffer Length: 1024");
    Serial.println("APLL: " + String(i2s_config.use_apll ? "ENABLED" : "DISABLED"));
    Serial.println("Communication Format: STANDARD I2S");
    Serial.println("I2S Setup Complete! 🎉");
    
    delay(100);
    Serial.println("I2S ready");
}

void connectWiFi() {
    Serial.println("=== WiFi Connection ===");
    Serial.println("SSID: " + String(ssid));
    
    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);
    WiFi.persistent(true);
    WiFi.disconnect();
    delay(500);
    
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    int maxAttempts = 20;
    
    Serial.print("Connecting");
    while (WiFi.status() != WL_CONNECTED && attempts < maxAttempts) {
        delay(1000);
        Serial.print(".");
        attempts++;
        
        if (attempts % 3 == 0) {
            Serial.println();
            Serial.println("Attempt " + String(attempts) + "/" + String(maxAttempts));
            Serial.println("WiFi Status: " + String(WiFi.status()));
            
            if (attempts == 6) {
                Serial.println("Scanning for available networks...");
                int n = WiFi.scanNetworks();
                if (n > 0) {
                    Serial.println("Found " + String(n) + " networks:");
                    for (int i = 0; i < n; i++) {
                        Serial.println("  " + String(i+1) + ": " + WiFi.SSID(i) + " (RSSI: " + String(WiFi.RSSI(i)) + ")");
                    }
                }
            }
        }
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println();
        Serial.println("✅ WiFi Connected Successfully!");
        Serial.println("IP Address: " + WiFi.localIP().toString());
        Serial.println("MAC Address: " + WiFi.macAddress());
        Serial.println("Signal Strength: " + String(WiFi.RSSI()) + " dBm");
        wifiConnected = true;
    } else {
        Serial.println();
        Serial.println("❌ WiFi Connection Failed!");
        Serial.println("Final Status: " + String(WiFi.status()));
        Serial.println("Possible causes:");
        Serial.println("- Wrong SSID or password");
        Serial.println("- WiFi signal too weak");
        Serial.println("- Router not responding");
        wifiConnected = false;
    }
}

bool collectAudio() {
    size_t bytes_read = 0;
    
    Serial.println("=== I2S DEBUG ===");
    
    // I2S 읽기 시도 (3번 시도)
    esp_err_t result = ESP_FAIL;
    for (int attempt = 0; attempt < 3; attempt++) {
        result = i2s_read(I2S_NUM_0, audioBuffer, BUFFER_SIZE * sizeof(int16_t), &bytes_read, 1000);
        
        Serial.println("Attempt " + String(attempt + 1) + ":");
        Serial.println("  I2S Read Result: " + String(result));
        Serial.println("  Bytes Read: " + String(bytes_read));
        
        if (result == ESP_OK && bytes_read > 0) {
            break;
        }
        delay(10);
    }
    
    if (result != ESP_OK) {
        Serial.println("❌ I2S read error: " + String(result));
        return false;
    }
    
    if (bytes_read == 0) {
        Serial.println("❌ No data read from I2S");
        return false;
    }
    
    // 실제 오디오 데이터 분석
    int16_t max_val = -32768;
    int16_t min_val = 32767;
    int16_t non_zero_count = 0;
    int16_t positive_count = 0;
    int16_t negative_count = 0;
    
    for (int i = 0; i < BUFFER_SIZE; i++) {
        if (audioBuffer[i] > max_val) max_val = audioBuffer[i];
        if (audioBuffer[i] < min_val) min_val = audioBuffer[i];
        if (audioBuffer[i] != 0) non_zero_count++;
        if (audioBuffer[i] > 0) positive_count++;
        if (audioBuffer[i] < 0) negative_count++;
    }
    
    Serial.println("=== AUDIO ANALYSIS ===");
    Serial.println("Max value: " + String(max_val));
    Serial.println("Min value: " + String(min_val));
    Serial.println("Buffer range: " + String(max_val - min_val));
    Serial.println("Non-zero samples: " + String(non_zero_count));
    Serial.println("Positive samples: " + String(positive_count));
    Serial.println("Negative samples: " + String(negative_count));
    Serial.println("First 10 samples: " + String(audioBuffer[0]) + ", " + String(audioBuffer[1]) + ", " + String(audioBuffer[2]) + ", " + String(audioBuffer[3]) + ", " + String(audioBuffer[4]));
    
    // 테스트 코드와 동일한 판정 기준
    bool has_sufficient_samples = non_zero_count > 10;  // 최소 10개 이상의 비영점 샘플
    bool has_dynamic_range = (max_val - min_val) > 10;  // 최소 10 이상의 동적 범위
    bool has_both_polarities = (positive_count > 0) && (negative_count > 0);  // 양수와 음수 모두 존재
    
    Serial.println("=== AUDIO VALIDATION ===");
    Serial.println("Sufficient samples: " + String(has_sufficient_samples) + " (" + String(non_zero_count) + "/" + String(BUFFER_SIZE) + ")");
    Serial.println("Dynamic range: " + String(has_dynamic_range) + " (" + String(max_val - min_val) + ")");
    Serial.println("Both polarities: " + String(has_both_polarities) + " (+" + String(positive_count) + ", -" + String(negative_count) + ")");
    
    if (has_sufficient_samples && has_dynamic_range && has_both_polarities) {
        Serial.println("✅ Real audio data detected!");
        Serial.println("  - Sufficient non-zero samples: " + String(non_zero_count));
        Serial.println("  - Good dynamic range: " + String(max_val - min_val));
        Serial.println("  - Both positive and negative values present");
        return true;
    } else {
        Serial.println("❌ No real audio data detected");
        if (!has_sufficient_samples) Serial.println("  - Not enough non-zero samples: " + String(non_zero_count) + " (need >10)");
        if (!has_dynamic_range) Serial.println("  - Dynamic range too small: " + String(max_val - min_val) + " (need >10)");
        if (!has_both_polarities) Serial.println("  - Missing positive/negative values");
        Serial.println("Check hardware connections and microphone power");
        return false;
    }
}

// LED 상태 표시 함수
void updateLEDStatus() {
    unsigned long currentTime = millis();
    
    if (wifiConnected && uploadEnabled) {
        // WiFi 연결됨 + 업로드 활성화: 빠른 깜빡임 (0.5초)
        if (currentTime - lastLEDBlink > 500) {
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
    } else {
        // WiFi 연결 안됨: 느린 깜빡임 (2초)
        if (currentTime - lastLEDBlink > 2000) {
            ledState = !ledState;
            digitalWrite(LED_PIN, ledState);
            lastLEDBlink = currentTime;
        }
    }
}

// RMS 에너지 계산
float calculateRMS(int16_t* buffer, int length) {
    long sum = 0;
    for (int i = 0; i < length; i++) {
        sum += (long)buffer[i] * buffer[i];
    }
    return sqrt((float)sum / length);
}

// 데시벨 계산 (RMS를 dB로 변환)
float calculateDecibel(float rms) {
    if (rms <= 0) return 0;
    // 20 * log10(rms) 공식 사용
    return 20 * log10(rms);
}

// 간소화된 특징 추출 함수들 (ESP32 최적화)



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

float calculateSpectralRolloff(int16_t* buffer, int length) {
    float total_energy = 0.0f;
    for (int i = 0; i < length; i++) {
        total_energy += abs(buffer[i]);
    }
    
    float cumulative_energy = 0.0f;
    float threshold = total_energy * 0.85f;
    
    for (int i = 0; i < length; i++) {
        cumulative_energy += abs(buffer[i]);
        if (cumulative_energy >= threshold) {
            return (float)i / length * (SAMPLE_RATE / 2);
        }
    }
    return SAMPLE_RATE / 2;
}


float classifySoundType(float rms, float spectralCentroid, float zeroCrossingRate) {
    if (rms < 100.0f) {
        return 0.0f; // 정적
    }
    
    // 24kHz 기준으로 주파수 범위 조정
    if (rms > 1000.0f && spectralCentroid > 3000.0f && spectralCentroid < 8000.0f && zeroCrossingRate < 0.15f) {
        return 1.0f; // 압축기
    }
    
    if (rms > 500.0f && spectralCentroid > 8000.0f && zeroCrossingRate > 0.3f) {
        return 2.0f; // 팬
    }
    
    if (rms > 2000.0f) {
        return 3.0f; // 이상음
    }
    
    return 4.0f; // 기타
}

float calculateIntensityLevel(float rms) {
    if (rms < 50.0f) return 0.0f;
    if (rms > 5000.0f) return 1.0f;
    return (rms - 50.0f) / 4950.0f;
}


bool detectCompressorState(float rms, float spectralCentroid, float zeroCrossingRate) {
    // 실제 데이터 기반 압축기 작동 감지
    // 현재 데이터: RMS 190.09, dB 45.6에서도 OFF 상태
    // 더 높은 임계값 적용
    bool isOn = (rms > 200.0f) && 
                (spectralCentroid > 2000.0f && spectralCentroid < 10000.0f) && 
                (zeroCrossingRate < 0.3f);
    return isOn;
}

float calculateAnomalyScore(float rms, float spectralCentroid, float zeroCrossingRate, bool compressorState) {
    float anomaly = 0.0f;
    
    if (rms > 3000.0f) anomaly += 0.3f;
    if (spectralCentroid > 15000.0f) anomaly += 0.2f;  // 24kHz 기준
    if (zeroCrossingRate > 0.6f) anomaly += 0.2f;
    
    if (compressorState && rms < 200.0f) anomaly += 0.3f;
    if (!compressorState && rms > 1500.0f) anomaly += 0.3f;
    
    if (spectralCentroid < 1000.0f) anomaly += 0.1f;
    
    return (anomaly > 1.0f) ? 1.0f : anomaly;
}

// 핀 연결 테스트 함수
void testPinConnections() {
    Serial.println("=== PIN CONNECTION TEST ===");
    
    // WS 핀 테스트
    digitalWrite(I2S_WS_PIN, HIGH);
    delay(100);
    digitalWrite(I2S_WS_PIN, LOW);
    Serial.println("WS Pin (GPIO " + String(I2S_WS_PIN) + ") toggled");
    
    // BCK 핀 테스트
    digitalWrite(I2S_BCK_PIN, HIGH);
    delay(100);
    digitalWrite(I2S_BCK_PIN, LOW);
    Serial.println("BCK Pin (GPIO " + String(I2S_BCK_PIN) + ") toggled");
    
    // DATA 핀 읽기 테스트
    int data_value = digitalRead(I2S_DATA_PIN);
    Serial.println("DATA Pin (GPIO " + String(I2S_DATA_PIN) + ") value: " + String(data_value));
    
    Serial.println("=== CONNECTION CHECKLIST ===");
    Serial.println("ICS-43434 → ESP32");
    Serial.println("VDD → 3.3V");
    Serial.println("GND → GND");
    Serial.println("WS → GPIO " + String(I2S_WS_PIN));
    Serial.println("BCK → GPIO " + String(I2S_BCK_PIN));
    Serial.println("DATA → GPIO " + String(I2S_DATA_PIN));
}


float calculateEfficiencyScore(bool compressorState, float rms, float spectralCentroid) {
    if (!compressorState) return 1.0f;
    
    float efficiency = 1.0f;
    if (rms > 3000.0f) efficiency -= 0.2f;
    if (spectralCentroid > 12000.0f) efficiency -= 0.3f;  // 24kHz 기준
    
    return (efficiency < 0.0f) ? 0.0f : efficiency;
}

// ====== 고급 오디오 특징 계산 함수들 ======

// 스펙트럼 롤오프 계산 (95% 에너지가 포함되는 주파수)
float calculateSpectralRolloff(int16_t* buffer, int length) {
    float total_energy = 0.0f;
    float threshold = 0.0f;
    
    // 전체 에너지 계산
    for (int i = 0; i < length; i++) {
        float magnitude = abs(buffer[i]);
        total_energy += magnitude * magnitude;
    }
    
    threshold = total_energy * 0.95f; // 95% 임계값
    
    // 롤오프 주파수 찾기
    float cumulative_energy = 0.0f;
    for (int i = 0; i < length; i++) {
        float magnitude = abs(buffer[i]);
        cumulative_energy += magnitude * magnitude;
        
        if (cumulative_energy >= threshold) {
            return (float)i * SAMPLE_RATE / length;
        }
    }
    
    return SAMPLE_RATE / 2.0f; // 최대 주파수
}

// 스펙트럼 대역폭 계산
float calculateSpectralBandwidth(int16_t* buffer, int length) {
    float centroid = calculateSpectralCentroid(buffer, length);
    float weighted_variance = 0.0f;
    float magnitude_sum = 0.0f;
    
    for (int i = 0; i < length; i++) {
        float magnitude = abs(buffer[i]);
        float frequency = (float)i * SAMPLE_RATE / length;
        float diff = frequency - centroid;
        
        weighted_variance += magnitude * diff * diff;
        magnitude_sum += magnitude;
    }
    
    return magnitude_sum > 0 ? sqrt(weighted_variance / magnitude_sum) : 0.0f;
}

// 스펙트럼 대비 계산
float calculateSpectralContrast(int16_t* buffer, int length) {
    float peak = 0.0f;
    float valley = 0.0f;
    
    // 피크와 밸리 찾기
    for (int i = 1; i < length - 1; i++) {
        float magnitude = abs(buffer[i]);
        float prev_mag = abs(buffer[i-1]);
        float next_mag = abs(buffer[i+1]);
        
        if (magnitude > prev_mag && magnitude > next_mag) {
            peak = max(peak, magnitude);
        } else if (magnitude < prev_mag && magnitude < next_mag) {
            valley = max(valley, magnitude);
        }
    }
    
    return peak > 0 && valley > 0 ? (peak - valley) / (peak + valley) : 0.0f;
}

// 스펙트럼 평탄도 계산
float calculateSpectralFlatness(int16_t* buffer, int length) {
    float geometric_mean = 1.0f;
    float arithmetic_mean = 0.0f;
    int valid_samples = 0;
    
    for (int i = 0; i < length; i++) {
        float magnitude = abs(buffer[i]);
        if (magnitude > 0) {
            geometric_mean *= pow(magnitude, 1.0f / length);
            arithmetic_mean += magnitude;
            valid_samples++;
        }
    }
    
    if (valid_samples == 0) return 0.0f;
    
    arithmetic_mean /= valid_samples;
    return arithmetic_mean > 0 ? geometric_mean / arithmetic_mean : 0.0f;
}

// 스펙트럼 왜도 계산
float calculateSpectralSkewness(int16_t* buffer, int length) {
    float mean = 0.0f;
    float variance = 0.0f;
    float skewness = 0.0f;
    
    // 평균 계산
    for (int i = 0; i < length; i++) {
        mean += abs(buffer[i]);
    }
    mean /= length;
    
    // 분산 계산
    for (int i = 0; i < length; i++) {
        float diff = abs(buffer[i]) - mean;
        variance += diff * diff;
    }
    variance /= length;
    
    // 왜도 계산
    float std_dev = sqrt(variance);
    if (std_dev > 0) {
        for (int i = 0; i < length; i++) {
            float diff = abs(buffer[i]) - mean;
            skewness += pow(diff / std_dev, 3);
        }
        skewness /= length;
    }
    
    return skewness;
}

// 스펙트럼 첨도 계산
float calculateSpectralKurtosis(int16_t* buffer, int length) {
    float mean = 0.0f;
    float variance = 0.0f;
    float kurtosis = 0.0f;
    
    // 평균 계산
    for (int i = 0; i < length; i++) {
        mean += abs(buffer[i]);
    }
    mean /= length;
    
    // 분산 계산
    for (int i = 0; i < length; i++) {
        float diff = abs(buffer[i]) - mean;
        variance += diff * diff;
    }
    variance /= length;
    
    // 첨도 계산
    float std_dev = sqrt(variance);
    if (std_dev > 0) {
        for (int i = 0; i < length; i++) {
            float diff = abs(buffer[i]) - mean;
            kurtosis += pow(diff / std_dev, 4);
        }
        kurtosis = (kurtosis / length) - 3.0f; // 정규화
    }
    
    return kurtosis;
}

// 하모닉 비율 계산
float calculateHarmonicRatio(int16_t* buffer, int length) {
    float fundamental_freq = 0.0f;
    float harmonic_energy = 0.0f;
    float total_energy = 0.0f;
    
    // 기본 주파수 찾기 (가장 강한 주파수)
    float max_magnitude = 0.0f;
    for (int i = 1; i < length / 2; i++) {
        float magnitude = abs(buffer[i]);
        if (magnitude > max_magnitude) {
            max_magnitude = magnitude;
            fundamental_freq = (float)i * SAMPLE_RATE / length;
        }
    }
    
    // 하모닉 에너지 계산
    for (int i = 1; i < length / 2; i++) {
        float magnitude = abs(buffer[i]);
        float frequency = (float)i * SAMPLE_RATE / length;
        
        total_energy += magnitude * magnitude;
        
        // 하모닉 주파수 체크 (기본 주파수의 정수배)
        if (fundamental_freq > 0) {
            float harmonic_ratio = frequency / fundamental_freq;
            if (abs(harmonic_ratio - round(harmonic_ratio)) < 0.1f) {
                harmonic_energy += magnitude * magnitude;
            }
        }
    }
    
    return total_energy > 0 ? harmonic_energy / total_energy : 0.0f;
}

// 비하모닉성 계산
float calculateInharmonicity(int16_t* buffer, int length) {
    float fundamental_freq = 0.0f;
    float inharmonic_energy = 0.0f;
    float total_energy = 0.0f;
    
    // 기본 주파수 찾기
    float max_magnitude = 0.0f;
    for (int i = 1; i < length / 2; i++) {
        float magnitude = abs(buffer[i]);
        if (magnitude > max_magnitude) {
            max_magnitude = magnitude;
            fundamental_freq = (float)i * SAMPLE_RATE / length;
        }
    }
    
    // 비하모닉 에너지 계산
    for (int i = 1; i < length / 2; i++) {
        float magnitude = abs(buffer[i]);
        float frequency = (float)i * SAMPLE_RATE / length;
        
        total_energy += magnitude * magnitude;
        
        // 비하모닉 주파수 체크
        if (fundamental_freq > 0) {
            float harmonic_ratio = frequency / fundamental_freq;
            if (abs(harmonic_ratio - round(harmonic_ratio)) >= 0.1f) {
                inharmonic_energy += magnitude * magnitude;
            }
        }
    }
    
    return total_energy > 0 ? inharmonic_energy / total_energy : 0.0f;
}

// ADSR 특징 계산
void calculateADSR(int16_t* buffer, int length, float* attack, float* decay, float* sustain, float* release) {
    float peak = 0.0f;
    int peak_index = 0;
    
    // 피크 찾기
    for (int i = 0; i < length; i++) {
        float magnitude = abs(buffer[i]);
        if (magnitude > peak) {
            peak = magnitude;
            peak_index = i;
        }
    }
    
    // Attack Time (0%에서 90%까지)
    float attack_threshold = peak * 0.9f;
    int attack_end = 0;
    for (int i = 0; i < peak_index; i++) {
        if (abs(buffer[i]) >= attack_threshold) {
            attack_end = i;
            break;
        }
    }
    *attack = (float)attack_end / SAMPLE_RATE * 1000.0f; // ms 단위
    
    // Decay Time (90%에서 10%까지)
    float decay_threshold = peak * 0.1f;
    int decay_end = peak_index;
    for (int i = peak_index; i < length; i++) {
        if (abs(buffer[i]) <= decay_threshold) {
            decay_end = i;
            break;
        }
    }
    *decay = (float)(decay_end - peak_index) / SAMPLE_RATE * 1000.0f; // ms 단위
    
    // Sustain Level (평균 레벨)
    float sustain_sum = 0.0f;
    int sustain_count = 0;
    for (int i = peak_index; i < length; i++) {
        sustain_sum += abs(buffer[i]);
        sustain_count++;
    }
    *sustain = sustain_count > 0 ? sustain_sum / sustain_count / peak : 0.0f;
    
    // Release Time (10%에서 0%까지)
    int release_start = decay_end;
    int release_end = length;
    for (int i = release_start; i < length; i++) {
        if (abs(buffer[i]) <= peak * 0.01f) {
            release_end = i;
            break;
        }
    }
    *release = (float)(release_end - release_start) / SAMPLE_RATE * 1000.0f; // ms 단위
}

// 주파수 지배도 계산
float calculateFrequencyDominance(int16_t* buffer, int length) {
    float low_energy = 0.0f;    // 0-1000 Hz
    float mid_energy = 0.0f;    // 1000-4000 Hz
    float high_energy = 0.0f;   // 4000+ Hz
    float total_energy = 0.0f;
    
    for (int i = 0; i < length; i++) {
        float magnitude = abs(buffer[i]);
        float frequency = (float)i * SAMPLE_RATE / length;
        float energy = magnitude * magnitude;
        
        total_energy += energy;
        
        if (frequency <= 1000) {
            low_energy += energy;
        } else if (frequency <= 4000) {
            mid_energy += energy;
        } else {
            high_energy += energy;
        }
    }
    
    if (total_energy == 0) return 0.0f;
    
    // 가장 지배적인 주파수 대역 반환
    if (low_energy >= mid_energy && low_energy >= high_energy) return 0.0f; // 저주파
    if (mid_energy >= high_energy) return 1.0f; // 중주파
    return 2.0f; // 고주파
}

AudioFeatures extractAudioFeatures() {
    AudioFeatures features;
    features.timestamp = millis();
    
    if (collectAudio()) {
        // 실제 오디오 데이터가 있는 경우 - 핵심 특징만 계산
        features.rms_energy = calculateRMS(audioBuffer, BUFFER_SIZE);
        features.spectral_centroid = calculateSpectralCentroid(audioBuffer, BUFFER_SIZE);
        features.zero_crossing_rate = calculateZeroCrossingRate(audioBuffer, BUFFER_SIZE);
        features.decibel_level = calculateDecibel(features.rms_energy);
        
        // 압축기 상태 감지 (간소화)
        features.compressor_state = detectCompressorState(features.rms_energy, features.spectral_centroid, features.zero_crossing_rate) ? 1.0f : 0.0f;
        features.anomaly_score = calculateAnomalyScore(features.rms_energy, features.spectral_centroid, features.zero_crossing_rate, features.compressor_state > 0.5);
        features.efficiency_score = calculateEfficiencyScore(features.compressor_state > 0.5, features.rms_energy, features.spectral_centroid);
        
        // 기본 소리 분류
        features.sound_type = classifySoundType(features.rms_energy, features.spectral_centroid, features.zero_crossing_rate);
        features.intensity_level = calculateIntensityLevel(features.rms_energy);
        
        // 고급 오디오 특징 계산
        features.spectral_rolloff = calculateSpectralRolloff(audioBuffer, BUFFER_SIZE);
        features.spectral_bandwidth = calculateSpectralBandwidth(audioBuffer, BUFFER_SIZE);
        features.spectral_contrast = calculateSpectralContrast(audioBuffer, BUFFER_SIZE);
        features.spectral_flatness = calculateSpectralFlatness(audioBuffer, BUFFER_SIZE);
        features.spectral_skewness = calculateSpectralSkewness(audioBuffer, BUFFER_SIZE);
        features.spectral_kurtosis = calculateSpectralKurtosis(audioBuffer, BUFFER_SIZE);
        features.harmonic_ratio = calculateHarmonicRatio(audioBuffer, BUFFER_SIZE);
        features.inharmonicity = calculateInharmonicity(audioBuffer, BUFFER_SIZE);
        
        // ADSR 특징 계산
        calculateADSR(audioBuffer, BUFFER_SIZE, &features.attack_time, &features.decay_time, &features.sustain_level, &features.release_time);
        
        // 주파수 지배도 계산
        features.frequency_dominance = calculateFrequencyDominance(audioBuffer, BUFFER_SIZE);
        
        Serial.println("=== REAL AUDIO DATA ===");
        Serial.println("RMS: " + String(features.rms_energy, 2));
        Serial.println("Decibel: " + String(features.decibel_level, 1) + " dB");
        Serial.println("Centroid: " + String(features.spectral_centroid, 1) + " Hz");
        Serial.println("Compressor: " + String(features.compressor_state > 0.5 ? "ON" : "OFF"));
    } else {
        // I2S 센서가 작동하지 않는 경우 시뮬레이션 데이터 (간소화)
        Serial.println("=== USING SIMULATION DATA ===");
        
        unsigned long time = millis() / 1000;
        float time_factor = sin(time * 0.1) * 0.3 + 0.7;
        float noise_factor = (random(0, 100) / 100.0) * 0.2;
        
        features.rms_energy = 20.0 + (sin(time * 0.05) * 10.0) + noise_factor;
        features.spectral_centroid = 3000.0 + (sin(time * 0.03) * 2000.0) + (noise_factor * 1000.0);
        features.zero_crossing_rate = 0.1 + (sin(time * 0.04) * 0.05) + noise_factor * 0.02;
        features.decibel_level = calculateDecibel(features.rms_energy);
        
        // 압축기 상태 시뮬레이션 (주기적 ON/OFF)
        features.compressor_state = (sin(time * 0.02) > 0.3) ? 1.0 : 0.0;
        features.anomaly_score = 0.1 + (sin(time * 0.19) * 0.1) + noise_factor * 0.05;
        features.efficiency_score = 0.8 + (sin(time * 0.21) * 0.2) + noise_factor * 0.1;
        
        // 기본 소리 분류 시뮬레이션
        features.sound_type = (int)(sin(time * 0.22) * 2.5 + 2.5) % 5; // 0-4 사이
        features.intensity_level = 0.5 + (sin(time * 0.23) * 0.4) + noise_factor * 0.1;
        
        Serial.println("Simulation - RMS: " + String(features.rms_energy, 2) + 
                      ", Decibel: " + String(features.decibel_level, 1) + " dB" +
                      ", Compressor: " + String(features.compressor_state > 0.5 ? "ON" : "OFF"));
    }
    
    return features;
}

String createJSON(AudioFeatures features) {
    String json = "{";
    json += "\"device_id\":\"" + deviceID + "\",";
    json += "\"timestamp\":" + String(features.timestamp) + ",";
    json += "\"sensor_number\":\"" + String(SENSOR_NUMBER) + "\",";
    json += "\"store_type\":\"" + String(STORE_TYPE) + "\",";
    json += "\"location\":\"" + String(LOCATION) + "\",";
    json += "\"rms_energy\":" + String(features.rms_energy, 3) + ",";
    json += "\"spectral_centroid\":" + String(features.spectral_centroid, 3) + ",";
    json += "\"zero_crossing_rate\":" + String(features.zero_crossing_rate, 3) + ",";
    json += "\"decibel_level\":" + String(features.decibel_level, 3) + ",";
    json += "\"compressor_state\":" + String(features.compressor_state, 3) + ",";
    json += "\"anomaly_score\":" + String(features.anomaly_score, 3) + ",";
    json += "\"efficiency_score\":" + String(features.efficiency_score, 3) + ",";
    json += "\"sound_type\":" + String(features.sound_type, 3) + ",";
    json += "\"intensity_level\":" + String(features.intensity_level, 3);
    json += "}";
    
    return json;
}

void uploadFeatures(AudioFeatures features) {
    if (!wifiConnected) return;
    
    String jsonString = createJSON(features);
    
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Device-ID", deviceID);
    http.addHeader("X-Store-Type", STORE_TYPE);
    http.addHeader("X-Location", LOCATION);
    
    int code = http.POST(jsonString);
    
    if (code > 0) {
        Serial.println("SUCCESS: Features uploaded - " + String(code));
        Serial.println("Data size: " + String(jsonString.length()) + " bytes");
    } else {
        Serial.println("ERROR: Upload failed - " + String(code));
    }
    
    http.end();
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
        } else if (pressDuration >= 3000) {
            Serial.println("=== WiFi Reconnecting ===");
            WiFi.disconnect();
            delay(1000);
            connectWiFi();
        }
    }
    
    lastButtonState = currentButtonState;
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    pinMode(BOOT_BUTTON, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);
    pinMode(STATUS_LED, OUTPUT);
    
    Serial.println("=== 24H Ice Cream Store Monitoring System ===");
    Serial.println("📍 Location: BUPYEONG BRANCH");
    Serial.println("Device: " + deviceID);
    Serial.println("Store Type: " + String(STORE_TYPE));
    Serial.println("Feature-based data transmission mode");
    Serial.println("Compressor On/Off time series analysis");
    
    setupI2S();
    
    // 핀 연결 테스트
    testPinConnections();
    
    // WiFi 정보 출력
    printWiFiInfo();
    
    // WiFi 연결 시도
    connectWiFi();
    
    // 최종 WiFi 상태 확인
    if (wifiConnected) {
        Serial.println("System ready - WiFi connected");
    } else {
        Serial.println("System ready - WiFi not connected");
        Serial.println("Check your WiFi settings and try again");
    }
}

void loop() {
    handleBootButton();
    updateLEDStatus();
    
    // WiFi 상태 확인 및 재연결
    static unsigned long lastWiFiCheck = 0;
    if (millis() - lastWiFiCheck > 10000) { // 10초마다 확인
        lastWiFiCheck = millis();
        
        bool wasConnected = wifiConnected;
        wifiConnected = (WiFi.status() == WL_CONNECTED);
        
        if (!wifiConnected && wasConnected) {
            Serial.println("⚠️ WiFi connection lost! Attempting to reconnect...");
            connectWiFi();
        } else if (wifiConnected && !wasConnected) {
            Serial.println("✅ WiFi reconnected!");
        }
    }
    
    // 오디오 수집
    if (collectAudio()) {
        // 10초마다 특징 분석
        if (millis() - lastAnalysis >= ANALYSIS_MS) {
            lastAnalysis = millis();
            
            AudioFeatures features = extractAudioFeatures();
            
            Serial.println("=== AUDIO FEATURES ===");
            Serial.println("RMS: " + String(features.rms_energy, 2));
            Serial.println("Decibel: " + String(features.decibel_level, 1) + " dB");
            Serial.println("Spectral Centroid: " + String(features.spectral_centroid, 3));
            Serial.println("Compressor State: " + String(features.compressor_state > 0.5 ? "ON" : "OFF"));
            Serial.println("Anomaly Score: " + String(features.anomaly_score, 3));
            Serial.println("Efficiency: " + String(features.efficiency_score, 3));
            
            // 15초마다 업로드
            if (uploadEnabled && millis() - lastUpload >= UPLOAD_MS) {
                lastUpload = millis();
                Serial.println("=== FEATURES UPLOAD START ===");
                uploadFeatures(features);
                Serial.println("=== FEATURES UPLOAD END ===");
            }
        }
    }
    
    delay(100);
}
