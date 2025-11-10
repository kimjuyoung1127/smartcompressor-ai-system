// 사용자 관리 기능
class UserManagement {
    constructor() {
        this.mainContent = null;
        this.init();
    }
    
    async init() {
        this.mainContent = document.getElementById('admin-main-content');
        await this.loadModals();
        this.setupModalEvents();
    }
    
    async loadModals() {
        try {
            // 모든 모달 HTML을 한 번에 로드
            const response = await fetch('./components/modals.html');
            const html = await response.text();
            
            // 모달 컨테이너 생성 또는 업데이트
            let modalContainer = document.getElementById('modals-container');
            if (!modalContainer) {
                modalContainer = document.createElement('div');
                modalContainer.id = 'modals-container';
                document.body.appendChild(modalContainer);
            }
            
            modalContainer.innerHTML = html;
        } catch (error) {
            console.error('모달 로드 오류:', error);
        }
    }
    
    setupModalEvents() {
        // 역할 변경 확인 버튼
        const roleUpdateBtn = document.getElementById('confirmRoleUpdate');
        if (roleUpdateBtn) {
            roleUpdateBtn.addEventListener('click', () => this.updateUserRole());
        }
        
        // 상태 변경 확인 버튼
        const statusUpdateBtn = document.getElementById('confirmStatusUpdate');
        if (statusUpdateBtn) {
            statusUpdateBtn.addEventListener('click', () => this.updateUserStatus());
        }
    }
    
    async loadUsers() {
        try {
            console.log('사용자 목록 불러오기 시도 - API 호출 전');
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
                this.displayUsers();
                
                // 대시보드가 로드되어 있으면 통계 업데이트
                if (window.adminDashboard) {
                    window.adminDashboard.updateDashboardStats();
                }
            } else {
                alert('사용자 목록을 불러오는데 실패했습니다: ' + data.message);
            }
        } catch (error) {
            console.error('사용자 목록 불러오기 오류:', error);
            alert('사용자 목록을 불러오는데 오류가 발생했습니다.');
        }
    }
    
    async showUserManagement() {
        try {
            // 사용자 관리 HTML 로드
            const response = await fetch('./components/users.html');
            const html = await response.text();
            
            // 섹션 컨테이너 생성 또는 업데이트
            let section = document.getElementById('users-section');
            if (!section) {
                section = document.createElement('section');
                section.id = 'users-section';
                section.className = 'section-content';
                this.mainContent.appendChild(section);
            }
            
            section.innerHTML = html;
            
            // 버튼 이벤트 리스너 설정
            this.setupButtonEvents();
            
            // 사용자 데이터 로드
            await this.loadUsers();
            
        } catch (error) {
            console.error('사용자 관리 페이지 로드 오류:', error);
        }
    }
    
    setupButtonEvents() {
        // 사용자 생성 버튼
        const createUserBtn = document.getElementById('createUserBtn');
        if (createUserBtn) {
            createUserBtn.addEventListener('click', () => {
                // 사용자 생성 기능 구현
                alert('사용자 생성 기능은 준비 중입니다.');
            });
        }
        
        // 초대 생성 버튼
        const inviteUserBtn = document.getElementById('inviteUserBtn');
        if (inviteUserBtn) {
            inviteUserBtn.addEventListener('click', () => {
                if (window.inviteManagement) {
                    const modal = new bootstrap.Modal(document.getElementById('inviteModal'));
                    modal.show();
                }
            });
        }
    }
    
    displayUsers() {
        const tbody = document.getElementById('usersTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (!window.allUsers) return;
        
        window.allUsers.forEach(user => {
            const row = document.createElement('tr');
            
            // 역할에 따라 배지 클래스 결정
            let roleClass = 'role-user';
            switch (user.role) {
                case 'admin': roleClass = 'role-admin'; break;
                case 'labeler': roleClass = 'role-labeler'; break;
                case 'owner': roleClass = 'role-owner'; break;
                case 'user': roleClass = 'role-user'; break;
            }
            
            // 상태에 따라 배지 클래스 결정
            const statusClass = user.is_active ? 'status-active' : 'status-inactive';
            const statusText = user.is_active ? '활성' : '비활성';
            
            // 마지막 로그인 날짜 포맷
            const lastLogin = user.last_login ? new Date(user.last_login).toLocaleString() : '없음';
            
            row.innerHTML = `
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td><span class="role-badge ${roleClass}">${user.role}</span></td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td>${new Date(user.created_at).toLocaleDateString()}</td>
                <td>${lastLogin}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline-primary" onclick="window.userManagement.openRoleModal(${user.id}, '${user.username}', '${user.email}', '${user.role}')">
                            <i class="fas fa-user-tag"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="window.userManagement.openStatusModal(${user.id}, '${user.username}', ${user.is_active})">
                            <i class="fas fa-power-off"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-info" onclick="window.userManagement.viewUserDetails(${user.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }
    
    openRoleModal(userId, username, email, currentRole) {
        document.getElementById('userIdToUpdate').value = userId;
        document.getElementById('userToUpdate').value = username;
        document.getElementById('emailToUpdate').value = email;
        document.getElementById('currentRole').value = currentRole;
        document.getElementById('newRole').value = currentRole;
        
        const modal = new bootstrap.Modal(document.getElementById('userRoleModal'));
        modal.show();
    }
    
    openStatusModal(userId, username, isActive) {
        document.getElementById('statusUserName').textContent = username;
        
        // 라디오 버튼 선택 상태 설정
        if (isActive) {
            document.getElementById('deactivateRadio').checked = true;
        } else {
            document.getElementById('activateRadio').checked = true;
        }
        
        // 숨김 입력 필드에 사용자 ID 저장
        document.getElementById('statusUserId').value = userId;
        
        const modal = new bootstrap.Modal(document.getElementById('userStatusModal'));
        modal.show();
    }
    
    async updateUserRole() {
        const userId = document.getElementById('userIdToUpdate').value;
        const newRole = document.getElementById('newRole').value;
        
        try {
            console.log(`사용자 역할 변경 시도 - ID: ${userId}, 역할: ${newRole}`);
            const response = await fetch(`/api/admin-users/users/${userId}/role`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',  // 쿠키 포함
                body: JSON.stringify({ role: newRole })
            });
            console.log('역할 변경 API 응답 상태:', response.status);
            
            const data = await response.json();
            
            if (data.success) {
                alert(data.message);
                const modal = bootstrap.Modal.getInstance(document.getElementById('userRoleModal'));
                modal.hide();
                this.loadUsers(); // 사용자 목록 다시 불러오기
            } else {
                alert('역할 변경에 실패했습니다: ' + data.message);
            }
        } catch (error) {
            console.error('역할 변경 오류:', error);
            alert('역할 변경 중 오류가 발생했습니다.');
        }
    }
    
    async updateUserStatus() {
        const selectedStatus = document.querySelector('input[name="statusRadio"]:checked');
        if (!selectedStatus) {
            alert('상태를 선택해주세요.');
            return;
        }
        
        const userId = document.getElementById('statusUserId').value;
        const isActive = selectedStatus.value === 'true';
        
        try {
            console.log(`사용자 상태 변경 시도 - ID: ${userId}, 상태: ${isActive}`);
            const response = await fetch(`/api/admin-users/users/${userId}/status`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',  // 쿠키 포함
                body: JSON.stringify({ isActive: isActive })
            });
            console.log('상태 변경 API 응답 상태:', response.status);
            
            const data = await response.json();
            
            if (data.success) {
                alert(data.message);
                const modal = bootstrap.Modal.getInstance(document.getElementById('userStatusModal'));
                modal.hide();
                this.loadUsers(); // 사용자 목록 다시 불러오기
            } else {
                alert('상태 변경에 실패했습니다: ' + data.message);
            }
        } catch (error) {
            console.error('상태 변경 오류:', error);
            alert('상태 변경 중 오류가 발생했습니다.');
        }
    }
    
    async viewUserDetails(userId) {
        try {
            console.log(`사용자 상세 정보 불러오기 시도 - ID: ${userId}`);
            const response = await fetch(`/api/admin-users/users/${userId}`, {
                credentials: 'include'  // 쿠키 포함
            });
            console.log('사용자 상세 정보 API 응답 상태:', response.status);
            const data = await response.json();
            console.log('사용자 상세 정보 응답 데이터:', data);
            
            if (data.success) {
                alert('사용자 정보: ' + JSON.stringify(data.user, null, 2));
            } else {
                alert('사용자 정보를 불러오는데 실패했습니다: ' + data.message);
            }
        } catch (error) {
            console.error('사용자 정보 불러오기 오류:', error);
            alert('사용자 정보를 불러오는데 오류가 발생했습니다.');
        }
    }
}

// 사용자 관리 인스턴스 생성
window.userManagement = new UserManagement();
