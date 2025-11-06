const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const cors = require('cors');

const app = express();
const PORT = 3000;

// 미들웨어 설정
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'static')));

// 디렉토리 생성
const uploadDir = path.join(__dirname, 'data', 'real_audio_uploads');
const augmentedDir = path.join(__dirname, 'data', 'augmented_audio');
const labelingDir = path.join(__dirname, 'data', 'labeling_ready');

[uploadDir, augmentedDir, labelingDir].forEach(dir => {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
});

// Multer 설정
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const originalName = file.originalname.replace(/\.[^/.]+$/, '');
        cb(null, `real_${timestamp}_${originalName}.wav`);
    }
});

const upload = multer({
    storage: storage,
    fileFilter: (req, file, cb) => {
        const allowedTypes = ['audio/wav', 'audio/mp3', 'audio/m4a', 'audio/ogg'];
        if (allowedTypes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error('오디오 파일만 업로드 가능합니다.'), false);
        }
    },
    limits: { fileSize: 50 * 1024 * 1024 }
});

// 라벨링 데이터 저장소 (메모리)
let labelingData = [];

// 메인 페이지
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'static', 'integrated_interface.html'));
});

// 라벨링 인터페이스
app.get('/labeling', (req, res) => {
    res.sendFile(path.join(__dirname, 'static', 'human_labeling_interface.html'));
});

// 데이터 업로드 페이지
app.get('/upload', (req, res) => {
    res.sendFile(path.join(__dirname, 'static', 'data_upload_interface.html'));
});

// 관리자 대시보드
app.get('/admin', (req, res) => {
    res.sendFile(path.join(__dirname, 'static', 'admin_dashboard.html'));
});

// 오디오 파일 업로드 API
app.post('/api/upload/audio', upload.single('audioFile'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ success: false, message: '파일이 선택되지 않았습니다.' });
        }

        const fileInfo = {
            id: Date.now(),
            originalName: req.file.originalname,
            fileName: req.file.filename,
            filePath: req.file.path,
            fileSize: req.file.size,
            uploadTime: new Date().toISOString(),
            status: 'uploaded'
        };

        console.log('오디오 파일 업로드 완료:', fileInfo);
        res.json({ success: true, data: fileInfo });

    } catch (error) {
        console.error('업로드 오류:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 업로드된 파일 목록 조회
app.get('/api/upload/files', (req, res) => {
    try {
        const files = fs.readdirSync(uploadDir)
            .filter(file => file.endsWith('.wav') || file.endsWith('.mp3') || file.endsWith('.m4a') || file.endsWith('.ogg'))
            .map(file => {
                const filePath = path.join(uploadDir, file);
                const stats = fs.statSync(filePath);
                return {
                    fileName: file,
                    fileSize: stats.size,
                    uploadTime: stats.birthtime.toISOString(),
                    filePath: filePath
                };
            })
            .sort((a, b) => new Date(b.uploadTime) - new Date(a.uploadTime));

        res.json({ success: true, files });
    } catch (error) {
        console.error('파일 목록 조회 오류:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 데이터 증강 API (고품질 합성 기반)
app.post('/api/augment/:fileName', async (req, res) => {
    try {
        const { fileName } = req.params;
        const { augmentCount = 20, label = 'unknown', segmentDuration = 3, qualityLevel = 'high' } = req.body;
        
        const sourceFile = path.join(uploadDir, fileName);
        if (!fs.existsSync(sourceFile)) {
            return res.status(404).json({ success: false, message: '파일을 찾을 수 없습니다.' });
        }

        console.log(`고품질 데이터 증강 시작: ${fileName} -> ${augmentCount}개 (${segmentDuration}초, 품질: ${qualityLevel})`);

        const augmentedFiles = [];
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        
        // Python 고품질 합성 엔진 호출
        const { spawn } = require('child_process');
        
        // Python 스크립트 실행
        const pythonProcess = spawn('python', [
            'ai/advanced_audio_synthesis.py',
            '--input', sourceFile,
            '--output-dir', augmentedDir,
            '--count', augmentCount.toString(),
            '--duration', segmentDuration.toString(),
            '--quality', qualityLevel,
            '--label', label
        ]);
        
        let pythonOutput = '';
        let pythonError = '';
        
        pythonProcess.stdout.on('data', (data) => {
            pythonOutput += data.toString();
            console.log(`Python: ${data.toString().trim()}`);
        });
        
        pythonProcess.stderr.on('data', (data) => {
            pythonError += data.toString();
            console.error(`Python Error: ${data.toString().trim()}`);
        });
        
        pythonProcess.on('close', (code) => {
            if (code === 0) {
                // Python 성공 - 생성된 파일들 처리
                processAugmentedFiles();
            } else {
                console.error(`Python 프로세스 실패: ${code}`);
                // 폴백: 기존 세그먼트 방식 사용
                fallbackToSegmentAugmentation();
            }
        });
        
        function processAugmentedFiles() {
            try {
                // 생성된 파일들 찾기
                const augmentedFilesList = fs.readdirSync(augmentedDir)
                    .filter(file => file.includes(timestamp) && file.endsWith('.wav'));
                
                console.log(`고품질 합성 완료: ${augmentedFilesList.length}개 파일 생성`);
                
                // 라벨링 시스템으로 전송
                for (let i = 0; i < augmentedFilesList.length; i++) {
                    const augmentedFileName = augmentedFilesList[i];
                    const augmentedFilePath = path.join(augmentedDir, augmentedFileName);
                    
                    // 라벨링용 파일로 복사
                    const labelingFileName = `labeling_${label}_${timestamp}_${i + 1}.wav`;
                    const labelingFilePath = path.join(labelingDir, labelingFileName);
                    fs.copyFileSync(augmentedFilePath, labelingFilePath);
                    
                    // 라벨링 데이터에 추가
                    const labelingItem = {
                        id: Date.now() + i,
                        fileName: labelingFileName,
                        originalFileName: fileName,
                        filePath: labelingFilePath,
                        fileSize: fs.statSync(augmentedFilePath).size,
                        label: label,
                        confidence: 0,
                        notes: '',
                        labelerId: 'system',
                        status: 'ready_for_labeling',
                        createdTime: new Date().toISOString(),
                        augmentedFrom: fileName,
                        synthesisInfo: {
                            qualityLevel: qualityLevel,
                            method: 'advanced_synthesis',
                            segmentIndex: i + 1
                        }
                    };
                    
                    labelingData.push(labelingItem);
                    augmentedFiles.push({
                        fileName: augmentedFileName,
                        labelingFileName: labelingFileName,
                        filePath: augmentedFilePath,
                        originalFile: fileName,
                        augmentationType: 'advanced_synthesis',
                        qualityLevel: qualityLevel,
                        segmentIndex: i + 1,
                        createdTime: new Date().toISOString()
                    });
                    
                    console.log(`고품질 합성 완료 (${i + 1}/${augmentedFilesList.length}): ${augmentedFileName} -> 라벨링 준비 완료`);
                }
                
                res.json({ 
                    success: true, 
                    message: `${augmentedFiles.length}개의 고품질 합성음이 생성되고 라벨링 시스템으로 전송되었습니다.`,
                    augmentedFiles: augmentedFiles,
                    labelingReady: augmentedFiles.length,
                    synthesisInfo: {
                        qualityLevel: qualityLevel,
                        method: 'advanced_synthesis',
                        totalSamples: augmentedFiles.length
                    }
                });
                
            } catch (error) {
                console.error('고품질 합성 후처리 오류:', error);
                fallbackToSegmentAugmentation();
            }
        }
        
        function fallbackToSegmentAugmentation() {
            console.log('폴백: 기존 세그먼트 방식 사용');
            // 기존 세그먼트 방식 코드...
            performSegmentAugmentation();
        }
        
        function performSegmentAugmentation() {
            // 기존 세그먼트 증강 코드 (fallback)
            const originalData = fs.readFileSync(sourceFile);
            const fileSize = originalData.length;
        
        // WAV 파일 헤더 분석 및 검증
        if (fileSize < 44) {
            throw new Error('파일이 너무 작습니다. 유효한 WAV 파일이 아닙니다.');
        }
        
        // WAV 헤더 검증
        const riffHeader = originalData.toString('ascii', 0, 4);
        const waveHeader = originalData.toString('ascii', 8, 12);
        
        if (riffHeader !== 'RIFF' || waveHeader !== 'WAVE') {
            throw new Error('유효한 WAV 파일이 아닙니다.');
        }
        
        // WAV 헤더에서 실제 정보 추출
        const fileSizeFromHeader = originalData.readUInt32LE(4);
        const fmtChunkSize = originalData.readUInt32LE(16);
        const audioFormat = originalData.readUInt16LE(20);
        const numChannels = originalData.readUInt16LE(22);
        const sampleRate = originalData.readUInt32LE(24);
        const byteRate = originalData.readUInt32LE(28);
        const blockAlign = originalData.readUInt16LE(32);
        const bitsPerSample = originalData.readUInt16LE(34);
        
        console.log(`WAV 정보: ${numChannels}채널, ${sampleRate}Hz, ${bitsPerSample}bit`);
        
        // 데이터 청크 찾기 (더 견고한 방법)
        let dataOffset = 36 + fmtChunkSize;
        let dataSize = 0;
        let audioDataStart = 0;
        
        // 여러 위치에서 데이터 청크 찾기 시도
        const searchPositions = [
            36 + fmtChunkSize,  // 표준 위치
            44,                 // 간단한 WAV 파일
            36,                 // fmt 청크가 16바이트인 경우
            fileSize - 8        // 파일 끝에서 역방향 검색
        ];
        
        for (const startPos of searchPositions) {
            if (startPos >= fileSize - 8) continue;
            
            let offset = startPos;
            while (offset < fileSize - 8) {
                const chunkId = originalData.toString('ascii', offset, offset + 4);
                const chunkSize = originalData.readUInt32LE(offset + 4);
                
                if (chunkId === 'data' && chunkSize > 0 && offset + 8 + chunkSize <= fileSize) {
                    dataOffset = offset;
                    dataSize = chunkSize;
                    audioDataStart = offset + 8;
                    break;
                }
                
                // 다음 청크로 이동
                offset += 8 + chunkSize;
                if (offset % 2 !== 0) offset++; // 2바이트 정렬
            }
            
            if (dataSize > 0) break;
        }
        
        // 여전히 찾지 못한 경우, 파일 끝에서 추정
        if (dataSize === 0) {
            console.log('데이터 청크를 찾지 못했습니다. 파일 끝에서 추정합니다.');
            audioDataStart = 44; // 표준 WAV 헤더 크기
            dataSize = fileSize - audioDataStart;
            dataOffset = 36;
        }
        
        const audioDataLength = Math.min(dataSize, fileSize - audioDataStart);
        
        console.log(`데이터 청크 정보: offset=${dataOffset}, size=${dataSize}, audioStart=${audioDataStart}, audioLength=${audioDataLength}`);
        
        // 세그먼트 계산
        const bytesPerSecond = byteRate;
        const segmentBytes = segmentDuration * bytesPerSecond;
        const totalDuration = audioDataLength / bytesPerSecond;
        const maxSegments = Math.floor(totalDuration / segmentDuration);
        
        console.log(`원본 파일 길이: ${totalDuration.toFixed(2)}초, 최대 세그먼트: ${maxSegments}개`);
        
        // 최소 세그먼트 길이 확인
        if (segmentBytes > audioDataLength) {
            throw new Error(`요청된 세그먼트 길이(${segmentDuration}초)가 파일 길이(${totalDuration.toFixed(2)}초)보다 깁니다.`);
        }
        
        // 실제 생성할 세그먼트 수 (요청된 수와 가능한 수 중 작은 값)
        const actualCount = Math.min(augmentCount, maxSegments);
        
        if (actualCount === 0) {
            throw new Error('파일이 너무 짧아서 세그먼트를 생성할 수 없습니다.');
        }
        
        for (let i = 0; i < actualCount; i++) {
            try {
                // 세그먼트 시작 위치 계산 (랜덤하게)
                const maxStartPosition = Math.max(0, audioDataLength - segmentBytes);
                const startPosition = Math.floor(Math.random() * maxStartPosition);
                const endPosition = Math.min(startPosition + segmentBytes, audioDataLength);
                
                // 세그먼트 데이터 추출
                const segmentData = originalData.slice(audioDataStart + startPosition, audioDataStart + endPosition);
                
                // 새로운 WAV 파일 생성
                const newDataSize = segmentData.length;
                const newFileSize = 36 + newDataSize;
                const newWavData = Buffer.alloc(44 + newDataSize);
                
                // RIFF 헤더
                newWavData.write('RIFF', 0);
                newWavData.writeUInt32LE(newFileSize, 4);
                newWavData.write('WAVE', 8);
                
                // fmt 청크
                newWavData.write('fmt ', 12);
                newWavData.writeUInt32LE(16, 16); // fmt 청크 크기
                newWavData.writeUInt16LE(audioFormat, 20);
                newWavData.writeUInt16LE(numChannels, 22);
                newWavData.writeUInt32LE(sampleRate, 24);
                newWavData.writeUInt32LE(byteRate, 28);
                newWavData.writeUInt16LE(blockAlign, 32);
                newWavData.writeUInt16LE(bitsPerSample, 34);
                
                // data 청크
                newWavData.write('data', 36);
                newWavData.writeUInt32LE(newDataSize, 40);
                
                // 오디오 데이터 추가
                segmentData.copy(newWavData, 44);
                
                // 증강 파일명 생성
                const augmentedFileName = `${label}_segment_${timestamp}_${i + 1}.wav`;
                const augmentedFilePath = path.join(augmentedDir, augmentedFileName);
                
                // 증강 파일 저장
                fs.writeFileSync(augmentedFilePath, newWavData);
                
                // 라벨링용 파일로 복사
                const labelingFileName = `labeling_${label}_${timestamp}_${i + 1}.wav`;
                const labelingFilePath = path.join(labelingDir, labelingFileName);
                fs.writeFileSync(labelingFilePath, newWavData);
                
                // 라벨링 데이터에 추가
                const labelingItem = {
                    id: Date.now() + i,
                    fileName: labelingFileName,
                    originalFileName: fileName,
                    filePath: labelingFilePath,
                    fileSize: newWavData.length,
                    label: label,
                    confidence: 0,
                    notes: '',
                    labelerId: 'system',
                    status: 'ready_for_labeling',
                    createdTime: new Date().toISOString(),
                    augmentedFrom: fileName,
                    segmentInfo: {
                        duration: segmentDuration,
                        startTime: (startPosition / bytesPerSecond).toFixed(2),
                        endTime: (endPosition / bytesPerSecond).toFixed(2),
                        segmentIndex: i + 1
                    }
                };
                
                labelingData.push(labelingItem);
                augmentedFiles.push({
                    fileName: augmentedFileName,
                    labelingFileName: labelingFileName,
                    filePath: augmentedFilePath,
                    originalFile: fileName,
                    augmentationType: 'segment_based',
                    segmentDuration: segmentDuration,
                    segmentIndex: i + 1,
                    createdTime: new Date().toISOString()
                });
                
                console.log(`세그먼트 증강 완료 (${i + 1}/${actualCount}): ${augmentedFileName} (${segmentDuration}초) -> 라벨링 준비 완료`);
                
            } catch (error) {
                console.error(`세그먼트 증강 실패 (${i + 1}/${actualCount}):`, error);
                continue;
            }
        }

        console.log(`세그먼트 증강 완료: ${augmentedFiles.length}/${actualCount}개 파일 생성 및 라벨링 준비 완료`);
        
        res.json({ 
            success: true, 
            message: `${augmentedFiles.length}개의 ${segmentDuration}초 세그먼트가 생성되고 라벨링 시스템으로 전송되었습니다.`,
            augmentedFiles: augmentedFiles,
            labelingReady: augmentedFiles.length,
            segmentInfo: {
                segmentDuration: segmentDuration,
                totalSegments: actualCount,
                originalDuration: totalDuration.toFixed(2)
            }
        });

    } catch (error) {
        console.error('데이터 증강 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '데이터 증강 실패: ' + error.message
        });
    }
});

// 라벨링 데이터 조회 API
app.get('/api/labeling/data', (req, res) => {
    try {
        // 라벨링 디렉토리의 파일들도 포함
        const labelingFiles = fs.readdirSync(labelingDir)
            .filter(file => file.endsWith('.wav'))
            .map(file => {
                const filePath = path.join(labelingDir, file);
                const stats = fs.statSync(filePath);
                return {
                    fileName: file,
                    filePath: filePath,
                    fileSize: stats.size,
                    createdTime: stats.birthtime.toISOString(),
                    status: 'ready_for_labeling'
                };
            })
            .sort((a, b) => new Date(b.createdTime) - new Date(a.createdTime));

        res.json({ 
            success: true, 
            data: labelingData,
            files: labelingFiles,
            total: labelingData.length
        });
    } catch (error) {
        console.error('라벨링 데이터 조회 오류:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 라벨링 데이터 저장 API
app.post('/api/labeling/save', (req, res) => {
    const { fileName, label, confidence, notes, labelerId } = req.body;
    
    const labelData = {
        id: Date.now(),
        fileName,
        label,
        confidence: parseInt(confidence) || 0,
        notes: notes || '',
        labelerId: labelerId || 'unknown',
        timestamp: new Date().toISOString(),
        status: 'labeled'
    };
    
    // 기존 데이터 업데이트 또는 새로 추가
    const existingIndex = labelingData.findIndex(item => item.fileName === fileName);
    if (existingIndex >= 0) {
        labelingData[existingIndex] = { ...labelingData[existingIndex], ...labelData };
    } else {
        labelingData.push(labelData);
    }
    
    console.log('라벨링 데이터 저장:', labelData);
    res.json({ success: true, data: labelData });
});

// 라벨링 통계 API
app.get('/api/labeling/stats', (req, res) => {
    const stats = {
        total: labelingData.length,
        normal: labelingData.filter(d => d.label === 'normal').length,
        warning: labelingData.filter(d => d.label === 'warning').length,
        critical: labelingData.filter(d => d.label === 'critical').length,
        unknown: labelingData.filter(d => d.label === 'unknown').length,
        labeled: labelingData.filter(d => d.status === 'labeled').length,
        ready: labelingData.filter(d => d.status === 'ready_for_labeling').length
    };
    
    res.json({ success: true, stats });
});

// 증강된 파일 목록 조회
app.get('/api/augment/files', (req, res) => {
    try {
        const files = fs.readdirSync(augmentedDir)
            .filter(file => file.endsWith('.wav'))
            .map(file => {
                const filePath = path.join(augmentedDir, file);
                const stats = fs.statSync(filePath);
                return {
                    fileName: file,
                    fileSize: stats.size,
                    createdTime: stats.birthtime.toISOString(),
                    filePath: filePath
                };
            })
            .sort((a, b) => new Date(b.createdTime) - new Date(a.createdTime));

        res.json({ success: true, files });
    } catch (error) {
        console.error('증강 파일 목록 조회 오류:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 파일 삭제 API
app.delete('/api/upload/:fileName', (req, res) => {
    try {
        const { fileName } = req.params;
        const filePath = path.join(uploadDir, fileName);
        
        if (fs.existsSync(filePath)) {
            fs.unlinkSync(filePath);
            console.log('파일 삭제 완료:', fileName);
            res.json({ success: true, message: '파일이 삭제되었습니다.' });
        } else {
            res.status(404).json({ success: false, message: '파일을 찾을 수 없습니다.' });
        }
    } catch (error) {
        console.error('파일 삭제 오류:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 오디오 파일 서빙 API
app.get('/api/audio/:fileName', (req, res) => {
    try {
        const fileName = decodeURIComponent(req.params.fileName);
        const filePath = path.join(labelingDir, fileName);
        
        if (fs.existsSync(filePath)) {
            res.sendFile(filePath);
        } else {
            res.status(404).json({ success: false, message: '오디오 파일을 찾을 수 없습니다.' });
        }
    } catch (error) {
        console.error('오디오 파일 서빙 오류:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 통계 API
app.get('/api/stats', (req, res) => {
    try {
        const uploadedFiles = fs.readdirSync(uploadDir)
            .filter(file => file.endsWith('.wav') || file.endsWith('.mp3') || file.endsWith('.m4a') || file.endsWith('.ogg'));
        
        const augmentedFiles = fs.readdirSync(augmentedDir)
            .filter(file => file.endsWith('.wav'));
        
        const labelingFiles = fs.readdirSync(labelingDir)
            .filter(file => file.endsWith('.wav'));
        
        const totalUploadSize = uploadedFiles.reduce((sum, file) => {
            const filePath = path.join(uploadDir, file);
            const stats = fs.statSync(filePath);
            return sum + stats.size;
        }, 0);
        
        const totalAugmentedSize = augmentedFiles.reduce((sum, file) => {
            const filePath = path.join(augmentedDir, file);
            const stats = fs.statSync(filePath);
            return sum + stats.size;
        }, 0);
        
        res.json({
            success: true,
            stats: {
                uploadedFiles: uploadedFiles.length,
                augmentedFiles: augmentedFiles.length,
                labelingFiles: labelingFiles.length,
                totalUploadSize: totalUploadSize,
                totalAugmentedSize: totalAugmentedSize,
                totalSize: totalUploadSize + totalAugmentedSize,
                labelingData: labelingData.length
            }
        });
    } catch (error) {
        console.error('통계 조회 오류:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 서버 시작
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 통합 서버가 http://localhost:${PORT} 에서 실행 중입니다`);
    console.log(`📊 데이터 업로드: http://localhost:${PORT}/upload`);
    console.log(`🏷️ 라벨링 인터페이스: http://localhost:${PORT}/labeling`);
    console.log(`👨‍💼 관리자 대시보드: http://localhost:${PORT}/admin`);
    console.log(`📁 업로드 디렉토리: ${uploadDir}`);
    console.log(`🔄 증강 데이터 디렉토리: ${augmentedDir}`);
    console.log(`🏷️ 라벨링 준비 디렉토리: ${labelingDir}`);
});

// 에러 처리
process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});
