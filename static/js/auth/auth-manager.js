// static/js/auth/auth-manager.js
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.authToken = null;
    }

    async updateLoginStatus() {
        const token = localStorage.getItem('authToken');
        if (!token) {
            showLoggedOutUI();
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            const data = await response.json();
            
            if (data.success && data.user) {
                showLoggedInUI(data.user);
            } else {
                showLoggedOutUI();
            }
        } catch (error) {
            console.error('로그인 상태 확인 오류:', error);
            showLoggedOutUI();
        }
    }

    async handleLogin(event) {
        console.log('로그인 시작:', event);
        event.preventDefault();
        
        const username = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        
        console.log('로그인 시도:', { username, password: password ? '***' : '' });
        
        try {
            console.log('API 호출 시작: /api/auth/login');
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            console.log('API 응답 수신:', response.status);
            const data = await response.json();
            console.log('API 응답 데이터:', data);

            if (data.success) {
                console.log('로그인 성공');
                this.currentUser = data.user;
                
                // 로컬 스토리지에 저장
                localStorage.setItem('currentUser', JSON.stringify(data.user));
                localStorage.setItem('authToken', 'session-token'); // 임시 토큰
                
                console.log('사용자 정보 저장 완료');
                
                // UI 직접 업데이트 (세션 검증 없이)
                showLoggedInUI(data.user);
                console.log('UI 업데이트 완료');
                
                // 모달 닫기 (Bootstrap 5 방식)
                const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
                if (modal) {
                    modal.hide();
                    console.log('로그인 모달 닫기 완료');
                }
                
                // 역할에 따른 리다이렉트
                if (data.user.role === 'admin') {
                    console.log('관리자 계정으로 리다이렉션 준비');
                    alert('로그인 성공! 관리자 대시보드로 이동합니다.');
                    window.location.href = '/admin-panel';
                } else {
                    console.log('일반 사용자 로그인 완료');
                    alert('로그인 성공! 환영합니다.');
                    // 일반 사용자는 메인 페이지에 머물거나 사용자 대시보드로 이동
                    // window.location.href = '/dashboard'; // 사용자 대시보드가 있다면
                    // 현재는 메인 페이지에 머물도록 함
                }
            } else {
                console.log('로그인 실패:', data.message || '알 수 없는 오류');
                alert('로그인 실패: ' + data.message);
            }
        } catch (error) {
            console.error('로그인 오류:', error);
            alert('로그인 중 오류가 발생했습니다.');
        }
    }

    async logout() {
        console.log('로그아웃 시작');
        
        try {
            const response = await fetch('/api/auth/logout', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
                // Note: We're not sending sessionId in body anymore, 
                // as the backend will get it from the session cookie
            });
            
            const data = await response.json();
            console.log('로그아웃 API 응답:', data);
            
            if (data.success) {
                // 로컬 스토리지 정리
                localStorage.removeItem('authToken');
                localStorage.removeItem('currentUser');
                
                console.log('로컬 스토리지 정리 완료');
                
                // UI 업데이트
                showLoggedOutUI();
                console.log('로그아웃 UI 표시 완료');
            } else {
                console.error('로그아웃 실패:', data.message);
                // 실패하더라도 UI는 로그아웃 상태로 변경
                localStorage.removeItem('authToken');
                localStorage.removeItem('currentUser');
                showLoggedOutUI();
            }
        } catch (error) {
            console.error('로그아웃 오류:', error);
            // 네트워크 오류 발생 시에도 UI는 로그아웃 상태로 변경
            localStorage.removeItem('authToken');
            localStorage.removeItem('currentUser');
            showLoggedOutUI();
        }
    }
}

// URL 파라미터 처리
function checkLoginSuccess() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('login') === 'success') {
        console.log('로그인 성공 감지');
        updateLoginStatus();
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}