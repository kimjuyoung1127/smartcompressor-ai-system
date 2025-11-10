/**
 * 인증 및 권한 관리 서비스
 */

class AuthService {
    constructor() {
        this.currentUser = null;
        this.hasAccess = false;
    }
    
    /**
     * 세션 및 권한 확인
     */
    async checkAuth() {
        try {
            Utils.log.info('권한 확인 시작...');
            
            // 1. 세션 검증
            const response = await fetch(CONFIG.AUTH.VERIFY_URL, {
                credentials: 'include'
            });
            
            if (!response.ok) {
                Utils.log.warn('세션 검증 실패:', response.status);
                this.redirectToLogin();
                return false;
            }
            
            const data = await response.json();
            
            // 로그인 안됨
            if (!data.success || !data.user) {
                Utils.log.warn('사용자 정보 없음');
                this.redirectToLogin();
                return false;
            }
            
            this.currentUser = data.user;
            Utils.log.info('사용자 정보:', this.currentUser);
            
            // 2. 고객 대시보드 접근 권한 확인
            const accessResponse = await fetch(CONFIG.AUTH.CHECK_ACCESS_URL, {
                credentials: 'include'
            });
            
            if (!accessResponse.ok) {
                Utils.log.error('권한 확인 API 실패');
                this.redirectToUpgrade();
                return false;
            }
            
            const accessData = await accessResponse.json();
            
            if (!accessData.hasAccess) {
                Utils.log.warn('접근 권한 없음:', accessData);
                this.redirectToUpgrade();
                return false;
            }
            
            this.hasAccess = true;
            Utils.log.info('✅ 권한 확인 완료');
            
            // 사용자 정보 로컬 스토리지 저장
            Utils.storage.set(CONFIG.STORAGE_KEYS.USER, this.currentUser);
            
            return true;
            
        } catch (error) {
            Utils.log.error('인증 오류:', error);
            this.redirectToLogin();
            return false;
        }
    }
    
    /**
     * 현재 사용자 정보 반환
     */
    getCurrentUser() {
        return this.currentUser;
    }
    
    /**
     * 접근 권한 확인
     */
    hasPermission() {
        return this.hasAccess;
    }
    
    /**
     * 특정 역할 확인
     */
    hasRole(role) {
        if (!this.currentUser) return false;
        
        const userRoles = Array.isArray(this.currentUser.roles)
            ? this.currentUser.roles
            : [this.currentUser.role];
        
        return userRoles.includes(role);
    }
    
    /**
     * admin 권한 확인
     */
    isAdmin() {
        return this.hasRole('admin');
    }
    
    /**
     * premium_user 권한 확인
     */
    isPremiumUser() {
        return this.hasRole('premium_user');
    }
    
    /**
     * 로그아웃
     */
    async logout() {
        try {
            await fetch('/api/auth/logout', {
                method: 'POST',
                credentials: 'include'
            });
        } catch (error) {
            Utils.log.error('로그아웃 오류:', error);
        } finally {
            // 로컬 스토리지 클리어
            Utils.storage.clear();
            
            // 로그인 페이지로 리다이렉트
            window.location.href = CONFIG.AUTH.LOGIN_URL;
        }
    }
    
    /**
     * 로그인 페이지로 리다이렉트
     */
    redirectToLogin() {
        Utils.log.info('로그인 페이지로 이동');
        window.location.href = CONFIG.AUTH.LOGIN_URL;
    }
    
    /**
     * 업그레이드 페이지로 리다이렉트
     */
    redirectToUpgrade() {
        Utils.log.info('업그레이드 페이지로 이동');
        window.location.href = CONFIG.PAGES.UPGRADE;
    }
    
    /**
     * 사용자 정보 업데이트
     */
    updateUser(userData) {
        this.currentUser = { ...this.currentUser, ...userData };
        Utils.storage.set(CONFIG.STORAGE_KEYS.USER, this.currentUser);
    }
}

// 전역 인스턴스 생성
window.authService = new AuthService();
