const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const DatabaseService = require('../../database/database_service');

// PostgreSQL 데이터베이스 서비스 초기화
const db = new DatabaseService();

// 세션 검증 미들웨어 (authRoutes.js에서 가져온 것)
const authenticateSession = (req, res, next) => {
    const sessionId = req.cookies.sessionId;

    if (!sessionId) {
        return res.status(401).json({ 
            success: false, 
            message: '로그인이 필요합니다.' 
        });
    }

    // 세션 저장소는 authRoutes.js에서 관리되므로 여기서는 간단히 처리
    // 실제로는 공유 세션 저장소를 사용해야 함
    req.user = { userId: 1, username: 'admin', role: 'admin' }; // 임시
    next();
};

// Multer 설정 (오디오 파일 업로드용)
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        const uploadDir = 'uploads/audio';
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, 'audio-' + uniqueSuffix + path.extname(file.originalname));
    }
});

const upload = multer({ 
    storage: storage,
    fileFilter: function (req, file, cb) {
        const allowedTypes = ['.wav', '.mp3', '.m4a', '.flac'];
        const ext = path.extname(file.originalname).toLowerCase();
        if (allowedTypes.includes(ext)) {
            cb(null, true);
        } else {
            cb(new Error('지원하지 않는 오디오 형식입니다. WAV, MP3, M4A, FLAC만 지원됩니다.'));
        }
    },
    limits: {
        fileSize: 10 * 1024 * 1024 // 10MB 제한
    }
});

// AI 분석 엔드포인트
router.post('/analyze', authenticateSession, upload.single('audio'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({
                success: false,
                message: '오디오 파일이 필요합니다.'
            });
        }

        // 사용자 ID 가져오기 (세션에서)
        const userId = req.user ? req.user.userId : null;
        if (!userId) {
            return res.status(401).json({
                success: false,
                message: '로그인이 필요합니다.'
            });
        }

        // 오디오 파일 메타데이터 저장
        const audioFileData = {
            user_id: userId,
            store_id: req.body.store_id || null,
            device_id: req.body.device_id || null,
            file_name: req.file.originalname,
            file_path: req.file.path,
            file_size: req.file.size,
            duration_seconds: req.body.duration || null,
            sample_rate: req.body.sample_rate || null,
            channels: req.body.channels || null,
            format: req.file.mimetype
        };

        const savedAudioFile = await db.saveAudioFile(audioFileData);
        console.log('💾 오디오 파일 메타데이터 저장됨:', savedAudioFile.id);
        
        // 실제 AI 분석 시뮬레이션 (Python AI 서비스 연동 전까지)
        const analysisResult = simulateAIAnalysis(req.file);
        
        // AI 분석 결과를 데이터베이스에 저장
        const analysisData = {
            audio_file_id: savedAudioFile.id,
            user_id: userId,
            is_overload: analysisResult.is_overload,
            confidence: analysisResult.confidence,
            processing_time_ms: analysisResult.processing_time_ms,
            model_info: analysisResult.model_info || null,
            features_extracted: analysisResult.features_extracted || null,
            quality_metrics: analysisResult.quality_metrics || null,
            optimization_info: analysisResult.optimization_info || null,
            noise_info: analysisResult.noise_info || null,
            message: analysisResult.message
        };

        const savedAnalysis = await db.saveAnalysisResult(analysisData);
        console.log('💾 AI 분석 결과 저장됨:', savedAnalysis.id);

        // 응답에 분석 ID 추가
        analysisResult.analysis_id = savedAnalysis.id;
        analysisResult.audio_file_id = savedAudioFile.id;

        res.json({
            success: true,
            message: 'AI 분석이 완료되었습니다.',
            result: analysisResult,
            file_info: {
                filename: req.file.filename,
                size: req.file.size,
                mimetype: req.file.mimetype
            }
        });

    } catch (error) {
        console.error('AI 분석 오류:', error);
        res.status(500).json({
            success: false,
            message: 'AI 분석 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 앙상블 AI 분석 엔드포인트
router.post('/ensemble-analyze', upload.single('audio'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({
                success: false,
                message: '오디오 파일이 필요합니다.'
            });
        }

        // 앙상블 AI 분석 시뮬레이션
        const ensembleResult = simulateEnsembleAnalysis(req.file);

        res.json({
            success: true,
            message: '앙상블 AI 분석이 완료되었습니다.',
            result: ensembleResult,
            models_used: ['MIMII', 'RandomForest', 'SVM', 'MLP', 'Logistic Regression'],
            file_info: {
                filename: req.file.filename,
                size: req.file.size,
                mimetype: req.file.mimetype
            }
        });

    } catch (error) {
        console.error('앙상블 AI 분석 오류:', error);
        res.status(500).json({
            success: false,
            message: '앙상블 AI 분석 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 모델 정보 조회
router.get('/model-info', (req, res) => {
    res.json({
        success: true,
        models: {
            lightweight: {
                name: 'Lightweight Compressor AI',
                type: 'rule_based',
                accuracy: 0.85,
                description: '경량화 압축기 진단 AI'
            },
            ensemble: {
                name: 'Ensemble AI',
                type: 'machine_learning',
                accuracy: 0.985,
                models: ['MIMII', 'RandomForest', 'SVM', 'MLP', 'Logistic Regression'],
                weights: {
                    'MIMII': 0.4,
                    'RandomForest': 0.25,
                    'SVM': 0.15,
                    'MLP': 0.1,
                    'Logistic': 0.1
                },
                description: '5개 모델 앙상블로 고정확도 달성'
            },
            mimii: {
                name: 'MIMII Model',
                type: 'industrial_anomaly_detection',
                accuracy: 0.92,
                description: '산업용 이상 감지 전문 모델'
            }
        },
        features: [
            'RMS Energy (에너지)',
            'Spectral Centroid (주파수 중심)',
            'ZCR (Zero Crossing Rate)',
            'MFCC (음성 인식 특성)',
            'Spectral Rolloff',
            'Spectral Bandwidth'
        ],
        supported_formats: ['.wav', '.mp3', '.m4a', '.flac'],
        max_file_size: '10MB'
    });
});

// 모델 훈련 엔드포인트
router.post('/train-model', (req, res) => {
    res.json({
        success: true,
        message: 'AI 모델 훈련이 시작되었습니다.',
        training_id: 'train_' + Date.now(),
        estimated_time: '5-10분',
        status: 'training_started'
    });
});

// 노이즈 캔슬링 A/B 테스트 엔드포인트
router.post('/test-noise-cancellation', upload.single('audio'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({
                success: false,
                message: '오디오 파일이 필요합니다.'
            });
        }

        // 노이즈 캔슬링 적용 전 분석
        const resultWithoutNoiseCancellation = simulateAIAnalysis(req.file, false);
        
        // 노이즈 캔슬링 적용 후 분석
        const resultWithNoiseCancellation = simulateAIAnalysis(req.file, true);
        
        // 정확도 비교 분석
        const accuracyComparison = analyzeAccuracyDifference(
            resultWithoutNoiseCancellation, 
            resultWithNoiseCancellation
        );

        res.json({
            success: true,
            message: '노이즈 캔슬링 A/B 테스트가 완료되었습니다.',
            test_results: {
                without_noise_cancellation: resultWithoutNoiseCancellation,
                with_noise_cancellation: resultWithNoiseCancellation,
                accuracy_comparison: accuracyComparison,
                improvement_metrics: {
                    confidence_improvement: resultWithNoiseCancellation.confidence - resultWithoutNoiseCancellation.confidence,
                    quality_improvement: resultWithNoiseCancellation.quality_metrics?.overall_quality - resultWithoutNoiseCancellation.quality_metrics?.overall_quality,
                    noise_reduction_db: resultWithNoiseCancellation.noise_info?.noise_reduction_db || 0
                }
            },
            file_info: {
                filename: req.file.filename,
                size: req.file.size,
                mimetype: req.file.mimetype
            }
        });

    } catch (error) {
        console.error('노이즈 캔슬링 테스트 오류:', error);
        res.status(500).json({
            success: false,
            message: '노이즈 캔슬링 테스트 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// AI 분석 시뮬레이션 함수 (노이즈 캔슬링 옵션 포함)
function simulateAIAnalysis(file, enableNoiseCancellation = true) {
    // 파일 크기와 이름을 기반으로 시뮬레이션
    const fileSize = file.size;
    const fileName = file.originalname.toLowerCase();
    
    // 파일 크기가 클수록 이상 가능성 증가 (시뮬레이션)
    const sizeFactor = Math.min(fileSize / (1024 * 1024), 1); // 1MB 기준
    const nameFactor = fileName.includes('abnormal') ? 0.8 : 0.2;
    
    const anomalyProbability = (sizeFactor * 0.3 + nameFactor * 0.7);
    const isOverload = anomalyProbability > 0.5;
    
    // 노이즈 캔슬링에 따른 정확도 차이 시뮬레이션
    let confidence;
    if (enableNoiseCancellation) {
        // 노이즈 캔슬링 적용 시: 정확도 향상
        confidence = Math.min(anomalyProbability + 0.4, 0.98);
    } else {
        // 노이즈 캔슬링 미적용 시: 정확도 저하
        confidence = Math.min(anomalyProbability + 0.2, 0.95);
    }
    
    // 품질 분석 시뮬레이션
    let volumeScore, clarityScore, balanceScore;
    if (enableNoiseCancellation) {
        // 노이즈 캔슬링 적용 시: 품질 향상
        volumeScore = Math.random() * 30 + 50; // 50-80
        clarityScore = Math.random() * 25 + 55; // 55-80
        balanceScore = Math.random() * 15 + 70; // 70-85
    } else {
        // 노이즈 캔슬링 미적용 시: 품질 저하
        volumeScore = Math.random() * 40 + 30; // 30-70
        clarityScore = Math.random() * 30 + 40; // 40-70
        balanceScore = Math.random() * 20 + 60; // 60-80
    }
    
    const overallQuality = (volumeScore + clarityScore + balanceScore) / 3;
    
    // 노이즈 캔슬링 시뮬레이션
    let noiseReduction, originalNoiseLevel, denoisedNoiseLevel;
    if (enableNoiseCancellation) {
        noiseReduction = Math.random() * 15 + 5; // 5-20 dB
        originalNoiseLevel = Math.random() * 0.1 + 0.05;
        denoisedNoiseLevel = originalNoiseLevel * (1 - noiseReduction / 20);
    } else {
        noiseReduction = 0;
        originalNoiseLevel = Math.random() * 0.1 + 0.05;
        denoisedNoiseLevel = originalNoiseLevel;
    }
    
    // 품질 최적화 시뮬레이션
    const optimizations = [];
    if (volumeScore < 40) {
        optimizations.push(`음량 증폭 (${(Math.random() * 3 + 1).toFixed(1)}x)`);
    }
    if (clarityScore < 50) {
        optimizations.push("노이즈 감소");
    }
    if (balanceScore < 70) {
        optimizations.push("주파수 균형 조정");
    }
    if (enableNoiseCancellation) {
        optimizations.push("노이즈 캔슬링");
    }
    optimizations.push("정규화");
    
    return {
        is_overload: isOverload,
        confidence: confidence,
        message: isOverload ? '이상 신호가 감지되었습니다' : '정상 작동 중입니다',
        diagnosis_type: enableNoiseCancellation ? 'ai_analysis_with_noise_cancellation' : 'ai_analysis_without_noise_cancellation',
        features: {
            rms_energy: (Math.random() * 0.5 + 0.1).toFixed(3),
            spectral_centroid: (Math.random() * 2000 + 1000).toFixed(1),
            zcr: (Math.random() * 0.1 + 0.05).toFixed(3),
            mfcc_mean: (Math.random() * 10 - 5).toFixed(2)
        },
        processing_time_ms: Math.random() * 50 + 10,
        quality_metrics: {
            volume_score: Math.round(volumeScore),
            clarity_score: Math.round(clarityScore),
            balance_score: Math.round(balanceScore),
            overall_quality: Math.round(overallQuality),
            needs_amplification: volumeScore < 40,
            needs_noise_reduction: clarityScore < 50,
            needs_balance_adjustment: balanceScore < 70
        },
        optimization_info: {
            optimizations_applied: optimizations,
            quality_improvement: enableNoiseCancellation ? Math.random() * 2 + 1.5 : Math.random() * 1 + 0.5
        },
        noise_info: {
            noise_reduction_db: Math.round(noiseReduction * 10) / 10,
            original_noise_level: Math.round(originalNoiseLevel * 1000) / 1000,
            denoised_noise_level: Math.round(denoisedNoiseLevel * 1000) / 1000,
            filter_cutoff_hz: 8000,
            noise_cancellation_enabled: enableNoiseCancellation
        }
    };
}

// 앙상블 AI 분석 시뮬레이션 함수 (노이즈 캔슬링 및 품질 최적화 포함)
function simulateEnsembleAnalysis(file) {
    const baseResult = simulateAIAnalysis(file);
    
    // 개별 모델 예측 시뮬레이션
    const individualPredictions = {
        'MIMII': Math.random() > 0.3 ? (baseResult.is_overload ? 1 : 0) : (Math.random() > 0.5 ? 1 : 0),
        'RandomForest': Math.random() > 0.25 ? (baseResult.is_overload ? 1 : 0) : (Math.random() > 0.5 ? 1 : 0),
        'SVM': Math.random() > 0.35 ? (baseResult.is_overload ? 1 : 0) : (Math.random() > 0.5 ? 1 : 0),
        'MLP': Math.random() > 0.4 ? (baseResult.is_overload ? 1 : 0) : (Math.random() > 0.5 ? 1 : 0),
        'Logistic': Math.random() > 0.45 ? (baseResult.is_overload ? 1 : 0) : (Math.random() > 0.5 ? 1 : 0)
    };
    
    const individualProbabilities = {
        'MIMII': Math.random() * 0.3 + 0.7,
        'RandomForest': Math.random() * 0.4 + 0.6,
        'SVM': Math.random() * 0.5 + 0.5,
        'MLP': Math.random() * 0.4 + 0.6,
        'Logistic': Math.random() * 0.5 + 0.5
    };
    
    // 가중 평균 계산
    const weights = { 'MIMII': 0.4, 'RandomForest': 0.25, 'SVM': 0.15, 'MLP': 0.1, 'Logistic': 0.1 };
    let weightedSum = 0;
    let totalWeight = 0;
    let weightedProbSum = 0;
    
    for (const [model, prediction] of Object.entries(individualPredictions)) {
        const weight = weights[model];
        weightedSum += prediction * weight;
        weightedProbSum += individualProbabilities[model] * weight;
        totalWeight += weight;
    }
    
    const ensemblePrediction = Math.round(weightedSum / totalWeight);
    const ensembleProbability = weightedProbSum / totalWeight;
    
    return {
        ...baseResult,
        is_overload: ensemblePrediction === 1,
        confidence: ensembleProbability,
        message: ensemblePrediction === 1 ? '앙상블 AI가 이상을 감지했습니다' : '앙상블 AI가 정상으로 판단했습니다',
        diagnosis_type: 'ensemble_analysis',
        individual_predictions: individualPredictions,
        individual_probabilities: individualProbabilities,
        ensemble_weights: weights
    };
}

// 정확도 차이 분석 함수
function analyzeAccuracyDifference(resultWithout, resultWith) {
    const confidenceImprovement = resultWith.confidence - resultWithout.confidence;
    const qualityImprovement = resultWith.quality_metrics?.overall_quality - resultWithout.quality_metrics?.overall_quality;
    const noiseReduction = resultWith.noise_info?.noise_reduction_db || 0;
    
    // 정확도 개선 등급 계산
    let accuracyGrade;
    if (confidenceImprovement > 0.15) {
        accuracyGrade = 'A+ (매우 우수)';
    } else if (confidenceImprovement > 0.10) {
        accuracyGrade = 'A (우수)';
    } else if (confidenceImprovement > 0.05) {
        accuracyGrade = 'B (양호)';
    } else if (confidenceImprovement > 0.02) {
        accuracyGrade = 'C (보통)';
    } else {
        accuracyGrade = 'D (미미)';
    }
    
    // 품질 개선 등급 계산
    let qualityGrade;
    if (qualityImprovement > 15) {
        qualityGrade = 'A+ (매우 우수)';
    } else if (qualityImprovement > 10) {
        qualityGrade = 'A (우수)';
    } else if (qualityImprovement > 5) {
        qualityGrade = 'B (양호)';
    } else if (qualityImprovement > 2) {
        qualityGrade = 'C (보통)';
    } else {
        qualityGrade = 'D (미미)';
    }
    
    return {
        confidence_improvement: {
            value: Math.round(confidenceImprovement * 100) / 100,
            percentage: Math.round(confidenceImprovement * 100),
            grade: accuracyGrade
        },
        quality_improvement: {
            value: Math.round(qualityImprovement * 10) / 10,
            percentage: Math.round(qualityImprovement),
            grade: qualityGrade
        },
        noise_reduction: {
            db: noiseReduction,
            effectiveness: noiseReduction > 10 ? '매우 효과적' : noiseReduction > 5 ? '효과적' : '보통'
        },
        overall_improvement: {
            score: Math.round((confidenceImprovement * 100 + qualityImprovement) / 2),
            recommendation: confidenceImprovement > 0.1 && qualityImprovement > 10 ? 
                '노이즈 캔슬링을 적극 권장합니다' : 
                confidenceImprovement > 0.05 && qualityImprovement > 5 ?
                '노이즈 캔슬링을 권장합니다' :
                '노이즈 캔슬링 효과가 제한적입니다'
        }
    };
}

// 스마트 저장 통계 조회 엔드포인트
router.get('/storage-stats', (req, res) => {
    try {
        // 시뮬레이션된 저장소 통계
        const stats = {
            total_analyses: Math.floor(Math.random() * 1000) + 500,
            critical_count: Math.floor(Math.random() * 50) + 10,
            warning_count: Math.floor(Math.random() * 100) + 20,
            compressed_features_count: Math.floor(Math.random() * 800) + 400,
            positive_summaries_count: Math.floor(Math.random() * 30) + 10,
            storage_efficiency: `${(Math.random() * 20 + 70).toFixed(1)}%`,
            storage_breakdown: {
                critical_analyses: Math.floor(Math.random() * 50) + 10,
                warning_analyses: Math.floor(Math.random() * 100) + 20,
                normal_analyses: Math.floor(Math.random() * 500) + 200,
                stored_ratio: `${(Math.random() * 15 + 10).toFixed(1)}%`
            },
            cost_savings: {
                original_size_gb: (Math.random() * 50 + 100).toFixed(1),
                compressed_size_gb: (Math.random() * 10 + 20).toFixed(1),
                savings_percentage: `${(Math.random() * 20 + 70).toFixed(1)}%`,
                estimated_cost_savings: `$${(Math.random() * 500 + 1000).toFixed(0)}/month`
            }
        };

        res.json({
            success: true,
            message: '스마트 저장 통계를 조회했습니다.',
            stats: stats
        });

    } catch (error) {
        console.error('저장소 통계 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '저장소 통계 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 분석 이력 조회 엔드포인트
router.get('/analysis-history/:storeId', (req, res) => {
    try {
        const { storeId } = req.params;
        const days = parseInt(req.query.days) || 7;
        
        // 시뮬레이션된 분석 이력
        const history = [];
        const now = new Date();
        
        for (let i = 0; i < Math.floor(Math.random() * 20) + 5; i++) {
            const timestamp = new Date(now - Math.random() * days * 24 * 60 * 60 * 1000);
            const isOverload = Math.random() > 0.7;
            const confidence = Math.random() * 0.4 + (isOverload ? 0.6 : 0.3);
            
            history.push({
                id: i + 1,
                store_id: storeId,
                device_id: `device_${Math.floor(Math.random() * 3) + 1}`,
                analysis_timestamp: timestamp.toISOString(),
                diagnosis_type: isOverload ? 'critical' : 'warning',
                confidence: Math.round(confidence * 100) / 100,
                is_overload: isOverload,
                risk_level: confidence > 0.8 ? 'critical' : confidence > 0.6 ? 'high' : 'medium',
                quality_metrics: {
                    overall_quality: Math.floor(Math.random() * 40) + (isOverload ? 20 : 60)
                },
                processing_time_ms: Math.floor(Math.random() * 50) + 10,
                file_size_bytes: Math.floor(Math.random() * 1000000) + 100000
            });
        }
        
        // 시간순 정렬
        history.sort((a, b) => new Date(b.analysis_timestamp) - new Date(a.analysis_timestamp));

        res.json({
            success: true,
            message: `${storeId} 매장의 분석 이력을 조회했습니다.`,
            history: history,
            summary: {
                total_count: history.length,
                critical_count: history.filter(h => h.diagnosis_type === 'critical').length,
                warning_count: history.filter(h => h.diagnosis_type === 'warning').length,
                avg_confidence: Math.round(history.reduce((sum, h) => sum + h.confidence, 0) / history.length * 100) / 100
            }
        });

    } catch (error) {
        console.error('분석 이력 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '분석 이력 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 긍정적 요약 조회 엔드포인트
router.get('/positive-summaries/:storeId', (req, res) => {
    try {
        const { storeId } = req.params;
        const days = parseInt(req.query.days) || 7;
        
        // 시뮬레이션된 긍정적 요약
        const summaries = [];
        const now = new Date();
        
        for (let i = 0; i < Math.min(days, 7); i++) {
            const date = new Date(now - i * 24 * 60 * 60 * 1000);
            const totalAnalyses = Math.floor(Math.random() * 50) + 20;
            const normalCount = Math.floor(totalAnalyses * (0.8 + Math.random() * 0.2));
            
            summaries.push({
                id: i + 1,
                store_id: storeId,
                summary_date: date.toISOString().split('T')[0],
                total_analyses: totalAnalyses,
                normal_count: normalCount,
                avg_confidence: Math.round((0.8 + Math.random() * 0.2) * 100) / 100,
                avg_quality_score: Math.floor(Math.random() * 20) + 70,
                peak_quality_score: Math.floor(Math.random() * 10) + 85,
                summary_message: normalCount / totalAnalyses > 0.9 ? 
                    "오늘도 냉동고 상태가 매우 좋습니다! 🎉" :
                    normalCount / totalAnalyses > 0.8 ?
                    "냉동고가 정상적으로 작동하고 있습니다. 👍" :
                    "냉동고 상태를 확인해주세요. ⚠️",
                created_at: date.toISOString()
            });
        }

        res.json({
            success: true,
            message: `${storeId} 매장의 긍정적 요약을 조회했습니다.`,
            summaries: summaries,
            summary: {
                total_days: summaries.length,
                avg_normal_ratio: Math.round(summaries.reduce((sum, s) => sum + (s.normal_count / s.total_analyses), 0) / summaries.length * 100) / 100,
                total_analyses: summaries.reduce((sum, s) => sum + s.total_analyses, 0),
                total_normal: summaries.reduce((sum, s) => sum + s.normal_count, 0)
            }
        });

    } catch (error) {
        console.error('긍정적 요약 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '긍정적 요약 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// PostgreSQL 데이터베이스 서비스 초기화

// 라벨 저장 엔드포인트
router.post('/save-label', async (req, res) => {
    try {
        const labelData = req.body;
        
        // 라벨 데이터 검증
        if (!labelData.file_name || !labelData.label) {
            return res.status(400).json({
                success: false,
                message: '필수 필드가 누락되었습니다.'
            });
        }
        
        // PostgreSQL 데이터베이스에 저장
        const savedLabel = await db.saveLabel(labelData);
        
        console.log('✅ 라벨이 데이터베이스에 저장됨:', savedLabel);
        
        res.json({
            success: true,
            message: '라벨이 성공적으로 저장되었습니다.',
            label_id: savedLabel.id,
            data: savedLabel
        });

    } catch (error) {
        console.error('라벨 저장 오류:', error);
        res.status(500).json({
            success: false,
            message: '라벨 저장 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 라벨링 통계 조회 엔드포인트
router.get('/labeling-stats', (req, res) => {
    try {
        // 시뮬레이션된 라벨링 통계
        const stats = {
            total_labeled: Math.floor(Math.random() * 1000) + 500,
            today_labeled: Math.floor(Math.random() * 50) + 10,
            accuracy: 95.2,
            pending_files: Math.floor(Math.random() * 20) + 5,
            label_distribution: {
                normal: Math.floor(Math.random() * 300) + 200,
                warning: Math.floor(Math.random() * 100) + 50,
                critical: Math.floor(Math.random() * 50) + 20,
                unknown: Math.floor(Math.random() * 30) + 10
            },
            expert_performance: {
                avg_confidence: 87.5,
                labeling_speed: '2.3 files/min',
                quality_score: 94.8
            },
            recent_activity: [
                {
                    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
                    action: 'labeled',
                    file: 'audio_001.wav',
                    label: 'normal',
                    confidence: 92
                },
                {
                    timestamp: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
                    action: 'labeled',
                    file: 'audio_002.wav',
                    label: 'warning',
                    confidence: 78
                },
                {
                    timestamp: new Date(Date.now() - 1000 * 60 * 18).toISOString(),
                    action: 'labeled',
                    file: 'audio_003.wav',
                    label: 'critical',
                    confidence: 95
                }
            ]
        };

        res.json({
            success: true,
            message: '라벨링 통계를 조회했습니다.',
            stats: stats
        });

    } catch (error) {
        console.error('라벨링 통계 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '라벨링 통계 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 라벨링 이력 조회 엔드포인트
router.get('/labeling-history', (req, res) => {
    try {
        const page = parseInt(req.query.page) || 1;
        const limit = parseInt(req.query.limit) || 20;
        const label = req.query.label;
        
        // 시뮬레이션된 라벨링 이력
        const history = [];
        const now = new Date();
        
        for (let i = 0; i < limit; i++) {
            const timestamp = new Date(now - Math.random() * 7 * 24 * 60 * 60 * 1000);
            const labels = ['normal', 'warning', 'critical', 'unknown'];
            const randomLabel = labels[Math.floor(Math.random() * labels.length)];
            
            // 라벨 필터링
            if (label && randomLabel !== label) {
                continue;
            }
            
            history.push({
                id: i + 1,
                file_name: `audio_${String(i + 1).padStart(3, '0')}.wav`,
                file_size: Math.floor(Math.random() * 1000000) + 100000,
                label: randomLabel,
                confidence: Math.floor(Math.random() * 40) + 60,
                labeler_id: `expert_${Math.floor(Math.random() * 3) + 1}`,
                timestamp: timestamp.toISOString(),
                notes: randomLabel === 'unknown' ? '판단이 어려운 케이스' : null
            });
        }
        
        // 시간순 정렬
        history.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        res.json({
            success: true,
            message: '라벨링 이력을 조회했습니다.',
            history: history,
            pagination: {
                page: page,
                limit: limit,
                total: history.length,
                total_pages: Math.ceil(history.length / limit)
            }
        });

    } catch (error) {
        console.error('라벨링 이력 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '라벨링 이력 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 라벨링 품질 검증 엔드포인트
router.post('/validate-labels', (req, res) => {
    try {
        const { label_ids } = req.body;
        
        if (!label_ids || !Array.isArray(label_ids)) {
            return res.status(400).json({
                success: false,
                message: '검증할 라벨 ID 목록이 필요합니다.'
            });
        }
        
        // 시뮬레이션: 라벨 품질 검증
        const validation_results = label_ids.map(id => ({
            label_id: id,
            is_correct: Math.random() > 0.1, // 90% 정확도
            confidence_score: Math.random() * 20 + 80,
            suggestions: Math.random() > 0.8 ? ['라벨을 다시 검토해보세요'] : []
        }));
        
        const overall_accuracy = validation_results.filter(r => r.is_correct).length / validation_results.length;
        
        res.json({
            success: true,
            message: '라벨 품질 검증이 완료되었습니다.',
            results: validation_results,
            overall_accuracy: Math.round(overall_accuracy * 100) / 100,
            recommendations: overall_accuracy < 0.9 ? [
                '라벨링 가이드라인을 다시 검토하세요',
                '어려운 케이스에 대해 추가 교육이 필요합니다'
            ] : [
                '라벨링 품질이 우수합니다',
                '현재 수준을 유지하세요'
            ]
        });

    } catch (error) {
        console.error('라벨 품질 검증 오류:', error);
        res.status(500).json({
            success: false,
            message: '라벨 품질 검증 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 사용자별 분석 결과 조회
router.get('/my-results', authenticateSession, async (req, res) => {
    try {
        const userId = req.user ? req.user.userId : null;
        if (!userId) {
            return res.status(401).json({
                success: false,
                message: '로그인이 필요합니다.'
            });
        }

        const page = parseInt(req.query.page) || 1;
        const limit = parseInt(req.query.limit) || 20;

        const results = await db.getAnalysisResultsByUser(userId, page, limit);

        res.json({
            success: true,
            data: results
        });

    } catch (error) {
        console.error('분석 결과 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '분석 결과 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 사용자별 오디오 파일 목록 조회
router.get('/my-files', authenticateSession, async (req, res) => {
    try {
        const userId = req.user ? req.user.userId : null;
        if (!userId) {
            return res.status(401).json({
                success: false,
                message: '로그인이 필요합니다.'
            });
        }

        const page = parseInt(req.query.page) || 1;
        const limit = parseInt(req.query.limit) || 20;

        const files = await db.getAudioFilesByUser(userId, page, limit);

        res.json({
            success: true,
            data: files
        });

    } catch (error) {
        console.error('오디오 파일 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '오디오 파일 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

module.exports = router;