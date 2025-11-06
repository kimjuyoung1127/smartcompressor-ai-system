// 시스템 설정 관리 기능
class SystemSettings {
    constructor() {
        this.mainContent = null;
        this.init();
    }
    
    init() {
        this.mainContent = document.getElementById('admin-main-content');
    }
    
    async showSystemSettings() {
        try {
            // 시스템 설정 HTML 로드
            const response = await fetch('./components/system.html');
            const html = await response.text();
            
            // 섹션 컨테이너 생성 또는 업데이트
            let section = document.getElementById('system-section');
            if (!section) {
                section = document.createElement('section');
                section.id = 'system-section';
                section.className = 'section-content';
                this.mainContent.appendChild(section);
            }
            
            section.innerHTML = html;
            section.style.display = 'block';
            
            // 설정 데이터 로드
            await this.loadSettings();
            
        } catch (error) {
            console.error('시스템 설정 페이지 로드 오류:', error);
        }
    }
    
    async loadSettings() {
        try {
            // 시스템 설정을 서버에서 불러오는 API 호출
            const response = await fetch('/api/admin/system-settings', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.displaySettings(data.settings);
                }
            } else {
                console.log('시스템 설정을 불러올 수 없습니다. 기본 설정을 표시합니다.');
                // 기본 설정 표시
                this.displayDefaultSettings();
            }
        } catch (error) {
            console.error('시스템 설정 로드 오류:', error);
            // 기본 설정 표시
            this.displayDefaultSettings();
        }
    }
    
    displaySettings(settings) {
        // 실제 설정 데이터를 표시하는 로직
        // API가 준비되면 이 부분을 구현합니다.
        console.log('시스템 설정:', settings);
    }
    
    displayDefaultSettings() {
        // 기본 설정을 표시하는 로직
        // 현재는 간단한 메시지만 표시
        const section = document.getElementById('system-section');
        if (section) {
            const settingsCard = section.querySelector('.admin-card');
            if (settingsCard) {
                settingsCard.innerHTML = `
                    <p>시스템 설정 기능은 준비 중입니다.</p>
                    <p>향후 다음과 같은 설정을 관리할 수 있습니다:</p>
                    <ul>
                        <li>시스템 기본 설정</li>
                        <li>사용자 정책 설정</li>
                        <li>보안 정책 설정</li>
                        <li>알림 설정</li>
                        <li>백업 설정</li>
                    </ul>
                `;
            }
        }
    }
}

// 시스템 설정 인스턴스 생성
window.systemSettings = new SystemSettings();
