#!/usr/bin/env node
/**
 * 완전한 AI 시스템 테스트 스크립트
 * Phase 1, 2, 3 전체 시스템 통합 테스트
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

// 서버 설정
const SERVER_URL = 'http://localhost:3000';
const API_BASE = `${SERVER_URL}/api/ai`;

class CompleteSystemTester {
    constructor() {
        this.testResults = {
            phase1: { success: false, stats: null },
            phase2: { success: false, stats: null },
            phase3: { success: false, stats: null },
            overall: { success: false, stats: null }
        };
        
        console.log('🎯 완전한 AI 시스템 테스트 시작');
        console.log(`🌐 서버 URL: ${SERVER_URL}`);
        console.log(`📡 API 베이스: ${API_BASE}`);
        console.log('=' * 60);
    }

    /**
     * 서버 상태 확인
     */
    async checkServerStatus() {
        try {
            console.log('\n🔍 서버 상태 확인 중...');
            const response = await axios.get(`${API_BASE}/status`);
            console.log('✅ 서버 연결 성공');
            return true;
        } catch (error) {
            console.error('❌ 서버 연결 실패:', error.message);
            return false;
        }
    }

    /**
     * 전체 시스템 상태 확인
     */
    async checkSystemStatus() {
        try {
            console.log('\n🔍 전체 시스템 상태 확인 중...');
            const response = await axios.get(`${API_BASE}/system/status`);
            console.log('✅ 전체 시스템 상태 조회 성공');
            console.log('📊 시스템 상태:', response.data.systemStatus);
            return response.data.systemStatus;
        } catch (error) {
            console.error('❌ 전체 시스템 상태 조회 실패:', error.message);
            return null;
        }
    }

    /**
     * 가상의 정상 오디오 파일 생성
     */
    generateTestAudio(duration = 5.0, sampleRate = 16000, anomalyType = 'normal') {
        const samples = Math.floor(duration * sampleRate);
        const audioData = new Float32Array(samples);
        
        // 정상 냉장고 소음 시뮬레이션
        for (let i = 0; i < samples; i++) {
            const t = i / sampleRate;
            let sample = 0;
            
            if (anomalyType === 'normal') {
                // 정상 소음 (60Hz 기본 주파수)
                sample = Math.sin(2 * Math.PI * 60 * t);
                sample += 0.3 * Math.sin(2 * Math.PI * 120 * t);
                sample += 0.2 * Math.sin(2 * Math.PI * 180 * t);
                sample += (Math.random() - 0.5) * 0.1; // 노이즈
            } else if (anomalyType === 'bearing_wear') {
                // 베어링 마모 (고주파 소음)
                sample = Math.sin(2 * Math.PI * 60 * t);
                sample += 0.5 * Math.sin(2 * Math.PI * 1000 * t);
                sample += 0.4 * Math.sin(2 * Math.PI * 1500 * t);
                sample += (Math.random() - 0.5) * 0.2;
            } else if (anomalyType === 'compressor_abnormal') {
                // 압축기 이상 (높은 에너지)
                sample = Math.sin(2 * Math.PI * 60 * t) * 2.0;
                sample += (Math.random() - 0.5) * 0.3;
            }
            
            audioData[i] = sample;
        }
        
        return audioData;
    }

    /**
     * WAV 파일 생성
     */
    createWAVFile(audioData, sampleRate, filename) {
        const buffer = Buffer.alloc(44 + audioData.length * 2);
        
        // WAV 헤더 작성
        buffer.write('RIFF', 0);
        buffer.writeUInt32LE(36 + audioData.length * 2, 4);
        buffer.write('WAVE', 8);
        buffer.write('fmt ', 12);
        buffer.writeUInt32LE(16, 16);
        buffer.writeUInt16LE(1, 20);
        buffer.writeUInt16LE(1, 22);
        buffer.writeUInt32LE(sampleRate, 24);
        buffer.writeUInt32LE(sampleRate * 2, 28);
        buffer.writeUInt16LE(2, 32);
        buffer.writeUInt16LE(16, 34);
        buffer.write('data', 36);
        buffer.writeUInt32LE(audioData.length * 2, 40);
        
        // 오디오 데이터 작성
        for (let i = 0; i < audioData.length; i++) {
            const sample = Math.max(-1, Math.min(1, audioData[i]));
            buffer.writeInt16LE(Math.floor(sample * 32767), 44 + i * 2);
        }
        
        fs.writeFileSync(filename, buffer);
        return filename;
    }

    /**
     * Phase 1 테스트
     */
    async testPhase1() {
        try {
            console.log('\n🎯 Phase 1 테스트 시작...');
            
            // 1. Phase 1 상태 확인
            const statusResponse = await axios.get(`${API_BASE}/phase1/status`);
            console.log('✅ Phase 1 상태 확인 완료');
            
            // 2. 가상의 정상 데이터로 훈련
            const normalFiles = [];
            for (let i = 0; i < 10; i++) {
                const audioData = this.generateTestAudio(5.0, 16000, 'normal');
                const filename = `temp_normal_${i}.wav`;
                this.createWAVFile(audioData, 16000, filename);
                normalFiles.push(path.resolve(filename));
            }
            
            const trainResponse = await axios.post(`${API_BASE}/phase1/train`, {
                normalAudioFiles: normalFiles
            });
            console.log('✅ Phase 1 모델 훈련 완료');
            
            // 3. Phase 1 이상 탐지 테스트
            const testAudio = this.generateTestAudio(5.0, 16000, 'normal');
            const testFilename = 'temp_test_phase1.wav';
            this.createWAVFile(testAudio, 16000, testFilename);
            
            const formData = new FormData();
            formData.append('audio', fs.createReadStream(testFilename));
            formData.append('sampleRate', '16000');
            
            const detectResponse = await axios.post(`${API_BASE}/phase1/detect`, formData, {
                headers: { ...formData.getHeaders() }
            });
            
            console.log('✅ Phase 1 이상 탐지 테스트 완료');
            console.log(`   결과: ${detectResponse.data.result.isAnomaly ? '이상' : '정상'}`);
            console.log(`   신뢰도: ${(detectResponse.data.result.confidence * 100).toFixed(1)}%`);
            
            // 4. Phase 1 통계 조회
            const statsResponse = await axios.get(`${API_BASE}/phase1/stats`);
            
            // 임시 파일 정리
            normalFiles.forEach(file => {
                if (fs.existsSync(file)) fs.unlinkSync(file);
            });
            if (fs.existsSync(testFilename)) fs.unlinkSync(testFilename);
            
            this.testResults.phase1 = {
                success: true,
                stats: statsResponse.data.stats
            };
            
            console.log('✅ Phase 1 테스트 완료');
            return true;
            
        } catch (error) {
            console.error('❌ Phase 1 테스트 실패:', error.message);
            this.testResults.phase1.success = false;
            return false;
        }
    }

    /**
     * Phase 2 테스트
     */
    async testPhase2() {
        try {
            console.log('\n🔄 Phase 2 테스트 시작...');
            
            // 1. Phase 2 초기화
            const initResponse = await axios.post(`${API_BASE}/phase2/initialize`);
            console.log('✅ Phase 2 초기화 완료');
            
            // 2. Phase 2 상태 확인
            const statusResponse = await axios.get(`${API_BASE}/phase2/status`);
            console.log('✅ Phase 2 상태 확인 완료');
            
            // 3. Phase 2 적응형 이상 탐지 테스트
            const testAudio = this.generateTestAudio(5.0, 16000, 'bearing_wear');
            const testFilename = 'temp_test_phase2.wav';
            this.createWAVFile(testAudio, 16000, testFilename);
            
            const formData = new FormData();
            formData.append('audio', fs.createReadStream(testFilename));
            formData.append('sampleRate', '16000');
            formData.append('groundTruth', 'true');
            
            const detectResponse = await axios.post(`${API_BASE}/phase2/detect`, formData, {
                headers: { ...formData.getHeaders() }
            });
            
            console.log('✅ Phase 2 적응형 이상 탐지 테스트 완료');
            console.log(`   결과: ${detectResponse.data.result.isAnomaly ? '이상' : '정상'}`);
            console.log(`   신뢰도: ${(detectResponse.data.result.confidence * 100).toFixed(1)}%`);
            console.log(`   이상 유형: ${detectResponse.data.result.anomalyType}`);
            
            // 4. Phase 2 통계 조회
            const statsResponse = await axios.get(`${API_BASE}/phase2/stats`);
            
            // 임시 파일 정리
            if (fs.existsSync(testFilename)) fs.unlinkSync(testFilename);
            
            this.testResults.phase2 = {
                success: true,
                stats: statsResponse.data.stats
            };
            
            console.log('✅ Phase 2 테스트 완료');
            return true;
            
        } catch (error) {
            console.error('❌ Phase 2 테스트 실패:', error.message);
            this.testResults.phase2.success = false;
            return false;
        }
    }

    /**
     * Phase 3 테스트
     */
    async testPhase3() {
        try {
            console.log('\n🎯 Phase 3 테스트 시작...');
            
            // 1. Phase 3 초기화
            const initResponse = await axios.post(`${API_BASE}/phase3/initialize`);
            console.log('✅ Phase 3 초기화 완료');
            
            // 2. Phase 3 상태 확인
            const statusResponse = await axios.get(`${API_BASE}/phase3/status`);
            console.log('✅ Phase 3 상태 확인 완료');
            
            // 3. Phase 3 통합 이상 탐지 테스트
            const testAudio = this.generateTestAudio(5.0, 16000, 'compressor_abnormal');
            const testFilename = 'temp_test_phase3.wav';
            this.createWAVFile(testAudio, 16000, testFilename);
            
            const formData = new FormData();
            formData.append('audio', fs.createReadStream(testFilename));
            formData.append('sampleRate', '16000');
            formData.append('groundTruth', 'true');
            
            const detectResponse = await axios.post(`${API_BASE}/phase3/detect`, formData, {
                headers: { ...formData.getHeaders() }
            });
            
            console.log('✅ Phase 3 통합 이상 탐지 테스트 완료');
            console.log(`   결과: ${detectResponse.data.result.isAnomaly ? '이상' : '정상'}`);
            console.log(`   신뢰도: ${(detectResponse.data.result.confidence * 100).toFixed(1)}%`);
            console.log(`   이상 유형: ${detectResponse.data.result.anomalyType}`);
            console.log(`   시스템 신뢰성: ${(detectResponse.data.result.systemReliability * 100).toFixed(1)}%`);
            
            // 4. Phase 3 통계 조회
            const statsResponse = await axios.get(`${API_BASE}/phase3/stats`);
            
            // 5. 모니터링 데이터 조회
            const monitoringResponse = await axios.get(`${API_BASE}/phase3/monitoring?limit=10`);
            
            // 임시 파일 정리
            if (fs.existsSync(testFilename)) fs.unlinkSync(testFilename);
            
            this.testResults.phase3 = {
                success: true,
                stats: statsResponse.data.stats
            };
            
            console.log('✅ Phase 3 테스트 완료');
            return true;
            
        } catch (error) {
            console.error('❌ Phase 3 테스트 실패:', error.message);
            this.testResults.phase3.success = false;
            return false;
        }
    }

    /**
     * 전체 시스템 테스트
     */
    async testOverallSystem() {
        try {
            console.log('\n🎯 전체 시스템 테스트 시작...');
            
            // 1. 전체 시스템 상태 확인
            const systemStatus = await this.checkSystemStatus();
            if (!systemStatus) {
                throw new Error('전체 시스템 상태 확인 실패');
            }
            
            // 2. 전체 시스템 통계 조회
            const statsResponse = await axios.get(`${API_BASE}/system/stats`);
            console.log('✅ 전체 시스템 통계 조회 완료');
            
            const systemStats = statsResponse.data.systemStats;
            console.log('📊 전체 시스템 통계:');
            console.log(`   총 탐지 수: ${systemStats.summary.totalDetections}`);
            console.log(`   전체 정확도: ${(systemStats.summary.overallAccuracy * 100).toFixed(1)}%`);
            console.log(`   시스템 신뢰성: ${(systemStats.summary.systemReliability * 100).toFixed(1)}%`);
            console.log(`   평균 처리 시간: ${systemStats.summary.averageProcessingTime.toFixed(1)}ms`);
            
            this.testResults.overall = {
                success: true,
                stats: systemStats
            };
            
            console.log('✅ 전체 시스템 테스트 완료');
            return true;
            
        } catch (error) {
            console.error('❌ 전체 시스템 테스트 실패:', error.message);
            this.testResults.overall.success = false;
            return false;
        }
    }

    /**
     * 전체 테스트 실행
     */
    async runAllTests() {
        console.log('🚀 완전한 AI 시스템 전체 테스트 시작');
        console.log('=' * 60);
        
        // 1. 서버 상태 확인
        const serverOk = await this.checkServerStatus();
        if (!serverOk) {
            console.log('❌ 서버 연결 실패로 테스트 중단');
            return;
        }
        
        // 2. Phase 1 테스트
        const phase1Ok = await this.testPhase1();
        
        // 3. Phase 2 테스트
        const phase2Ok = await this.testPhase2();
        
        // 4. Phase 3 테스트
        const phase3Ok = await this.testPhase3();
        
        // 5. 전체 시스템 테스트
        const overallOk = await this.testOverallSystem();
        
        // 6. 테스트 결과 요약
        console.log('\n🎉 전체 테스트 완료');
        console.log('=' * 60);
        console.log(`✅ 서버 연결: ${serverOk ? '성공' : '실패'}`);
        console.log(`✅ Phase 1: ${phase1Ok ? '성공' : '실패'}`);
        console.log(`✅ Phase 2: ${phase2Ok ? '성공' : '실패'}`);
        console.log(`✅ Phase 3: ${phase3Ok ? '성공' : '실패'}`);
        console.log(`✅ 전체 시스템: ${overallOk ? '성공' : '실패'}`);
        
        // 7. 성능 요약
        if (this.testResults.overall.success) {
            const stats = this.testResults.overall.stats.summary;
            console.log('\n📊 최종 성능 요약:');
            console.log(`   정확도: ${(stats.overallAccuracy * 100).toFixed(1)}%`);
            console.log(`   신뢰성: ${(stats.systemReliability * 100).toFixed(1)}%`);
            console.log(`   처리 시간: ${stats.averageProcessingTime.toFixed(1)}ms`);
            console.log(`   총 탐지 수: ${stats.totalDetections}`);
        }
        
        console.log('\n🎯 완전한 AI 시스템이 성공적으로 구현되었습니다!');
        console.log('=' * 60);
        
        return this.testResults;
    }
}

// 테스트 실행
if (require.main === module) {
    const tester = new CompleteSystemTester();
    tester.runAllTests().catch(console.error);
}

module.exports = CompleteSystemTester;
