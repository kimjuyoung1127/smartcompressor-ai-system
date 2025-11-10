/**
 * SPA 라우터
 * 클라이언트 사이드 라우팅 관리
 */

class Router {
    constructor() {
        this.routes = {};
        this.currentRoute = null;
        this.init();
    }
    
    /**
     * 라우터 초기화
     */
    init() {
        // 기본 라우트 등록
        this.register('/', this.renderDashboard.bind(this));
        this.register('/dashboard', this.renderDashboard.bind(this));
        this.register('/devices', this.renderDevices.bind(this));
        this.register('/monitoring', this.renderMonitoring.bind(this));
        this.register('/anomalies', this.renderAnomalies.bind(this));
        this.register('/audio', this.renderAudio.bind(this));
        this.register('/reports', this.renderReports.bind(this));
        this.register('/settings', this.renderSettings.bind(this));
        
        // 브라우저 뒤로가기/앞으로가기 처리
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.route) {
                this.navigate(e.state.route, false);
            }
        });
    }
    
    /**
     * 라우트 등록
     */
    register(path, handler) {
        this.routes[path] = handler;
    }
    
    /**
     * 라우트 이동
     */
    async navigate(path, pushState = true) {
        Utils.log.info('네비게이트:', path);
        
        // 현재 경로와 같으면 무시
        if (this.currentRoute === path) {
            return;
        }
        
        // 라우트 핸들러 찾기
        const handler = this.routes[path];
        
        if (!handler) {
            Utils.log.warn('라우트를 찾을 수 없음:', path);
            return;
        }
        
        try {
            // 라우트 핸들러 실행
            await handler();
            
            // 브라우저 히스토리 업데이트
            if (pushState) {
                history.pushState({ route: path }, '', path);
            }
            
            // 현재 라우트 저장
            this.currentRoute = path;
            
            // 네비게이션 메뉴 활성화 상태 업데이트
            this.updateActiveNav(path);
            
        } catch (error) {
            Utils.log.error('라우트 핸들링 오류:', error);
        }
    }
    
    /**
     * 네비게이션 메뉴 활성화 상태 업데이트
     */
    updateActiveNav(path) {
        // 모든 nav-link에서 active 클래스 제거
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // 현재 경로와 일치하는 링크에 active 추가
        const activeLink = document.querySelector(`[data-route="${path}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }
    
    /**
     * 대시보드 렌더링
     */
    async renderDashboard() {
        Utils.log.info('대시보드 렌더링');
        const content = document.getElementById('dashboard-content');
        content.innerHTML = `
            <div class="dashboard-header">
                <h1>대시보드</h1>
                <p>실시간 모니터링 및 관리</p>
            </div>
            <div class="dashboard-grid">
                <div class="card">
                    <h3>디바이스 현황</h3>
                    <p>준비 중...</p>
                </div>
                <div class="card">
                    <h3>센서 데이터</h3>
                    <p>준비 중...</p>
                </div>
                <div class="card">
                    <h3>이상 징후</h3>
                    <p>준비 중...</p>
                </div>
            </div>
        `;
    }
    
    /**
     * 디바이스 페이지 렌더링
     */
    async renderDevices() {
        Utils.log.info('디바이스 페이지 렌더링');
        const content = document.getElementById('dashboard-content');
        content.innerHTML = `
            <div class="page-header">
                <h1>디바이스 관리</h1>
                <p>등록된 디바이스 목록 및 관리</p>
            </div>
            <div class="page-content">
                <p>디바이스 목록을 불러오는 중...</p>
            </div>
        `;
    }
    
    /**
     * 모니터링 페이지 렌더링
     */
    async renderMonitoring() {
        Utils.log.info('모니터링 페이지 렌더링');
        const content = document.getElementById('dashboard-content');
        content.innerHTML = `
            <div class="page-header">
                <h1>실시간 모니터링</h1>
                <p>센서 데이터 실시간 모니터링</p>
            </div>
            <div class="page-content">
                <p>모니터링 데이터를 불러오는 중...</p>
            </div>
        `;
    }
    
    /**
     * 이상 징후 페이지 렌더링
     */
    async renderAnomalies() {
        Utils.log.info('이상 징후 페이지 렌더링');
        const content = document.getElementById('dashboard-content');
        content.innerHTML = `
            <div class="page-header">
                <h1>이상 징후</h1>
                <p>감지된 이상 징후 목록</p>
            </div>
            <div class="page-content">
                <p>이상 징후를 불러오는 중...</p>
            </div>
        `;
    }
    
    /**
     * 오디오 분석 페이지 렌더링
     */
    async renderAudio() {
        Utils.log.info('오디오 분석 페이지 렌더링');
        const content = document.getElementById('dashboard-content');
        content.innerHTML = `
            <div class="page-header">
                <h1>오디오 분석</h1>
                <p>AI 기반 오디오 분석</p>
            </div>
            <div class="page-content">
                <p>오디오 분석 페이지 준비 중...</p>
            </div>
        `;
    }
    
    /**
     * 리포트 페이지 렌더링
     */
    async renderReports() {
        Utils.log.info('리포트 페이지 렌더링');
        const content = document.getElementById('dashboard-content');
        content.innerHTML = `
            <div class="page-header">
                <h1>리포트</h1>
                <p>데이터 분석 및 리포트 생성</p>
            </div>
            <div class="page-content">
                <p>리포트 페이지 준비 중...</p>
            </div>
        `;
    }
    
    /**
     * 설정 페이지 렌더링
     */
    async renderSettings() {
        Utils.log.info('설정 페이지 렌더링');
        const content = document.getElementById('dashboard-content');
        content.innerHTML = `
            <div class="page-header">
                <h1>설정</h1>
                <p>시스템 설정 및 환경설정</p>
            </div>
            <div class="page-content">
                <p>설정 페이지 준비 중...</p>
            </div>
        `;
    }
}

// 전역 라우터 인스턴스
window.router = new Router();
