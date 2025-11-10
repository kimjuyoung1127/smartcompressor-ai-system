// 대시보드 관련 기능
class AdminDashboard {
    constructor() {
        this.mainContent = null;
        this.init();
    }
    
    async init() {
        this.mainContent = document.getElementById('admin-main-content');
    }
    
    async loadDashboard() {
        try {
            // 대시보드 HTML 로드
            const response = await fetch('./components/dashboard.html');
            const html = await response.text();
            
            // 섹션 컨테이너 생성 또는 업데이트
            let section = document.getElementById('dashboard-section');
            if (!section) {
                section = document.createElement('section');
                section.id = 'dashboard-section';
                section.className = 'section-content';
                this.mainContent.appendChild(section);
            }
            
            section.innerHTML = html;
            section.style.display = 'block';
            
            // 사용자 데이터 로드
            await this.loadUsers();
            
            // 대시보드 통계 업데이트
            this.updateDashboardStats();
            
        } catch (error) {
            console.error('대시보드 로드 오류:', error);
        }
    }
    
    async loadUsers() {
        try {
            console.log('대시보드 사용자 목록 불러오기 시도 - API 호출 전');
            const response = await fetch('/api/admin-users/users', {
                credentials: 'include'  // 쿠키 포함
            });
            console.log('API 응답 수신:', response.status);
            const data = await response.json();
            console.log('API 응답 데이터:', data);
            
            if (response.status === 401) {
                console.error('401 인증 오류 발생 - 세션 또는 권한 문제');
                alert('권한이 없거나 세션이 만료되었습니다. 다시 로그인해주세요.');
                window.location.href = '/';
                return;
            }
            
            if (data.success) {
                window.allUsers = data.users;
            } else {
                alert('사용자 목록을 불러오는데 실패했습니다: ' + data.message);
            }
        } catch (error) {
            console.error('사용자 목록 불러오기 오류:', error);
            alert('사용자 목록을 불러오는데 오류가 발생했습니다.');
        }
    }
    
    updateDashboardStats() {
        if (!window.allUsers) return;
        
        document.getElementById('totalUsers').textContent = window.allUsers.length;
        
        const activeUsers = window.allUsers.filter(u => u.is_active).length;
        document.getElementById('activeUsers').textContent = activeUsers;
        
        const adminUsers = window.allUsers.filter(u => u.role === 'admin').length;
        document.getElementById('adminUsers').textContent = adminUsers;
        
        // 오늘 가입한 사용자 수 계산
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const todayUsers = window.allUsers.filter(u => {
            const userCreated = new Date(u.created_at);
            userCreated.setHours(0, 0, 0, 0);
            return userCreated.getTime() === today.getTime();
        }).length;
        document.getElementById('todayUsers').textContent = todayUsers;
    }
}

// 대시보드 인스턴스 생성
window.adminDashboard = new AdminDashboard();
