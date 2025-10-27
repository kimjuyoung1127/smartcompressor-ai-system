// ESP32 시간 범위 선택 모듈
class TimeRangeSelector {
    constructor() {
        this.currentRange = 'today';
        this.callback = null;
        this.presets = {
            'today': { label: '오늘', hours: 24 },
            'yesterday': { label: '어제', days: 1, offset: 1 },
            'last7days': { label: '최근 7일', days: 7 },
            'last30days': { label: '최근 30일', days: 30 }
        };
    }

    // 프리셋에 따라 날짜 범위 계산
    getDateRange(preset) {
        const now = new Date();
        let startDate, endDate;

        switch (preset) {
            case 'today':
                startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                endDate = new Date(startDate.getTime() + 86400000 - 1);
                break;
            
            case 'yesterday':
                startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
                endDate = new Date(startDate.getTime() + 86400000 - 1);
                break;
            
            case 'last7days':
                startDate = new Date(now.getTime() - 7 * 86400000);
                endDate = new Date(now);
                break;
            
            case 'last30days':
                startDate = new Date(now.getTime() - 30 * 86400000);
                endDate = new Date(now);
                break;
            
            default:
                startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                endDate = new Date(startDate.getTime() + 86400000 - 1);
        }

        return {
            startDate: startDate.toISOString().split('T')[0],
            endDate: endDate.toISOString().split('T')[0],
            startTimestamp: startDate.getTime(),
            endTimestamp: endDate.getTime()
        };
    }

    // 버튼 렌더링
    render(containerId = 'timeRangePanel') {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('[TimeRangeSelector] 컨테이너를 찾을 수 없습니다:', containerId);
            return;
        }

        let html = '<div class="quick-select-buttons">';
        
        Object.keys(this.presets).forEach(preset => {
            const isActive = preset === this.currentRange;
            html += `<button class="time-btn ${isActive ? 'active' : ''}" data-range="${preset}">${this.presets[preset].label}</button>`;
        });
        
        html += '</div>';
        container.innerHTML = html;

        // 버튼 이벤트 리스너
        container.querySelectorAll('.time-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.selectRange(btn.dataset.range);
            });
        });
    }

    // 범위 선택
    selectRange(preset) {
        // 이전 버튼 비활성화
        document.querySelectorAll('.time-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // 선택한 버튼 활성화
        const btn = document.querySelector(`[data-range="${preset}"]`);
        if (btn) {
            btn.classList.add('active');
        }

        this.currentRange = preset;
        const dateRange = this.getDateRange(preset);
        
        if (this.callback) {
            this.callback(preset, dateRange);
        }
    }

    // 콜백 설정
    onRangeChange(callback) {
        this.callback = callback;
    }

    // 현재 범위 반환
    getCurrentRange() {
        return this.currentRange;
    }

    // 현재 날짜 범위 반환
    getCurrentDateRange() {
        return this.getDateRange(this.currentRange);
    }
}

// 전역으로 노출
window.TimeRangeSelector = TimeRangeSelector;
