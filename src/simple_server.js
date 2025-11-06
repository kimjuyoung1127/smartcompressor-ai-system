const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// 미들웨어 설정
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// 정적 파일 서빙
app.use('/static', express.static(path.join(__dirname, 'static')));
app.use(express.static(path.join(__dirname, 'static')));

// 메인 페이지 (쇼윈도 - 로그인 화면)
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'static/showcase.html'));
});

// 소리 라벨링 도구 페이지
app.get('/labeling', (req, res) => {
    res.sendFile(path.join(__dirname, 'static/sound_labeling_tool.html'));
});

// 소리 데이터 관리자 페이지
app.get('/sound-manager', (req, res) => {
    res.sendFile(path.join(__dirname, 'static/sound_data_manager.html'));
});

// 실제 소리 라벨링 도구 페이지
app.get('/real-labeling', (req, res) => {
    res.sendFile(path.join(__dirname, 'static/real_sound_labeling_tool.html'));
});

// 고품질 합성음 라벨링 도구 페이지
app.get('/high-quality-labeling', (req, res) => {
    res.sendFile(path.join(__dirname, 'static/high_quality_labeling_tool.html'));
});

// API 라우트들
app.get('/api/status', (req, res) => {
    res.json({
        status: 'running',
        message: '소리 데이터 라벨링 서버가 정상적으로 실행 중입니다.',
        timestamp: new Date().toISOString()
    });
});

// 라벨링 데이터 저장 API
app.post('/api/save-labeling', (req, res) => {
    try {
        const labelingData = req.body;
        
        // 간단한 파일 저장 (실제로는 데이터베이스 사용)
        const fs = require('fs');
        const dataDir = path.join(__dirname, 'data', 'labeling');
        
        // 디렉토리 생성
        if (!fs.existsSync(dataDir)) {
            fs.mkdirSync(dataDir, { recursive: true });
        }
        
        // 파일 저장
        const filename = `labeling_${new Date().toISOString().split('T')[0]}.json`;
        const filepath = path.join(dataDir, filename);
        
        // 기존 데이터 로드
        let existingData = [];
        if (fs.existsSync(filepath)) {
            const fileContent = fs.readFileSync(filepath, 'utf8');
            existingData = JSON.parse(fileContent);
        }
        
        // 새 데이터 추가
        existingData.push({
            ...labelingData,
            timestamp: new Date().toISOString()
        });
        
        // 파일 저장
        fs.writeFileSync(filepath, JSON.stringify(existingData, null, 2), 'utf8');
        
        res.json({
            success: true,
            message: '라벨링 데이터가 저장되었습니다.',
            filename: filename
        });
        
    } catch (error) {
        console.error('라벨링 데이터 저장 오류:', error);
        res.status(500).json({
            success: false,
            message: '라벨링 데이터 저장 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 라벨링 데이터 조회 API
app.get('/api/get-labeling', (req, res) => {
    try {
        const fs = require('fs');
        const dataDir = path.join(__dirname, 'data', 'labeling');
        
        if (!fs.existsSync(dataDir)) {
            return res.json([]);
        }
        
        // 모든 라벨링 파일 조회
        const files = fs.readdirSync(dataDir).filter(file => file.endsWith('.json'));
        let allData = [];
        
        files.forEach(file => {
            const filepath = path.join(dataDir, file);
            const fileContent = fs.readFileSync(filepath, 'utf8');
            const data = JSON.parse(fileContent);
            allData = allData.concat(data);
        });
        
        res.json(allData);
        
    } catch (error) {
        console.error('라벨링 데이터 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '라벨링 데이터 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 소리 데이터 조회 API
app.get('/api/get-sound-data', (req, res) => {
    try {
        const fs = require('fs');
        const dataPath = path.join(__dirname, 'data', 'sound_samples', 'labeling_data.json');
        
        if (fs.existsSync(dataPath)) {
            const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
            res.json(data);
        } else {
            // 기본 데이터 반환
            res.json({
                synthetic_sounds: [],
                downloaded_sounds: [],
                total_files: 0,
                categories: ['normal_compressor', 'normal_fan', 'normal_motor', 'abnormal_bearing', 'abnormal_unbalance', 'abnormal_friction', 'abnormal_overload']
            });
        }
    } catch (error) {
        console.error('소리 데이터 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '소리 데이터 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 소리 파일 서빙 API
app.get('/api/sound-file/:filename', (req, res) => {
    try {
        const filename = req.params.filename;
        const fs = require('fs');
        
        // 합성 소리 파일 경로들
        const possiblePaths = [
            path.join(__dirname, 'data', 'synthetic_sounds', 'normal_compressor', filename),
            path.join(__dirname, 'data', 'synthetic_sounds', 'normal_fan', filename),
            path.join(__dirname, 'data', 'synthetic_sounds', 'normal_motor', filename),
            path.join(__dirname, 'data', 'synthetic_sounds', 'abnormal_bearing', filename),
            path.join(__dirname, 'data', 'synthetic_sounds', 'abnormal_unbalance', filename),
            path.join(__dirname, 'data', 'synthetic_sounds', 'abnormal_friction', filename),
            path.join(__dirname, 'data', 'synthetic_sounds', 'abnormal_overload', filename),
            path.join(__dirname, 'data', 'downloaded_sounds', 'normal_compressor', filename),
            path.join(__dirname, 'data', 'downloaded_sounds', 'normal_fan', filename),
            path.join(__dirname, 'data', 'downloaded_sounds', 'normal_motor', filename),
            path.join(__dirname, 'data', 'downloaded_sounds', 'abnormal_bearing', filename),
            path.join(__dirname, 'data', 'downloaded_sounds', 'abnormal_unbalance', filename),
            path.join(__dirname, 'data', 'downloaded_sounds', 'abnormal_friction', filename),
            path.join(__dirname, 'data', 'downloaded_sounds', 'abnormal_overload', filename)
        ];
        
        let filePath = null;
        for (const possiblePath of possiblePaths) {
            if (fs.existsSync(possiblePath)) {
                filePath = possiblePath;
                break;
            }
        }
        
        if (filePath) {
            res.sendFile(filePath);
        } else {
            res.status(404).json({
                success: false,
                message: '소리 파일을 찾을 수 없습니다.',
                filename: filename
            });
        }
    } catch (error) {
        console.error('소리 파일 서빙 오류:', error);
        res.status(500).json({
            success: false,
            message: '소리 파일 서빙 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 소리 데이터 생성 API
app.post('/api/generate-sound-data', (req, res) => {
    try {
        // 소리 데이터 생성 시스템 실행
        const { spawn } = require('child_process');
        const generator = spawn('node', [path.join(__dirname, 'ai', 'sound_data_generator.js')]);
        
        generator.on('close', (code) => {
            if (code === 0) {
                res.json({
                    success: true,
                    message: '새로운 소리 데이터가 생성되었습니다.'
                });
            } else {
                res.status(500).json({
                    success: false,
                    message: '소리 데이터 생성 중 오류가 발생했습니다.'
                });
            }
        });
        
        generator.on('error', (error) => {
            console.error('소리 데이터 생성 오류:', error);
            res.status(500).json({
                success: false,
                message: '소리 데이터 생성 중 오류가 발생했습니다.',
                error: error.message
            });
        });
        
    } catch (error) {
        console.error('소리 데이터 생성 API 오류:', error);
        res.status(500).json({
            success: false,
            message: '소리 데이터 생성 API 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 고급 데이터 관리 API들
const AdvancedDataManager = require('./ai/advanced_data_manager');
let dataManager = null;

// 데이터 관리자 초기화
(async () => {
    dataManager = new AdvancedDataManager();
    await dataManager.initialize();
})();

// 라벨링 세션 저장 API
app.post('/api/save-labeling-session', async (req, res) => {
    try {
        if (!dataManager) {
            dataManager = new AdvancedDataManager();
            await dataManager.initialize();
        }
        
        const session = await dataManager.addLabelingSession(req.body);
        
        res.json({
            success: true,
            message: '라벨링 세션이 저장되었습니다.',
            session_id: session.id,
            filename: `session_${session.id}.json`
        });
    } catch (error) {
        console.error('라벨링 세션 저장 오류:', error);
        res.status(500).json({
            success: false,
            message: '라벨링 세션 저장 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// AI 훈련용 데이터 생성 API
app.post('/api/generate-ai-training-data', async (req, res) => {
    try {
        if (!dataManager) {
            dataManager = new AdvancedDataManager();
            await dataManager.initialize();
        }
        
        const trainingData = await dataManager.exportForAITraining();
        
        res.json({
            success: true,
            message: 'AI 훈련용 데이터가 생성되었습니다.',
            filename: `ai_training_data_${new Date().toISOString().split('T')[0]}.json`,
            data: trainingData
        });
    } catch (error) {
        console.error('AI 훈련 데이터 생성 오류:', error);
        res.status(500).json({
            success: false,
            message: 'AI 훈련 데이터 생성 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 라벨링 보고서 생성 API
app.post('/api/generate-labeling-report', async (req, res) => {
    try {
        if (!dataManager) {
            dataManager = new AdvancedDataManager();
            await dataManager.initialize();
        }
        
        const report = await dataManager.generateReport();
        
        res.json({
            success: true,
            message: '라벨링 보고서가 생성되었습니다.',
            filename: `labeling_report_${new Date().toISOString().split('T')[0]}.json`,
            report: report
        });
    } catch (error) {
        console.error('라벨링 보고서 생성 오류:', error);
        res.status(500).json({
            success: false,
            message: '라벨링 보고서 생성 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 데이터 통계 조회 API
app.get('/api/get-labeling-stats', async (req, res) => {
    try {
        if (!dataManager) {
            dataManager = new AdvancedDataManager();
            await dataManager.initialize();
        }
        
        res.json({
            success: true,
            statistics: dataManager.dataStructure.statistics,
            engineer_info: dataManager.dataStructure.engineer_info
        });
    } catch (error) {
        console.error('데이터 통계 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '데이터 통계 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 실제 소리 데이터 조회 API
app.get('/api/get-real-sound-data', (req, res) => {
    try {
        const fs = require('fs');
        const dataPath = path.join(__dirname, 'data', 'real_sounds', 'labeling_data.json');
        
        if (fs.existsSync(dataPath)) {
            const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
            res.json(data);
        } else {
            // 기본 데이터 반환
            res.json({
                real_sounds: [],
                total_files: 0,
                categories: ['normal_compressor', 'normal_fan', 'normal_motor', 'abnormal_bearing', 'abnormal_unbalance', 'abnormal_friction', 'abnormal_overload']
            });
        }
    } catch (error) {
        console.error('실제 소리 데이터 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '실제 소리 데이터 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 실제 소리 파일 서빙 API
app.get('/api/real-sound-file/:filename', (req, res) => {
    try {
        const filename = req.params.filename;
        const fs = require('fs');
        
        // 실제 소리 파일 경로들
        const possiblePaths = [
            path.join(__dirname, 'data', 'real_sounds', 'normal_compressor', filename),
            path.join(__dirname, 'data', 'real_sounds', 'normal_fan', filename),
            path.join(__dirname, 'data', 'real_sounds', 'normal_motor', filename),
            path.join(__dirname, 'data', 'real_sounds', 'abnormal_bearing', filename),
            path.join(__dirname, 'data', 'real_sounds', 'abnormal_unbalance', filename),
            path.join(__dirname, 'data', 'real_sounds', 'abnormal_friction', filename),
            path.join(__dirname, 'data', 'real_sounds', 'abnormal_overload', filename)
        ];
        
        let filePath = null;
        for (const possiblePath of possiblePaths) {
            if (fs.existsSync(possiblePath)) {
                filePath = possiblePath;
                break;
            }
        }
        
        if (filePath) {
            res.sendFile(filePath);
        } else {
            res.status(404).json({
                success: false,
                message: '실제 소리 파일을 찾을 수 없습니다.',
                filename: filename
            });
        }
    } catch (error) {
        console.error('실제 소리 파일 서빙 오류:', error);
        res.status(500).json({
            success: false,
            message: '실제 소리 파일 서빙 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 실제 소리 라벨링 데이터 저장 API
app.post('/api/save-real-sound-labeling', (req, res) => {
    try {
        const labelingData = req.body;
        const fs = require('fs');
        const dataDir = path.join(__dirname, 'data', 'real_sound_labeling');
        
        // 디렉토리 생성
        if (!fs.existsSync(dataDir)) {
            fs.mkdirSync(dataDir, { recursive: true });
        }
        
        // 파일 저장
        const filename = `real_sound_labeling_${new Date().toISOString().split('T')[0]}.json`;
        const filepath = path.join(dataDir, filename);
        
        fs.writeFileSync(filepath, JSON.stringify(labelingData, null, 2), 'utf8');
        
        res.json({
            success: true,
            message: '실제 소리 라벨링 데이터가 저장되었습니다.',
            filename: filename
        });
        
    } catch (error) {
        console.error('실제 소리 라벨링 데이터 저장 오류:', error);
        res.status(500).json({
            success: false,
            message: '실제 소리 라벨링 데이터 저장 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 고품질 합성음 데이터 조회 API
app.get('/api/get-high-quality-sound-data', (req, res) => {
    try {
        const fs = require('fs');
        const dataPath = path.join(__dirname, 'data', 'high_quality_sounds', 'labeling_data.json');
        
        if (fs.existsSync(dataPath)) {
            const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
            res.json(data);
        } else {
            // 기본 데이터 반환
            res.json({
                high_quality_sounds: [],
                total_files: 0,
                categories: ['normal_compressor', 'normal_fan', 'normal_motor', 'abnormal_bearing', 'abnormal_unbalance', 'abnormal_friction', 'abnormal_overload']
            });
        }
    } catch (error) {
        console.error('고품질 합성음 데이터 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '고품질 합성음 데이터 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 고품질 합성음 파일 서빙 API
app.get('/api/high-quality-sound-file/:filename', (req, res) => {
    try {
        const filename = req.params.filename;
        const fs = require('fs');
        
        // 고품질 합성음 파일 경로들
        const possiblePaths = [
            path.join(__dirname, 'data', 'high_quality_sounds', 'normal_compressor', filename),
            path.join(__dirname, 'data', 'high_quality_sounds', 'normal_fan', filename),
            path.join(__dirname, 'data', 'high_quality_sounds', 'normal_motor', filename),
            path.join(__dirname, 'data', 'high_quality_sounds', 'abnormal_bearing', filename),
            path.join(__dirname, 'data', 'high_quality_sounds', 'abnormal_unbalance', filename),
            path.join(__dirname, 'data', 'high_quality_sounds', 'abnormal_friction', filename),
            path.join(__dirname, 'data', 'high_quality_sounds', 'abnormal_overload', filename)
        ];
        
        let filePath = null;
        for (const possiblePath of possiblePaths) {
            if (fs.existsSync(possiblePath)) {
                filePath = possiblePath;
                break;
            }
        }
        
        if (filePath) {
            res.sendFile(filePath);
        } else {
            res.status(404).json({
                success: false,
                message: '고품질 합성음 파일을 찾을 수 없습니다.',
                filename: filename
            });
        }
    } catch (error) {
        console.error('고품질 합성음 파일 서빙 오류:', error);
        res.status(500).json({
            success: false,
            message: '고품질 합성음 파일 서빙 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 고품질 합성음 라벨링 데이터 저장 API
app.post('/api/save-high-quality-labeling', (req, res) => {
    try {
        const labelingData = req.body;
        const fs = require('fs');
        const dataDir = path.join(__dirname, 'data', 'high_quality_labeling');
        
        // 디렉토리 생성
        if (!fs.existsSync(dataDir)) {
            fs.mkdirSync(dataDir, { recursive: true });
        }
        
        // 파일 저장
        const filename = `high_quality_labeling_${new Date().toISOString().split('T')[0]}.json`;
        const filepath = path.join(dataDir, filename);
        
        fs.writeFileSync(filepath, JSON.stringify(labelingData, null, 2), 'utf8');
        
        res.json({
            success: true,
            message: '고품질 합성음 라벨링 데이터가 저장되었습니다.',
            filename: filename
        });
        
    } catch (error) {
        console.error('고품질 합성음 라벨링 데이터 저장 오류:', error);
        res.status(500).json({
            success: false,
            message: '고품질 합성음 라벨링 데이터 저장 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// AI 진단 API (간단한 버전)
app.post('/api/diagnose', (req, res) => {
    try {
        const { audioData, features } = req.body;
        
        // 간단한 진단 로직 (실제로는 훈련된 AI 모델 사용)
        const diagnosis = {
            prediction: 'normal_compressor', // 기본값
            confidence: 0.85,
            features: features || [],
            timestamp: new Date().toISOString(),
            model_version: '1.0.0'
        };
        
        // 간단한 규칙 기반 진단
        if (features && features.length > 0) {
            const mean = features[0] || 0;
            const std = features[1] || 0;
            const max = features[2] || 0;
            
            if (std > 0.5) {
                diagnosis.prediction = 'abnormal_bearing';
                diagnosis.confidence = 0.9;
            } else if (max > 0.8) {
                diagnosis.prediction = 'abnormal_overload';
                diagnosis.confidence = 0.95;
            } else if (mean > 0.3) {
                diagnosis.prediction = 'normal_compressor';
                diagnosis.confidence = 0.8;
            }
        }
        
        res.json({
            success: true,
            diagnosis: diagnosis
        });
        
    } catch (error) {
        console.error('AI 진단 오류:', error);
        res.status(500).json({
            success: false,
            message: 'AI 진단 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 404 처리
app.use((req, res) => {
    res.status(404).json({
        error: 'Not Found',
        message: '요청한 페이지를 찾을 수 없습니다.',
        path: req.path
    });
});

// 에러 처리
app.use((err, req, res, next) => {
    console.error('서버 오류:', err);
    res.status(500).json({
        error: 'Internal Server Error',
        message: '서버 내부 오류가 발생했습니다.',
        timestamp: new Date().toISOString()
    });
});

// 서버 시작
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 소리 데이터 라벨링 서버가 http://0.0.0.0:${PORT} 에서 실행 중입니다`);
    console.log(`🌐 외부 접근: http://localhost:${PORT}`);
    console.log(`🎵 소리 라벨링 도구: http://localhost:${PORT}/labeling`);
    console.log(`📁 정적 파일 서빙: static/ 폴더`);
    console.log(`🔗 API 엔드포인트: /api/*`);
    console.log(`⏰ 시작 시간: ${new Date().toISOString()}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    process.exit(0);
});
