// 메인 앱 초기화 및 공통 기능
class AdminApp {
    constructor() {
        this.currentUser = null;
        this.allUsers = [];
        this.allInvites = [];
        this.init();
    }
    
    async init() {
        // 세션 확인
        await this.checkSession();
        
        // 모듈 로드 확인 및 초기화
        await this.waitForModules();
        
        // 초기 섹션 로드
        await this.loadInitialSection();
    }
    
    async checkSession() {
        try {
            console.log('세션 확인 시작 - API 호출 전');
            const response = await fetch('/api/auth/verify', {
                credentials: 'include'  // 쿠키 포함
            });
            console.log('세션 확인 API 응답 상태:', response.status);
            
            if (response.status === 401) {
                console.error('401 인증 오류 발생 - 유효하지 않은 세션');
                window.location.href = '/';
                return;
            }
            
            const data = await response.json();
            console.log('세션 확인 응답 데이터:', data);
            
            if (!data.success || !data.user) {
                console.error('세션 확인 실패 - 사용자 정보 없음:', data);
                // 관리자 권한이 없으면 메인 페이지로 리디렉션
                window.location.href = '/';
                return;
            }
            
            // 사용자 정보 저장
            this.currentUser = data.user;
            
            // UI 업데이트
            document.title = `SignalCraft 관리자 대시보드 - ${data.user.username}`;
            
        } catch (error) {
            console.error('세션 확인 오류:', error);
            window.location.href = '/';
        }
    }
    
    async waitForModules() {
        // 모든 모듈이 로드될 때까지 기다림
        const maxWait = 5000; // 최대 5초 대기
        const waitInterval = 100; // 100ms 간격으로 확인
        let waitTime = 0;
        
        const checkModules = () => {
            return window.adminSidebar && 
                   window.adminDashboard && 
                   window.userManagement && 
                   window.inviteManagement && 
                   window.systemSettings;
        };
        
        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                waitTime += waitInterval;
                
                if (checkModules()) {
                    clearInterval(checkInterval);
                    resolve();
                } else if (waitTime >= maxWait) {
                    console.error('모듈 로드 시간 초과');
                    clearInterval(checkInterval);
                    resolve();
                }
            }, waitInterval);
        });
    }
    
    async loadInitialSection() {
        // 초기에 대시보드 섹션 로드
        if (window.adminSidebar) {
            await window.adminSidebar.showSection('dashboard');
        }
    }
    
    // 에러 표시
    showError(message) {
        alert(message);
    }
}

// 앱 인스턴스 생성
document.addEventListener('DOMContentLoaded', function() {
    window.adminApp = new AdminApp();
});
