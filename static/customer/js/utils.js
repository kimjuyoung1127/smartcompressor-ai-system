/**
 * 유틸리티 함수 모음
 */

const Utils = {
    /**
     * 날짜 포맷팅
     */
    formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    },
    
    /**
     * 상대 시간 표시 (예: "5분 전")
     */
    timeAgo(date) {
        const seconds = Math.floor((new Date() - new Date(date)) / 1000);
        
        if (seconds < 60) return '방금 전';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}분 전`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}시간 전`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}일 전`;
        
        return this.formatDate(date, 'YYYY-MM-DD');
    },
    
    /**
     * 숫자 포맷팅 (천단위 콤마)
     */
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },
    
    /**
     * 바이트 크기를 사람이 읽을 수 있는 형태로 변환
     */
    formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },
    
    /**
     * 디바운스 함수
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * 쓰로틀 함수
     */
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    /**
     * 쿼리 문자열을 객체로 변환
     */
    parseQueryString(queryString) {
        const params = new URLSearchParams(queryString);
        const result = {};
        for (const [key, value] of params) {
            result[key] = value;
        }
        return result;
    },
    
    /**
     * 객체를 쿼리 문자열로 변환
     */
    objectToQueryString(obj) {
        return Object.keys(obj)
            .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(obj[key])}`)
            .join('&');
    },
    
    /**
     * 딥 클론
     */
    deepClone(obj) {
        return JSON.parse(JSON.stringify(obj));
    },
    
    /**
     * 로컬 스토리지 헬퍼
     */
    storage: {
        set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (error) {
                console.error('Storage set error:', error);
                return false;
            }
        },
        
        get(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                console.error('Storage get error:', error);
                return defaultValue;
            }
        },
        
        remove(key) {
            try {
                localStorage.removeItem(key);
                return true;
            } catch (error) {
                console.error('Storage remove error:', error);
                return false;
            }
        },
        
        clear() {
            try {
                localStorage.clear();
                return true;
            } catch (error) {
                console.error('Storage clear error:', error);
                return false;
            }
        }
    },
    
    /**
     * 콘솔 로그 헬퍼
     */
    log: {
        info(...args) {
            if (CONFIG.DEBUG) {
                console.log('[INFO]', ...args);
            }
        },
        
        warn(...args) {
            if (CONFIG.DEBUG) {
                console.warn('[WARN]', ...args);
            }
        },
        
        error(...args) {
            console.error('[ERROR]', ...args);
        }
    }
};

// 전역으로 노출
window.Utils = Utils;
