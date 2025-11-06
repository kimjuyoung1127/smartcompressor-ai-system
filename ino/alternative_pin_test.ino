/*
 * 다양한 핀 조합으로 ICS-43434 테스트
 * 완성형 보드용
 */

#include <driver/i2s.h>

// 핀 조합 1: ESP32 표준 I2S 핀
#define I2S_WS_PIN_1 15
#define I2S_BCK_PIN_1 14
#define I2S_DATA_PIN_1 32

// 핀 조합 2: 대안 핀
#define I2S_WS_PIN_2 25
#define I2S_BCK_PIN_2 26
#define I2S_DATA_PIN_2 27

// 핀 조합 3: 다른 조합
#define I2S_WS_PIN_3 22
#define I2S_BCK_PIN_3 21
#define I2S_DATA_PIN_3 19

#define SAMPLE_RATE 16000
#define BUFFER_SIZE 1024

int16_t audioBuffer[BUFFER_SIZE];
int current_pin_set = 1;

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("=== 완성형 보드 핀 조합 테스트 ===");
    Serial.println("여러 핀 조합을 자동으로 테스트합니다.");
    Serial.println();
    
    testPinCombination(1, I2S_WS_PIN_1, I2S_BCK_PIN_1, I2S_DATA_PIN_1);
    delay(2000);
    
    testPinCombination(2, I2S_WS_PIN_2, I2S_BCK_PIN_2, I2S_DATA_PIN_2);
    delay(2000);
    
    testPinCombination(3, I2S_WS_PIN_3, I2S_BCK_PIN_3, I2S_DATA_PIN_3);
    
    Serial.println("\n=== 모든 핀 조합 테스트 완료 ===");
    Serial.println("가장 좋은 결과를 보인 핀 조합을 사용하세요.");
}

void loop() {
    // 테스트 완료 후 대기
    delay(1000);
}

void testPinCombination(int set_num, int ws_pin, int bck_pin, int data_pin) {
    Serial.println("\n==================================================");
    Serial.println("핀 조합 " + String(set_num) + " 테스트");
    Serial.println("WS: GPIO " + String(ws_pin));
    Serial.println("BCK: GPIO " + String(bck_pin));
    Serial.println("DATA: GPIO " + String(data_pin));
    Serial.println("==================================================");
    
    // I2S 정리
    i2s_driver_uninstall(I2S_NUM_0);
    delay(100);
    
    // 핀 모드 설정
    pinMode(ws_pin, OUTPUT);
    pinMode(bck_pin, OUTPUT);
    pinMode(data_pin, INPUT);
    
    // I2S 설정
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = 1024,
        .use_apll = true,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };
    
    i2s_pin_config_t pin_config = {
        .bck_io_num = bck_pin,
        .ws_io_num = ws_pin,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = data_pin
    };
    
    // I2S 드라이버 설치
    esp_err_t result = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 드라이버 설치 실패: " + String(result));
        return;
    }
    
    // 핀 설정
    result = i2s_set_pin(I2S_NUM_0, &pin_config);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 핀 설정 실패: " + String(result));
        i2s_driver_uninstall(I2S_NUM_0);
        return;
    }
    
    // I2S 시작
    i2s_zero_dma_buffer(I2S_NUM_0);
    result = i2s_start(I2S_NUM_0);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 시작 실패: " + String(result));
        i2s_driver_uninstall(I2S_NUM_0);
        return;
    }
    
    Serial.println("✅ I2S 설정 완료");
    
    // 데이터 읽기 테스트 (3번 시도)
    bool success = false;
    int16_t best_max = 0;
    int16_t best_min = 0;
    int best_non_zero = 0;
    
    for (int attempt = 0; attempt < 3; attempt++) {
        Serial.println("시도 " + String(attempt + 1) + "/3");
        
        size_t bytes_read = 0;
        result = i2s_read(I2S_NUM_0, audioBuffer, BUFFER_SIZE * sizeof(int16_t), &bytes_read, 1000);
        
        if (result == ESP_OK && bytes_read > 0) {
            // 데이터 분석
            int16_t max_val = -32768;
            int16_t min_val = 32767;
            int16_t non_zero_count = 0;
            
            for (int i = 0; i < BUFFER_SIZE; i++) {
                if (audioBuffer[i] > max_val) max_val = audioBuffer[i];
                if (audioBuffer[i] < min_val) min_val = audioBuffer[i];
                if (audioBuffer[i] != 0) non_zero_count++;
            }
            
            Serial.println("  최대값: " + String(max_val));
            Serial.println("  최소값: " + String(min_val));
            Serial.println("  비영점: " + String(non_zero_count) + "/" + String(BUFFER_SIZE));
            
            if (non_zero_count > best_non_zero) {
                best_max = max_val;
                best_min = min_val;
                best_non_zero = non_zero_count;
                success = true;
            }
            
            if (non_zero_count > 50) {
                Serial.println("  ✅ 좋은 신호 감지!");
                break;
            }
        } else {
            Serial.println("  ❌ 읽기 실패: " + String(result));
        }
        
        delay(500);
    }
    
    // 결과 요약
    Serial.println("\n--- 핀 조합 " + String(set_num) + " 결과 ---");
    Serial.println("최대값: " + String(best_max));
    Serial.println("최소값: " + String(best_min));
    Serial.println("비영점 샘플: " + String(best_non_zero) + "/" + String(BUFFER_SIZE));
    Serial.println("동적 범위: " + String(best_max - best_min));
    
    if (success && best_non_zero > 50) {
        Serial.println("🎉 이 핀 조합이 작동합니다!");
        Serial.println("WS: GPIO " + String(ws_pin));
        Serial.println("BCK: GPIO " + String(bck_pin));
        Serial.println("DATA: GPIO " + String(data_pin));
    } else if (success && best_non_zero > 10) {
        Serial.println("⚠️  약한 신호이지만 작동 가능");
    } else {
        Serial.println("❌ 이 핀 조합은 작동하지 않습니다");
    }
    
    Serial.println();
}
