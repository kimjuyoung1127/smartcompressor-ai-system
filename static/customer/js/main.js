/**
 * Customer Dashboard 메인 앱
 * 앱 초기화 및 전체 플로우 관리
 */

class CustomerApp {
    constructor() {
        this.initialized = false;
    }
    
    /**
     * 앱 초기화
     */
    async init() {
        try {
            Utils.log.info('=== Customer Dashboard 초기화 시작 ===');
            
            // 1. 권한 확인 (가장 먼저)
            Utils.log.info('Step 1: 권한 확인');
            const hasAuth = await authService.checkAuth();
            
            if (!hasAuth) {
                // authService에서 이미 리다이렉트 처리됨
                return;
            }
            
            Utils.log.info('✅ 권한 확인 완료:', authService.getCurrentUser());
            
            // 2. UI 초기화
            Utils.log.info('Step 2: UI 초기화');
            this.initUI();
            
            // 3. 이벤트 리스너 설정
            Utils.log.info('Step 3: 이벤트 리스너 설정');
            this.setupEventListeners();
            
            // 4. 초기 페이지 로드
            Utils.log.info('Step 4: 초기 페이지 로드');
            await this.loadInitialPage();
            
            // 5. 로딩 화면 숨기기
            this.hideLoading();
            
            // 6. 메인 앱 표시
            document.getElementById('app').style.display = 'block';
            
            this.initialized = true;
            Utils.log.info('=== Customer Dashboard 초기화 완료 ===');
            
        } catch (error) {
            Utils.log.error('앱 초기화 오류:', error);
            this.showError('앱을 초기화할 수 없습니다. 페이지를 새로고침해주세요.');
        }
    }
    
    /**
     * UI 초기화
     */
    initUI() {
        // 사이드바 렌더링
        this.renderSidebar();
        
        // 헤더 렌더링
        this.renderHeader();
    }
    
    /**
     * 사이드바 렌더링
     */
    renderSidebar() {
        const sidebar = document.getElementById('sidebar');
        const user = authService.getCurrentUser();
        
        sidebar.innerHTML = `
            <div class="sidebar-header">
                <div class="logo">
                    <i class="fas fa-chart-line"></i>
                    <span>SignalCraft</span>
                </div>
            </div>
            
            <nav class="sidebar-nav">
                <a href="#" class="nav-link active" data-route="/dashboard">
                    <i class="fas fa-th-large"></i>
                    <span>대시보드</span>
                </a>
                <a href="#" class="nav-link" data-route="/devices">
                    <i class="fas fa-cubes"></i>
                    <span>디바이스</span>
                </a>
                <a href="#" class="nav-link" data-route="/monitoring">
                    <i class="fas fa-chart-bar"></i>
                    <span>모니터링</span>
                </a>
                <a href="#" class="nav-link" data-route="/anomalies">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>이상 징후</span>
                </a>
                <a href="#" class="nav-link" data-route="/audio">
                    <i class="fas fa-microphone"></i>
                    <span>오디오 분석</span>
                </a>
                <a href="#" class="nav-link" data-route="/reports">
                    <i class="fas fa-file-alt"></i>
                    <span>리포트</span>
                </a>
                <a href="#" class="nav-link" data-route="/settings">
                    <i class="fas fa-cog"></i>
                    <span>설정</span>
                </a>
            </nav>
            
            <div class="sidebar-footer">
                <div class="user-info">
                    <i class="fas fa-user-circle"></i>
                    <div class="user-details">
                        <div class="user-name">${user?.username || 'User'}</div>
                        <div class="user-role">${user?.role || 'user'}</div>
                    </div>
                </div>
                <button class="logout-btn" id="logout-btn">
                    <i class="fas fa-sign-out-alt"></i>
                    <span>로그아웃</span>
                </button>
            </div>
        `;
    }
    
    /**
     * 헤더 렌더링
     */
    renderHeader() {
        const header = document.getElementById('header');
        const user = authService.getCurrentUser();
        
        header.innerHTML = `
            <div class="header-left">
                <button class="menu-toggle" id="menu-toggle">
                    <i class="fas fa-bars"></i>
                </button>
                <h2 class="page-title">대시보드</h2>
            </div>
            
            <div class="header-right">
                <button class="header-btn" id="refresh-btn" title="새로고침">
                    <i class="fas fa-sync-alt"></i>
                </button>
                <button class="header-btn" id="notification-btn" title="알림">
                    <i class="fas fa-bell"></i>
                    <span class="badge">0</span>
                </button>
                <div class="user-menu">
                    <button class="user-menu-btn">
                        <i class="fas fa-user-circle"></i>
                        <span>${user?.username || 'User'}</span>
                        <i class="fas fa-chevron-down"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    /**
     * 이벤트 리스너 설정
     */
    setupEventListeners() {
        // 로그아웃 버튼
        document.getElementById('logout-btn')?.addEventListener('click', () => {
            if (confirm('로그아웃 하시겠습니까?')) {
                authService.logout();
            }
        });
        
        // 네비게이션 링크
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const route = link.getAttribute('data-route');
                if (route) {
                    router.navigate(route);
                }
            });
        });
        
        // 메뉴 토글 (모바일)
        document.getElementById('menu-toggle')?.addEventListener('click', () => {
            document.getElementById('sidebar')?.classList.toggle('active');
        });
        
        // 새로고침 버튼
        document.getElementById('refresh-btn')?.addEventListener('click', () => {
            this.refresh();
        });
    }
    
    /**
     * 초기 페이지 로드
     */
    async loadInitialPage() {
        // 기본적으로 대시보드 표시
        await router.navigate('/dashboard', false);
    }
    
    /**
     * 데이터 새로고침
     */
    async refresh() {
        Utils.log.info('데이터 새로고침');
        
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.classList.add('spinning');
            setTimeout(() => {
                refreshBtn.classList.remove('spinning');
            }, 1000);
        }
        
        // 현재 페이지 다시 로드
        if (router.currentRoute) {
            await router.navigate(router.currentRoute, false);
        }
    }
    
    /**
     * 로딩 화면 숨기기
     */
    hideLoading() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.classList.add('hidden');
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 300);
        }
    }
    
    /**
     * 에러 표시
     */
    showError(message) {
        alert(message);
        // TODO: 토스트 알림으로 개선
    }
}

// 앱 시작
document.addEventListener('DOMContentLoaded', () => {
    Utils.log.info('DOM 로드 완료 - 앱 시작');
    window.app = new CustomerApp();
    window.app.init();
});
