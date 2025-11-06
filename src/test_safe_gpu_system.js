#!/usr/bin/env node
/**
 * 안전한 GPU 준비 시스템 테스트
 * GPU 없이도 안전하게 동작하고, GPU 도입 시점에 쉽게 전환할 수 있는 시스템 테스트
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

// 서버 설정
const BASE_URL = 'http://localhost:3000';
const API_BASE = `${BASE_URL}/api/ai`;

// 테스트 데이터
const testAudioFiles = [
    'test_audio_1.wav',
    'test_audio_2.wav',
    'test_audio_3.wav'
];

const testLabels = [0, 1, 0]; // 0: 정상, 1: 이상

class SafeGPUSystemTester {
    constructor() {
        this.testResults = [];
        this.startTime = Date.now();
        
        console.log('🛡️ 안전한 GPU 준비 시스템 테스트 시작');
        console.log('=' * 60);
    }

    /**
     * 테스트 실행
     */
    async runTests() {
        try {
            // 1. GPU 상태 확인
            await this.testGPUStatus();
            
            // 2. 시스템 상태 확인
            await this.testSystemStatus();
            
            // 3. 안전한 특징 추출 테스트
            await this.testSafeFeatureExtraction();
            
            // 4. 안전한 모델 훈련 테스트
            await this.testSafeModelTraining();
            
            // 5. 안전한 예측 테스트
            await this.testSafePrediction();
            
            // 6. 안전한 AI 파이프라인 테스트
            await this.testSafeAIPipeline();
            
            // 7. 배치 처리 테스트
            await this.testBatchProcessing();
            
            // 8. 모델 저장/로드 테스트
            await this.testModelSaveLoad();
            
            // 9. 성능 메트릭 테스트
            await this.testPerformanceMetrics();
            
            // 10. 모델 리셋 테스트
            await this.testModelReset();
            
            // 결과 출력
            this.printTestResults();
            
        } catch (error) {
            console.error('❌ 테스트 실행 중 오류:', error);
        }
    }

    /**
     * GPU 상태 확인 테스트
     */
    async testGPUStatus() {
        console.log('\n1️⃣ GPU 상태 확인 테스트');
        try {
            const response = await axios.get(`${API_BASE}/safe-gpu/gpu-status`);
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ GPU 사용 가능: ${result.gpu_available}`);
                console.log(`   ✅ 현재 디바이스: ${result.device}`);
                
                this.testResults.push({
                    test: 'GPU 상태 확인',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ GPU 상태 확인 실패: ${error.message}`);
            this.testResults.push({
                test: 'GPU 상태 확인',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 시스템 상태 확인 테스트
     */
    async testSystemStatus() {
        console.log('\n2️⃣ 시스템 상태 확인 테스트');
        try {
            const response = await axios.get(`${API_BASE}/safe-gpu/status`);
            
            if (response.data.success) {
                const status = response.data.status;
                console.log(`   ✅ 서비스 이름: ${status.service_name}`);
                console.log(`   ✅ 초기화 상태: ${status.is_initialized}`);
                console.log(`   ✅ GPU 사용 가능: ${status.gpu_available}`);
                console.log(`   ✅ 현재 디바이스: ${status.device}`);
                console.log(`   ✅ 모델 수: ${status.models_count}`);
                
                this.testResults.push({
                    test: '시스템 상태 확인',
                    success: true,
                    result: status
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 시스템 상태 확인 실패: ${error.message}`);
            this.testResults.push({
                test: '시스템 상태 확인',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 안전한 특징 추출 테스트
     */
    async testSafeFeatureExtraction() {
        console.log('\n3️⃣ 안전한 특징 추출 테스트');
        try {
            // 가상의 오디오 파일 생성
            const testAudioPath = await this.createTestAudioFile();
            
            const formData = new FormData();
            formData.append('audio', fs.createReadStream(testAudioPath));
            formData.append('sampleRate', '16000');
            
            const response = await axios.post(`${API_BASE}/safe-gpu/extract-features`, formData, {
                headers: formData.getHeaders()
            });
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ 특징 추출 성공`);
                console.log(`   ✅ 특징 수: ${Object.keys(result.features || {}).length}`);
                
                this.testResults.push({
                    test: '안전한 특징 추출',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
            
            // 테스트 파일 삭제
            fs.unlinkSync(testAudioPath);
            
        } catch (error) {
            console.error(`   ❌ 안전한 특징 추출 실패: ${error.message}`);
            this.testResults.push({
                test: '안전한 특징 추출',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 안전한 모델 훈련 테스트
     */
    async testSafeModelTraining() {
        console.log('\n4️⃣ 안전한 모델 훈련 테스트');
        try {
            // 가상의 특징 데이터 생성
            const features = this.generateTestFeatures(10);
            const labels = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1];
            
            const response = await axios.post(`${API_BASE}/safe-gpu/train`, {
                features: features,
                labels: labels
            });
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ 모델 훈련 성공`);
                console.log(`   ✅ 훈련된 모델 수: ${Object.keys(result.models || {}).length}`);
                
                this.testResults.push({
                    test: '안전한 모델 훈련',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 안전한 모델 훈련 실패: ${error.message}`);
            this.testResults.push({
                test: '안전한 모델 훈련',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 안전한 예측 테스트
     */
    async testSafePrediction() {
        console.log('\n5️⃣ 안전한 예측 테스트');
        try {
            // 가상의 특징 데이터 생성
            const features = this.generateTestFeatures(5);
            
            const response = await axios.post(`${API_BASE}/safe-gpu/predict`, {
                features: features,
                modelName: null // 자동 선택
            });
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ 예측 성공`);
                console.log(`   ✅ 예측 결과: ${result.prediction}`);
                console.log(`   ✅ 신뢰도: ${result.confidence}`);
                
                this.testResults.push({
                    test: '안전한 예측',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 안전한 예측 실패: ${error.message}`);
            this.testResults.push({
                test: '안전한 예측',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 안전한 AI 파이프라인 테스트
     */
    async testSafeAIPipeline() {
        console.log('\n6️⃣ 안전한 AI 파이프라인 테스트');
        try {
            const response = await axios.post(`${API_BASE}/safe-gpu/pipeline`, {
                audioFiles: testAudioFiles,
                labels: testLabels
            });
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ AI 파이프라인 성공`);
                console.log(`   ✅ GPU 사용 가능: ${result.gpu_available}`);
                console.log(`   ✅ 현재 디바이스: ${result.device}`);
                console.log(`   ✅ 최고 정확도: ${result.best_accuracy?.toFixed(3)}`);
                console.log(`   ✅ 최고 모델: ${result.best_model}`);
                
                this.testResults.push({
                    test: '안전한 AI 파이프라인',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 안전한 AI 파이프라인 실패: ${error.message}`);
            this.testResults.push({
                test: '안전한 AI 파이프라인',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 배치 처리 테스트
     */
    async testBatchProcessing() {
        console.log('\n7️⃣ 배치 처리 테스트');
        try {
            const response = await axios.post(`${API_BASE}/safe-gpu/batch-process`, {
                audioFiles: testAudioFiles,
                labels: testLabels,
                batchSize: 2
            });
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ 배치 처리 성공`);
                console.log(`   ✅ 총 배치 수: ${result.total_batches}`);
                console.log(`   ✅ 처리된 배치 수: ${result.results.length}`);
                
                this.testResults.push({
                    test: '배치 처리',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 배치 처리 실패: ${error.message}`);
            this.testResults.push({
                test: '배치 처리',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 모델 저장/로드 테스트
     */
    async testModelSaveLoad() {
        console.log('\n8️⃣ 모델 저장/로드 테스트');
        try {
            // 모델 저장
            const saveResponse = await axios.post(`${API_BASE}/safe-gpu/save-models`, {
                filepath: 'test_safe_models.pkl'
            });
            
            if (saveResponse.data.success) {
                console.log(`   ✅ 모델 저장 성공`);
                
                // 모델 로드
                const loadResponse = await axios.post(`${API_BASE}/safe-gpu/load-models`, {
                    filepath: 'test_safe_models.pkl'
                });
                
                if (loadResponse.data.success) {
                    console.log(`   ✅ 모델 로드 성공`);
                    
                    this.testResults.push({
                        test: '모델 저장/로드',
                        success: true,
                        result: {
                            save: saveResponse.data.result,
                            load: loadResponse.data.result
                        }
                    });
                } else {
                    throw new Error(loadResponse.data.message);
                }
            } else {
                throw new Error(saveResponse.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 모델 저장/로드 실패: ${error.message}`);
            this.testResults.push({
                test: '모델 저장/로드',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 성능 메트릭 테스트
     */
    async testPerformanceMetrics() {
        console.log('\n9️⃣ 성능 메트릭 테스트');
        try {
            const response = await axios.get(`${API_BASE}/safe-gpu/performance`);
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ 성능 메트릭 조회 성공`);
                console.log(`   ✅ 메트릭 수: ${Object.keys(result.metrics || {}).length}`);
                
                this.testResults.push({
                    test: '성능 메트릭',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 성능 메트릭 조회 실패: ${error.message}`);
            this.testResults.push({
                test: '성능 메트릭',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 모델 리셋 테스트
     */
    async testModelReset() {
        console.log('\n🔟 모델 리셋 테스트');
        try {
            const response = await axios.post(`${API_BASE}/safe-gpu/reset`);
            
            if (response.data.success) {
                console.log(`   ✅ 모델 리셋 성공`);
                
                this.testResults.push({
                    test: '모델 리셋',
                    success: true,
                    result: response.data.result
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 모델 리셋 실패: ${error.message}`);
            this.testResults.push({
                test: '모델 리셋',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 테스트 결과 출력
     */
    printTestResults() {
        const endTime = Date.now();
        const totalTime = (endTime - this.startTime) / 1000;
        
        console.log('\n' + '=' * 60);
        console.log('📊 테스트 결과 요약');
        console.log('=' * 60);
        
        const successCount = this.testResults.filter(r => r.success).length;
        const totalCount = this.testResults.length;
        const successRate = (successCount / totalCount) * 100;
        
        console.log(`총 테스트 수: ${totalCount}`);
        console.log(`성공한 테스트: ${successCount}`);
        console.log(`실패한 테스트: ${totalCount - successCount}`);
        console.log(`성공률: ${successRate.toFixed(1)}%`);
        console.log(`총 소요 시간: ${totalTime.toFixed(2)}초`);
        
        console.log('\n📋 상세 결과:');
        this.testResults.forEach((result, index) => {
            const status = result.success ? '✅' : '❌';
            console.log(`${index + 1}. ${status} ${result.test}`);
            if (!result.success && result.error) {
                console.log(`   오류: ${result.error}`);
            }
        });
        
        if (successRate >= 80) {
            console.log('\n🎉 테스트 성공! 안전한 GPU 준비 시스템이 정상적으로 동작합니다.');
        } else {
            console.log('\n⚠️ 일부 테스트가 실패했습니다. 로그를 확인해주세요.');
        }
    }

    /**
     * 가상의 오디오 파일 생성
     */
    async createTestAudioFile() {
        const testAudioPath = path.join(__dirname, 'test_audio.wav');
        
        // 간단한 사인파 생성 (1초, 440Hz)
        const sampleRate = 16000;
        const duration = 1.0;
        const frequency = 440;
        const samples = Math.floor(sampleRate * duration);
        
        const audioData = new Float32Array(samples);
        for (let i = 0; i < samples; i++) {
            audioData[i] = Math.sin(2 * Math.PI * frequency * i / sampleRate) * 0.5;
        }
        
        // WAV 파일 헤더 생성
        const buffer = Buffer.alloc(44 + samples * 2);
        let offset = 0;
        
        // RIFF 헤더
        buffer.write('RIFF', offset); offset += 4;
        buffer.writeUInt32LE(36 + samples * 2, offset); offset += 4;
        buffer.write('WAVE', offset); offset += 4;
        
        // fmt 청크
        buffer.write('fmt ', offset); offset += 4;
        buffer.writeUInt32LE(16, offset); offset += 4;
        buffer.writeUInt16LE(1, offset); offset += 2;  // PCM
        buffer.writeUInt16LE(1, offset); offset += 2;  // 모노
        buffer.writeUInt32LE(sampleRate, offset); offset += 4;
        buffer.writeUInt32LE(sampleRate * 2, offset); offset += 4;
        buffer.writeUInt16LE(2, offset); offset += 2;  // 바이트/샘플
        buffer.writeUInt16LE(16, offset); offset += 2; // 비트/샘플
        
        // data 청크
        buffer.write('data', offset); offset += 4;
        buffer.writeUInt32LE(samples * 2, offset); offset += 4;
        
        // 오디오 데이터
        for (let i = 0; i < samples; i++) {
            const sample = Math.max(-1, Math.min(1, audioData[i]));
            buffer.writeInt16LE(Math.floor(sample * 32767), offset);
            offset += 2;
        }
        
        fs.writeFileSync(testAudioPath, buffer);
        return testAudioPath;
    }

    /**
     * 가상의 특징 데이터 생성
     */
    generateTestFeatures(count) {
        const features = [];
        for (let i = 0; i < count; i++) {
            features.push([
                Math.random() * 0.5,  // rms
                Math.random() * 0.3,  // zcr
                Math.random() * 1000, // spectral_centroid
                Math.random() * 0.4,  // spectral_rolloff
                Math.random() * 500   // spectral_bandwidth
            ]);
        }
        return features;
    }
}

// 테스트 실행
if (require.main === module) {
    const tester = new SafeGPUSystemTester();
    tester.runTests().catch(console.error);
}

module.exports = SafeGPUSystemTester;
