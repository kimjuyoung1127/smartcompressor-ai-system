// ESP32 압축기 작동 히트맵 시각화 모듈
class CompressorHeatmap {
    constructor(canvasId) {
        this.canvasId = canvasId;
        this.ctx = null;
        this.data = null;
    }

    // 히트맵 데이터 로드
    async loadHeatmapData(deviceId, startDate, endDate) {
        try {
            const url = `/api/esp32/analytics/heatmap?device_id=${deviceId}&start_date=${startDate}&end_date=${endDate}&granularity=hour`;
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`API 요청 실패: ${response.status}`);
            }

            const result = await response.json();
            if (!result.success) {
                throw new Error(result.message || '히트맵 데이터 조회 실패');
            }

            this.data = result.data;
            return result.data;

        } catch (error) {
            console.error('[CompressorHeatmap] 데이터 로드 실패:', error);
            throw error;
        }
    }

    // 히트맵 렌더링
    render() {
        if (!this.data || this.data.length === 0) {
            console.warn('[CompressorHeatmap] 렌더링할 데이터가 없습니다');
            return;
        }

        const canvas = document.getElementById(this.canvasId);
        if (!canvas) {
            console.error('[CompressorHeatmap] 캔버스를 찾을 수 없습니다:', this.canvasId);
            return;
        }

        this.ctx = canvas.getContext('2d');
        
        // 캔버스 크기 설정
        const padding = { top: 50, right: 20, bottom: 50, left: 80 };
        const cellWidth = 30;
        const cellHeight = 30;
        const hours = 24;
        const days = this.data.length;

        canvas.width = padding.left + (hours * cellWidth) + padding.right;
        canvas.height = padding.top + (days * cellHeight) + padding.bottom;

        // 배경 지우기
        this.ctx.clearRect(0, 0, canvas.width, canvas.height);
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, canvas.width, canvas.height);

        // 최대값 찾기
        let maxValue = 0;
        this.data.forEach(day => {
            Object.keys(day.hours).forEach(hour => {
                maxValue = Math.max(maxValue, day.hours[hour]);
            });
        });

        // 히트맵 그리기
        this.data.forEach((day, dayIndex) => {
            for (let hour = 0; hour < hours; hour++) {
                const value = day.hours[hour] || 0;
                const color = this.getColorForValue(value, maxValue);
                
                const x = padding.left + (hour * cellWidth);
                const y = padding.top + (dayIndex * cellHeight);

                // 셀 그리기
                this.ctx.fillStyle = color;
                this.ctx.fillRect(x, y, cellWidth - 1, cellHeight - 1);

                // 값 표시 (선택적)
                if (cellWidth > 25) {
                    this.ctx.fillStyle = value > 50 ? '#ffffff' : '#333333';
                    this.ctx.font = '10px Arial';
                    this.ctx.textAlign = 'center';
                    this.ctx.textBaseline = 'middle';
                    this.ctx.fillText(
                        Math.round(value) + '%',
                        x + cellWidth / 2,
                        y + cellHeight / 2
                    );
                }
            }
        });

        // Y축 레이블 (날짜)
        this.ctx.fillStyle = '#333333';
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'right';
        this.ctx.textBaseline = 'middle';
        this.data.forEach((day, dayIndex) => {
            const y = padding.top + (dayIndex * cellHeight) + cellHeight / 2;
            const dateLabel = new Date(day.date).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
            this.ctx.fillText(dateLabel, padding.left - 10, y);
        });

        // X축 레이블 (시간)
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'top';
        for (let hour = 0; hour < hours; hour += 6) { // 6시간 간격
            const x = padding.left + (hour * cellWidth) + cellWidth / 2;
            this.ctx.fillText(hour + '시', x, padding.top + (days * cellHeight) + 5);
        }

        // 제목
        this.ctx.font = 'bold 14px Arial';
        this.ctx.textAlign = 'left';
        this.ctx.fillStyle = '#2c3e50';
        this.ctx.fillText('시간대별 압축기 작동률(%)', 10, 25);
    }

    // 값을 색상으로 변환 (0% = 파랑, 50% = 노랑, 100% = 빨강)
    getColorForValue(value, maxValue) {
        const ratio = Math.min(value / 100, 1); // 0~1로 정규화
        
        if (ratio <= 0.5) {
            // 파랑 -> 노랑
            const r = Math.round(52 + (243 - 52) * (ratio * 2));
            const g = Math.round(152 + (156 - 152) * (ratio * 2));
            const b = Math.round(219);
            return `rgb(${r}, ${g}, ${b})`;
        } else {
            // 노랑 -> 빨강
            const r = Math.round(243 + (231 - 243) * ((ratio - 0.5) * 2));
            const g = Math.round(156 + (76 - 156) * ((ratio - 0.5) * 2));
            const b = Math.round(42 + (60 - 42) * ((ratio - 0.5) * 2));
            return `rgb(${r}, ${g}, ${b})`;
        }
    }

    // 데이터 최신화 및 재렌더링
    async update(deviceId, startDate, endDate) {
        await this.loadHeatmapData(deviceId, startDate, endDate);
        this.render();
    }
}

// 전역으로 노출
window.CompressorHeatmap = CompressorHeatmap;
