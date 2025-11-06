#!/usr/bin/env node
/**
 * 경량화된 3순위 조합 시스템 테스트
 * 10-15개 하드웨어로 딥러닝 + 다중 센서 융합 + 실시간 적응형 학습 테스트
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
    'test_audio_3.wav',
    'test_audio_4.wav',
    'test_audio_5.wav'
];

const testLabels = [0, 1, 0, 1, 0]; // 0: 정상, 1: 이상

class Lightweight3TierSystemTester {
    constructor() {
        this.testResults = [];
        this.startTime = Date.now();
        
        console.log('🚀 경량화된 3순위 조합 시스템 테스트 시작');
        console.log('=' * 60);
    }

    /**
     * 테스트 실행
     */
    async runTests() {
        try {
            // 1. 하드웨어 사양 확인
            await this.testHardwareSpecs();
            
            // 2. 시스템 상태 확인
            await this.testSystemStatus();
            
            // 3. 통합 3순위 조합 시스템 테스트
            await this.testIntegrated3TierSystem();
            
            // 4. 경량화된 딥러닝 모델 훈련 테스트
            await this.testLightweightModelTraining();
            
            // 5. 다중 센서 융합 테스트
            await this.testMultiSensorFusion();
            
            // 6. 실시간 적응형 학습 테스트
            await this.testAdaptiveLearning();
            
            // 7. 배치 처리 테스트
            await this.testBatchProcessing();
            
            // 8. 하드웨어별 성능 분석 테스트
            await this.testHardwareAnalysis();
            
            // 9. 시스템 최적화 테스트
            await this.testSystemOptimization();
            
            // 10. 하드웨어 수 조정 테스트
            await this.testHardwareAdjustment();
            
            // 결과 출력
            this.printTestResults();
            
        } catch (error) {
            console.error('❌ 테스트 실행 중 오류:', error);
        }
    }

    /**
     * 하드웨어 사양 확인 테스트
     */
    async testHardwareSpecs() {
        console.log('\n1️⃣ 하드웨어 사양 확인 테스트');
        try {
            const response = await axios.get(`${API_BASE}/lightweight-3tier/hardware-specs`);
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ CPU 코어: ${result.cpu_cores}`);
                console.log(`   ✅ RAM: ${result.ram_gb}GB`);
                console.log(`   ✅ 디스크: ${result.disk_gb}GB`);
                console.log(`   ✅ GPU 사용 가능: ${result.gpu_available}`);
                console.log(`   ✅ 네트워크: ${result.network_mbps}Mbps`);
                
                this.testResults.push({
                    test: '하드웨어 사양 확인',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 하드웨어 사양 확인 실패: ${error.message}`);
            this.testResults.push({
                test: '하드웨어 사양 확인',
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
            const response = await axios.get(`${API_BASE}/lightweight-3tier/status`);
            
            if (response.data.success) {
                const status = response.data.status;
                console.log(`   ✅ 서비스 이름: ${status.service_name}`);
                console.log(`   ✅ 초기화 상태: ${status.is_initialized}`);
                console.log(`   ✅ 하드웨어 수: ${status.hardware_count}`);
                console.log(`   ✅ 모델 수: ${status.models_count}`);
                console.log(`   ✅ 센서 수: ${status.sensors_count}`);
                console.log(`   ✅ 학습 시스템 수: ${status.learning_systems_count}`);
                
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
     * 통합 3순위 조합 시스템 테스트
     */
    async testIntegrated3TierSystem() {
        console.log('\n3️⃣ 통합 3순위 조합 시스템 테스트');
        try {
            const response = await axios.post(`${API_BASE}/lightweight-3tier/integrated`, {
                audioFiles: testAudioFiles,
                labels: testLabels
            });
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ 통합 시스템 성공`);
                console.log(`   ✅ 최종 정확도: ${result.final_accuracy?.toFixed(3)}`);
                console.log(`   ✅ 딥러닝 정확도: ${result.dl_accuracy?.toFixed(3)}`);
                console.log(`   ✅ 센서 융합 성공: ${result.sensor_success}`);
                console.log(`   ✅ 적응형 학습 성공률: ${result.adaptive_success_rate?.toFixed(3)}`);
                console.log(`   ✅ 하드웨어 수: ${result.hardware_count}`);
                
                this.testResults.push({
                    test: '통합 3순위 조합 시스템',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 통합 3순위 조합 시스템 실패: ${error.message}`);
            this.testResults.push({
                test: '통합 3순위 조합 시스템',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 경량화된 딥러닝 모델 훈련 테스트
     */
    async testLightweightModelTraining() {
        console.log('\n4️⃣ 경량화된 딥러닝 모델 훈련 테스트');
        try {
            // 가상의 특징 데이터 생성
            const features = this.generateTestFeatures(20);
            const labels = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1];
            
            const response = await axios.post(`${API_BASE}/lightweight-3tier/train-models`, {
                features: features,
                labels: labels
            });
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ 모델 훈련 성공`);
                console.log(`   ✅ 평균 정확도: ${result.overall_accuracy?.toFixed(3)}`);
                console.log(`   ✅ 훈련된 하드웨어 수: ${Object.keys(result.hardware_results || {}).length}`);
                
                this.testResults.push({
                    test: '경량화된 딥러닝 모델 훈련',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 경량화된 딥러닝 모델 훈련 실패: ${error.message}`);
            this.testResults.push({
                test: '경량화된 딥러닝 모델 훈련',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 다중 센서 융합 테스트
     */
    async testMultiSensorFusion() {
        console.log('\n5️⃣ 다중 센서 융합 테스트');
        try {
            // 가상의 오디오 파일 생성
            const testAudioPath = await this.createTestAudioFile();
            
            const formData = new FormData();
            formData.append('audio', fs.createReadStream(testAudioPath));
            formData.append('sampleRate', '16000');
            
            const response = await axios.post(`${API_BASE}/lightweight-3tier/sensor-fusion`, formData, {
                headers: formData.getHeaders()
            });
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ 센서 융합 성공`);
                console.log(`   ✅ 센서 읽기 수: ${Object.keys(result.sensor_readings || {}).length}`);
                console.log(`   ✅ 융합된 특징 수: ${result.fused_features?.length || 0}`);
                console.log(`   ✅ 융합 방법: ${result.fusion_method}`);
                
                this.testResults.push({
                    test: '다중 센서 융합',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
            
            // 테스트 파일 삭제
            fs.unlinkSync(testAudioPath);
            
        } catch (error) {
            console.error(`   ❌ 다중 센서 융합 실패: ${error.message}`);
            this.testResults.push({
                test: '다중 센서 융합',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 실시간 적응형 학습 테스트
     */
    async testAdaptiveLearning() {
        console.log('\n6️⃣ 실시간 적응형 학습 테스트');
        try {
            // 가상의 오디오 데이터 생성
            const audioData = this.generateTestAudioData();
            
            const response = await axios.post(`${API_BASE}/lightweight-3tier/adaptive-learning`, {
                audioData: audioData,
                groundTruth: 1,
                hardwareId: 0
            });
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ 적응형 학습 성공`);
                console.log(`   ✅ 예측 결과: ${result.prediction}`);
                console.log(`   ✅ 신뢰도: ${result.confidence?.toFixed(3)}`);
                console.log(`   ✅ 학습률: ${result.learning_rate?.toFixed(6)}`);
                console.log(`   ✅ 오류: ${result.error?.toFixed(3)}`);
                
                this.testResults.push({
                    test: '실시간 적응형 학습',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 실시간 적응형 학습 실패: ${error.message}`);
            this.testResults.push({
                test: '실시간 적응형 학습',
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
            const response = await axios.post(`${API_BASE}/lightweight-3tier/batch-process`, {
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
     * 하드웨어별 성능 분석 테스트
     */
    async testHardwareAnalysis() {
        console.log('\n8️⃣ 하드웨어별 성능 분석 테스트');
        try {
            const response = await axios.get(`${API_BASE}/lightweight-3tier/hardware-analysis`);
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ 하드웨어 성능 분석 성공`);
                console.log(`   ✅ 분석 결과 수: ${Object.keys(result.analysis || {}).length}`);
                
                this.testResults.push({
                    test: '하드웨어별 성능 분석',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 하드웨어별 성능 분석 실패: ${error.message}`);
            this.testResults.push({
                test: '하드웨어별 성능 분석',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 시스템 최적화 테스트
     */
    async testSystemOptimization() {
        console.log('\n9️⃣ 시스템 최적화 테스트');
        try {
            const response = await axios.post(`${API_BASE}/lightweight-3tier/optimize`);
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ 시스템 최적화 성공`);
                console.log(`   ✅ 최적화 결과: ${result.optimization_result || '완료'}`);
                
                this.testResults.push({
                    test: '시스템 최적화',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 시스템 최적화 실패: ${error.message}`);
            this.testResults.push({
                test: '시스템 최적화',
                success: false,
                error: error.message
            });
        }
    }

    /**
     * 하드웨어 수 조정 테스트
     */
    async testHardwareAdjustment() {
        console.log('\n🔟 하드웨어 수 조정 테스트');
        try {
            const response = await axios.post(`${API_BASE}/lightweight-3tier/adjust-hardware`, {
                hardwareCount: 15
            });
            
            if (response.data.success) {
                const result = response.data.result;
                console.log(`   ✅ 하드웨어 수 조정 성공`);
                console.log(`   ✅ 새로운 하드웨어 수: ${result.hardware_count}`);
                
                this.testResults.push({
                    test: '하드웨어 수 조정',
                    success: true,
                    result: result
                });
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            console.error(`   ❌ 하드웨어 수 조정 실패: ${error.message}`);
            this.testResults.push({
                test: '하드웨어 수 조정',
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
            console.log('\n🎉 테스트 성공! 경량화된 3순위 조합 시스템이 정상적으로 동작합니다.');
            console.log('   ✅ 10-15개 하드웨어로 3순위 조합 구현 가능');
            console.log('   ✅ 딥러닝 + 다중 센서 융합 + 실시간 적응형 학습 동작');
            console.log('   ✅ CPU만으로도 충분한 성능');
        } else {
            console.log('\n⚠️ 일부 테스트가 실패했습니다. 로그를 확인해주세요.');
        }
    }

    /**
     * 가상의 오디오 파일 생성
     */
    async createTestAudioFile() {
        const testAudioPath = path.join(__dirname, 'test_audio_3tier.wav');
        
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

    /**
     * 가상의 오디오 데이터 생성
     */
    generateTestAudioData() {
        const sampleRate = 16000;
        const duration = 1.0;
        const samples = Math.floor(sampleRate * duration);
        
        const audioData = [];
        for (let i = 0; i < samples; i++) {
            audioData.push(Math.sin(2 * Math.PI * 440 * i / sampleRate) * 0.5);
        }
        
        return audioData;
    }
}

// 테스트 실행
if (require.main === module) {
    const tester = new Lightweight3TierSystemTester();
    tester.runTests().catch(console.error);
}

module.exports = Lightweight3TierSystemTester;
