// ESP32 기간 비교 뷰 모듈
class ComparisonView {
    constructor() {
        this.period1Data = null;
        this.period2Data = null;
    }

    // 비교 데이터 로드
    async loadComparisonData(period1Range, period2Range, deviceId) {
        try {
            const [period1, period2] = await Promise.all([
                this.fetchPeriodData(period1Range, deviceId),
                this.fetchPeriodData(period2Range, deviceId)
            ]);

            this.period1Data = period1;
            this.period2Data = period2;

            return {
                period1: period1,
                period2: period2
            };

        } catch (error) {
            console.error('[ComparisonView] 비교 데이터 로드 실패:', error);
            throw error;
        }
    }

    // 특정 기간 데이터 조회
    async fetchPeriodData(dateRange, deviceId) {
        const url = `/api/esp32/analytics/date-range?start_date=${dateRange.startDate}&end_date=${dateRange.endDate}&device_id=${deviceId}`;
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`API 요청 실패: ${response.status}`);
        }

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.message || '데이터 조회 실패');
        }

        return result.data;
    }

    // 비교 통계 계산
    calculateStats(data) {
        if (!data || data.length === 0) {
            return null;
        }

        const onCount = data.filter(item => {
            const decibelLevel = item.decibel_level !== undefined 
                ? item.decibel_level 
                : 20 * Math.log10(item.rms_energy || 1);
            return decibelLevel >= 45;
        }).length;

        const stats = {
            total_points: data.length,
            operation_ratio: (onCount / data.length) * 100,
            avg_rms: data.reduce((sum, item) => sum + (item.rms_energy || 0), 0) / data.length,
            avg_decibel: data.reduce((sum, item) => {
                const db = item.decibel_level !== undefined 
                    ? item.decibel_level 
                    : 20 * Math.log10(item.rms_energy || 1);
                return sum + db;
            }, 0) / data.length,
            avg_anomaly_score: data.reduce((sum, item) => sum + (item.anomaly_score || 0), 0) / data.length,
            avg_efficiency: data.reduce((sum, item) => sum + (item.efficiency_score || 0), 0) / data.length,
            on_count: onCount,
            off_count: data.length - onCount
        };

        return stats;
    }

    // 차이 계산
    calculateDifferences(stats1, stats2) {
        if (!stats1 || !stats2) return null;

        return {
            operation_ratio_diff: stats2.operation_ratio - stats1.operation_ratio,
            avg_rms_diff: stats2.avg_rms - stats1.avg_rms,
            avg_decibel_diff: stats2.avg_decibel - stats1.avg_decibel,
            avg_anomaly_diff: stats2.avg_anomaly_score - stats1.avg_anomaly_score,
            avg_efficiency_diff: stats2.avg_efficiency - stats1.avg_efficiency,
            total_points_diff: stats2.total_points - stats1.total_points
        };
    }

    // 비교 UI 렌더링
    renderComparisonStats(period1Label, period2Label, stats1, stats2, differences) {
        // 기간 1 통계
        document.getElementById('period1Label').textContent = period1Label;
        document.getElementById('period1Stats').innerHTML = this.formatStats(stats1);

        // 기간 2 통계
        document.getElementById('period2Label').textContent = period2Label;
        document.getElementById('period2Stats').innerHTML = this.formatStats(stats2);

        // 차이 표시
        if (differences) {
            document.getElementById('statDiff').innerHTML = this.formatDifferences(differences);
        }
    }

    // 통계 포맷
    formatStats(stats) {
        if (!stats) return '<div class="alert alert-warning">데이터 없음</div>';

        return `
            <div class="stat-item-compare">
                <span class="stat-label-compare">작동 비율:</span>
                <span class="stat-value-compare">${stats.operation_ratio.toFixed(1)}%</span>
            </div>
            <div class="stat-item-compare">
                <span class="stat-label-compare">평균 RMS:</span>
                <span class="stat-value-compare">${stats.avg_rms.toFixed(2)}</span>
            </div>
            <div class="stat-item-compare">
                <span class="stat-label-compare">평균 데시벨:</span>
                <span class="stat-value-compare">${stats.avg_decibel.toFixed(1)} dB</span>
            </div>
            <div class="stat-item-compare">
                <span class="stat-label-compare">이상 점수:</span>
                <span class="stat-value-compare">${stats.avg_anomaly_score.toFixed(3)}</span>
            </div>
            <div class="stat-item-compare">
                <span class="stat-label-compare">효율성:</span>
                <span class="stat-value-compare">${stats.avg_efficiency.toFixed(3)}</span>
            </div>
            <div class="stat-item-compare">
                <span class="stat-label-compare">ON 횟수:</span>
                <span class="stat-value-compare">${stats.on_count}</span>
            </div>
            <div class="stat-item-compare">
                <span class="stat-label-compare">OFF 횟수:</span>
                <span class="stat-value-compare">${stats.off_count}</span>
            </div>
            <div class="stat-item-compare">
                <span class="stat-label-compare">총 포인트:</span>
                <span class="stat-value-compare">${stats.total_points}</span>
            </div>
        `;
    }

    // 차이 포맷
    formatDifferences(diffs) {
        if (!diffs) return '';

        const formatDiff = (value, label, unit = '') => {
            if (value === 0) {
                return `<div class="stat-diff-neutral"><span>${label}:</span> 0${unit}</div>`;
            }
            const isPositive = value > 0;
            const sign = isPositive ? '+' : '';
            const className = isPositive ? 'positive' : 'negative';
            return `<div class="stat-diff-${className}"><span>${label}:</span> ${sign}${value.toFixed(2)}${unit}</div>`;
        };

        return `
            ${formatDiff(diffs.operation_ratio_diff, '작동 비율', '%')}
            ${formatDiff(diffs.avg_rms_diff, '평균 RMS', '')}
            ${formatDiff(diffs.avg_decibel_diff, '평균 데시벨', ' dB')}
            ${formatDiff(diffs.avg_anomaly_diff, '이상 점수', '')}
            ${formatDiff(diffs.avg_efficiency_diff, '효율성', '')}
            ${formatDiff(diffs.total_points_diff, '데이터 포인트', '')}
        `;
    }
}

// 전역으로 노출
window.ComparisonView = ComparisonView;
