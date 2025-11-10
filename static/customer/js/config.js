/**
 * Customer Dashboard 설정 파일
 */

const CONFIG = {
    // API 기본 URL
    API_BASE_URL: '/api/customer',
    
    // 인증 관련
    AUTH: {
        VERIFY_URL: '/api/auth/verify',
        LOGIN_URL: '/login',
        CHECK_ACCESS_URL: '/customer/check-access'
    },
    
    // 권한
    ALLOWED_ROLES: ['admin', 'premium_user'],
    
    // 페이지 URL
    PAGES: {
        DASHBOARD: '/customer/dashboard',
        UPGRADE: '/customer/upgrade-required',
        HOME: '/'
    },
    
    // API 타임아웃 (밀리초)
    API_TIMEOUT: 10000,
    
    // 데이터 새로고침 간격 (밀리초)
    REFRESH_INTERVAL: 30000,
    
    // 로컬 스토리지 키
    STORAGE_KEYS: {
        USER: 'signalcraft_user',
        SESSION: 'signalcraft_session',
        SETTINGS: 'signalcraft_settings'
    },
    
    // 차트 기본 색상
    CHART_COLORS: {
        primary: '#667eea',
        success: '#28a745',
        warning: '#ffc107',
        danger: '#dc3545',
        info: '#17a2b8',
        secondary: '#6c757d'
    },
    
    // 디바이스 상태 색상
    DEVICE_STATUS_COLORS: {
        online: '#28a745',
        offline: '#6c757d',
        warning: '#ffc107',
        error: '#dc3545'
    },
    
    // 심각도 색상
    SEVERITY_COLORS: {
        low: '#17a2b8',
        medium: '#ffc107',
        high: '#fd7e14',
        critical: '#dc3545'
    },
    
    // 페이지네이션 기본값
    PAGINATION: {
        PER_PAGE: 10,
        MAX_PER_PAGE: 100
    },
    
    // 디버그 모드
    DEBUG: true
};

// 전역으로 노출
window.CONFIG = CONFIG;
