// 사이드바 관련 기능
class AdminSidebar {
    constructor() {
        this.sidebarElement = null;
        this.hamburgerMenu = null;
        this.init();
    }
    
    async init() {
        // 사이드바 HTML 로드
        await this.loadSidebarHTML();
        
        // 이벤트 리스너 설정
        this.setupEventListeners();
    }
    
    async loadSidebarHTML() {
        try {
            const response = await fetch('./components/sidebar.html');
            const html = await response.text();
            this.sidebarElement = document.getElementById('admin-sidebar');
            this.sidebarElement.innerHTML = html;
        } catch (error) {
            console.error('사이드바 로드 오류:', error);
        }
    }
    
    setupEventListeners() {
        // 모바일 메뉴 토글
        this.hamburgerMenu = document.getElementById('admin-hamburger-menu');
        if (this.hamburgerMenu) {
            this.hamburgerMenu.addEventListener('click', () => {
                this.sidebarElement.classList.toggle('active');
            });
        }
        
        // 네비게이션 링크 클릭 이벤트
        document.querySelectorAll('[data-section]').forEach(link => {
            link.addEventListener('click', async (e) => {
                e.preventDefault();
                const sectionId = e.currentTarget.getAttribute('data-section');
                await this.showSection(sectionId);
            });
        });
        
        // 로그아웃 버튼
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                this.handleLogout();
            });
        }
    }
    
    async showSection(sectionId) {
        // 모든 섹션 숨기기
        document.querySelectorAll('.section-content').forEach(el => {
            el.style.display = 'none';
        });
        
        // 선택한 섹션 보이기
        const sectionElement = document.getElementById(`${sectionId}-section`);
        if (sectionElement) {
            sectionElement.style.display = 'block';
        }
        
        // 네비게이션 링크 활성화 상태 업데이트
        document.querySelectorAll('.admin-nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // 클릭한 링크에 활성 클래스 추가
        const activeLink = document.querySelector(`[data-section="${sectionId}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
        // 해당 섹션에 맞는 데이터 불러오기
        await this.loadSectionData(sectionId);
    }
    
    async loadSectionData(sectionId) {
        // 각 섹션별 데이터 로드 함수 호출
        switch(sectionId) {
            case 'users':
                if (window.userManagement) {
                    await window.userManagement.showUserManagement();
                }
                break;
            case 'invites':
                if (window.inviteManagement) {
                    await window.inviteManagement.showInviteManagement();
                }
                break;
            case 'dashboard':
                if (window.adminDashboard) {
                    await window.adminDashboard.loadDashboard();
                }
                break;
            case 'system':
                if (window.systemSettings) {
                    await window.systemSettings.showSystemSettings();
                }
                break;
        }
    }
    
    handleLogout() {
        if (confirm('정말로 로그아웃 하시겠습니까?')) {
            fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/';
                } else {
                    alert('로그아웃에 실패했습니다.');
                }
            })
            .catch(error => {
                console.error('로그아웃 오류:', error);
                alert('로그아웃 중 오류가 발생했습니다.');
                window.location.href = '/';
            });
        }
    }
}

// 사이드바 인스턴스 생성
window.adminSidebar = new AdminSidebar();
