const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = 3000;

// 미들웨어 설정
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'static')));

// 메인 페이지
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'static', 'showcase.html'));
});

// 라벨링 인터페이스
app.get('/labeling', (req, res) => {
    res.sendFile(path.join(__dirname, 'static', 'human_labeling_interface.html'));
});

// 관리자 대시보드
app.get('/admin', (req, res) => {
    res.sendFile(path.join(__dirname, 'static', 'admin_dashboard.html'));
});

// 라벨링 데이터 저장 API (메모리 저장)
let labelingData = [];

app.post('/api/labeling/save', (req, res) => {
    const { fileName, label, confidence, notes, labelerId, aiSuggestion } = req.body;
    
    const labelData = {
        id: Date.now(),
        fileName,
        label,
        confidence,
        notes,
        labelerId,
        aiSuggestion: aiSuggestion || null,
        timestamp: new Date().toISOString()
    };
    
    labelingData.push(labelData);
    
    console.log('라벨링 데이터 저장:', labelData);
    res.json({ success: true, data: labelData });
});

// 라벨링 데이터 조회 API
app.get('/api/labeling/data', (req, res) => {
    res.json({ success: true, data: labelingData });
});

// 라벨링 통계 API
app.get('/api/labeling/stats', (req, res) => {
    const stats = {
        total: labelingData.length,
        ready: labelingData.filter(d => !d.label).length,
        labeled: labelingData.filter(d => d.label).length,
        normal: labelingData.filter(d => d.label === 'normal').length,
        warning: labelingData.filter(d => d.label === 'warning').length,
        critical: labelingData.filter(d => d.label === 'critical').length,
        unknown: labelingData.filter(d => d.label === 'unknown').length
    };
    
    res.json({ success: true, stats });
});

// 파일 업로드 API
const multer = require('multer');
const path = require('path');

// 업로드 설정
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'data/real_audio_uploads/');
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
});

const upload = multer({ 
    storage: storage,
    limits: {
        fileSize: 10 * 1024 * 1024 // 10MB 제한
    },
    fileFilter: function (req, file, cb) {
        if (file.mimetype.startsWith('audio/')) {
            cb(null, true);
        } else {
            cb(new Error('오디오 파일만 업로드 가능합니다.'), false);
        }
    }
});

app.post('/api/labeling/upload', upload.single('audio'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({
                success: false,
                message: '오디오 파일이 필요합니다.'
            });
        }

        const { fileName, suggestedLabel, fileSize, createdTime, status } = req.body;
        
        const labelData = {
            id: Date.now(),
            fileName: fileName || req.file.originalname,
            filePath: req.file.path,
            fileSize: parseInt(fileSize) || req.file.size,
            suggestedLabel: suggestedLabel || 'unknown',
            status: status || 'ready_for_labeling',
            createdTime: createdTime || new Date().toISOString(),
            uploadedTime: new Date().toISOString()
        };
        
        labelingData.push(labelData);
        
        console.log('파일 업로드 완료:', labelData);
        res.json({ 
            success: true, 
            data: labelData,
            message: '파일이 성공적으로 업로드되었습니다.'
        });
        
    } catch (error) {
        console.error('파일 업로드 오류:', error);
        res.status(500).json({
            success: false,
            message: '파일 업로드 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 오디오 파일 서빙 API
app.get('/api/audio/:filename', (req, res) => {
    const filename = req.params.filename;
    const filePath = path.join(__dirname, 'data/real_audio_uploads', filename);
    
    // 파일 존재 확인
    const fs = require('fs');
    if (!fs.existsSync(filePath)) {
        return res.status(404).json({
            success: false,
            message: '오디오 파일을 찾을 수 없습니다.'
        });
    }
    
    // 오디오 파일 스트리밍
    res.sendFile(filePath);
});

// 서버 시작
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 라벨링 서버가 http://localhost:${PORT} 에서 실행 중입니다`);
    console.log(`📊 라벨링 인터페이스: http://localhost:${PORT}/labeling`);
    console.log(`👨‍💼 관리자 대시보드: http://localhost:${PORT}/admin`);
    console.log(`📁 정적 파일: static/ 폴더`);
});

// 에러 처리
process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});
