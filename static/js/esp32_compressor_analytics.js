// ESP32 압축기 작동 분석 모듈

const ESP32CompressorAnalytics = {
    // 시간대별 작동 비율 계산
    async calculateHourlyOperationRatio(deviceId = '', hours = 24, limit = 200) {
        try {
            const url = `/api/esp32/analytics/hourly?device_id=${deviceId}&hours=${hours}&limit=${limit}`;
            const response = await fetch(url);
            const result = await response.json();
            
            if (result.success) {
                return result.hourly_stats;
            } else {
                console.error('[Analytics] 시간대별 분석 실패:', result.error);
                return [];
            }
        } catch (error) {
            console.error('[Analytics] 시간대별 분석 오류:', error);
            return [];
        }
    },

    // 연속 작동/휴지 시간 분석
    async analyzeOperationCycles(deviceId = '', limit = 200) {
        try {
            const url = `/api/esp32/analytics/cycles?device_id=${deviceId}&limit=${limit}`;
            const response = await fetch(url);
            const result = await response.json();
            
            if (result.success) {
                return result;
            } else {
                console.error('[Analytics] 작동 주기 분석 실패:', result.error);
                return null;
            }
        } catch (error) {
            console.error('[Analytics] 작동 주기 분석 오류:', error);
            return null;
        }
    },

    // 작동 주기 패턴 분석
    analyzeOperationPatterns(data) {
        if (!Array.isArray(data) || data.length === 0) {
            return {
                avgDuration: 0,
                minDuration: 0,
                maxDuration: 0,
                cycleFrequency: 0,
                regularity: 0
            };
        }

        // 상태 판정
        const states = data.map(item => {
            const decibelLevel = item.decibel_level !== undefined 
                ? item.decibel_level 
                : 20 * Math.log10(item.rms_energy || 1);
            return {
                timestamp: item.timestamp,
                isOn: decibelLevel >= 45
            };
        });

        // 연속 상태 구간 식별
        const intervals = [];
        let currentState = states[0].isOn;
        let startTime = states[0].timestamp;
        
        for (let i = 1; i < states.length; i++) {
            if (states[i].isOn !== currentState) {
                intervals.push({
                    state: currentState ? 'on' : 'off',
                    duration: (states[i-1].timestamp - startTime) / 1000
                });
                currentState = states[i].isOn;
                startTime = states[i].timestamp;
            }
        }

        // 마지막 구간
        intervals.push({
            state: currentState ? 'on' : 'off',
            duration: (states[states.length - 1].timestamp - startTime) / 1000
        });

        // 통계 계산
        const onIntervals = intervals.filter(i => i.state === 'on');
        const durations = onIntervals.map(i => i.duration);
        
        const avgDuration = durations.length > 0 
            ? durations.reduce((sum, d) => sum + d, 0) / durations.length 
            : 0;
        const minDuration = durations.length > 0 ? Math.min(...durations) : 0;
        const maxDuration = durations.length > 0 ? Math.max(...durations) : 0;
        const totalTime = (data[data.length - 1].timestamp - data[0].timestamp) / 1000;
        const cycleFrequency = totalTime > 0 ? (intervals.length / 2) / (totalTime / 60) : 0; // 분당 주기
        
        // 규칙성 계산 (표준편차 기반)
        const variance = durations.length > 0
            ? durations.reduce((sum, d) => sum + Math.pow(d - avgDuration, 2), 0) / durations.length
            : 0;
        const standardDeviation = Math.sqrt(variance);
        const regularity = avgDuration > 0 
            ? Math.max(0, 100 - (standardDeviation / avgDuration * 100)) 
            : 0;

        return {
            avgDuration: avgDuration.toFixed(1),
            minDuration: minDuration.toFixed(1),
            maxDuration: maxDuration.toFixed(1),
            cycleFrequency: cycleFrequency.toFixed(2),
            regularity: regularity.toFixed(1)
        };
    },

    // 이상 패턴 감지
    async detectAnomalousPatterns(deviceId = '', limit = 200) {
        try {
            const url = `/api/esp32/analytics/anomalies?device_id=${deviceId}&limit=${limit}`;
            const response = await fetch(url);
            const result = await response.json();
            
            if (result.success) {
                return result.anomalies;
            } else {
                console.error('[Analytics] 이상 패턴 분석 실패:', result.error);
                return [];
            }
        } catch (error) {
            console.error('[Analytics] 이상 패턴 분석 오류:', error);
            return [];
        }
    },

    // 트렌드 분석
    calculateOperationTrend(hourlyStats) {
        if (!Array.isArray(hourlyStats) || hourlyStats.length < 2) {
            return {
                trend: 'unknown',
                direction: 0,
                volatility: 0
            };
        }

        // 트렌드 방향 계산
        const firstHalf = hourlyStats.slice(0, Math.floor(hourlyStats.length / 2));
        const secondHalf = hourlyStats.slice(Math.floor(hourlyStats.length / 2));
        
        const avgFirst = firstHalf.reduce((sum, h) => sum + parseFloat(h.on_ratio), 0) / firstHalf.length;
        const avgSecond = secondHalf.reduce((sum, h) => sum + parseFloat(h.on_ratio), 0) / secondHalf.length;
        
        const direction = avgSecond - avgFirst;
        let trend = 'stable';
        if (direction > 5) trend = 'increasing';
        if (direction < -5) trend = 'decreasing';

        // 변동성 계산
        const avgRatio = hourlyStats.reduce((sum, h) => sum + parseFloat(h.on_ratio), 0) / hourlyStats.length;
        const variance = hourlyStats.reduce((sum, h) => 
            sum + Math.pow(parseFloat(h.on_ratio) - avgRatio, 2), 0) / hourlyStats.length;
        const volatility = Math.sqrt(variance);

        return {
            trend: trend,
            direction: direction.toFixed(1),
            volatility: volatility.toFixed(1),
            avg_ratio: avgRatio.toFixed(1)
        };
    },

    // 작동 효율성 점수 계산 (0-100)
    calculateEfficiencyScore(onRatio, avgOnTime, avgOffTime) {
        // 작동 비율 기반 점수 (0-60점)
        let ratioScore = 0;
        if (onRatio >= 30 && onRatio <= 70) {
            ratioScore = 60; // 이상적 범위
        } else if (onRatio >= 20 && onRatio <= 80) {
            ratioScore = 40; // 허용 가능 범위
        } else if (onRatio >= 10 && onRatio <= 90) {
            ratioScore = 20; // 경계 범위
        }

        // 작동 주기 기반 점수 (0-40점)
        let cycleScore = 0;
        const totalCycleTime = avgOnTime + avgOffTime;
        if (totalCycleTime >= 300 && totalCycleTime <= 1800) {
            cycleScore = 40; // 이상적 주기 (5-30분)
        } else if (totalCycleTime >= 180 && totalCycleTime <= 3600) {
            cycleScore = 25; // 허용 가능 주기
        } else {
            cycleScore = 10; // 비이상적 주기
        }

        const totalScore = Math.min(100, ratioScore + cycleScore);
        return totalScore;
    }
};

// 전역 네임스페이스에 추가
window.ESP32CompressorAnalytics = ESP32CompressorAnalytics;
