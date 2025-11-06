// 초대 관리 기능
class InviteManagement {
    constructor() {
        this.mainContent = null;
        this.allInvites = [];
        this.init();
    }
    
    init() {
        this.mainContent = document.getElementById('admin-main-content');
        this.setupInviteEvents();
    }
    
    setupInviteEvents() {
        // 초대 생성 확인 버튼 - DOM에 추가될 때까지 기다림
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                const confirmInviteBtn = document.getElementById('confirmInvite');
                if (confirmInviteBtn) {
                    confirmInviteBtn.addEventListener('click', () => this.createInvite());
                }
            }, 100);
        });
    }
    
    async loadInvites() {
        try {
            const response = await fetch('/api/admin-invites/invites', {
                credentials: 'include'  // 쿠키 포함
            });
            const data = await response.json();
            
            if (data.success) {
                this.allInvites = data.invites;
                this.displayInvites();
            } else {
                alert('초대 목록을 불러오는데 실패했습니다: ' + data.message);
            }
        } catch (error) {
            console.error('초대 목록 불러오기 오류:', error);
            alert('초대 목록을 불러오는데 오류가 발생했습니다.');
        }
    }
    
    async showInviteManagement() {
        try {
            // 초대 관리 HTML 로드
            const response = await fetch('./components/invites.html');
            const html = await response.text();
            
            // 섹션 컨테이너 생성 또는 업데이트
            let section = document.getElementById('invites-section');
            if (!section) {
                section = document.createElement('section');
                section.id = 'invites-section';
                section.className = 'section-content';
                this.mainContent.appendChild(section);
            }
            
            section.innerHTML = html;
            section.style.display = 'block';
            
            // 초대 생성 버튼 이벤트
            const createInviteBtn = document.getElementById('createInviteBtn');
            if (createInviteBtn) {
                createInviteBtn.addEventListener('click', () => {
                    const modal = new bootstrap.Modal(document.getElementById('inviteModal'));
                    modal.show();
                });
            }
            
            // 초대 데이터 로드
            await this.loadInvites();
            
        } catch (error) {
            console.error('초대 관리 페이지 로드 오류:', error);
        }
    }
    
    displayInvites() {
        const tbody = document.getElementById('invitesTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        this.allInvites.forEach(invite => {
            // 상태 확인
            const isUsed = invite.is_used;
            const isExpired = new Date(invite.expiry) < new Date();
            const status = isUsed ? '사용됨' : (isExpired ? '만료됨' : '유효');
            const statusClass = isUsed ? 'status-inactive' : (isExpired ? 'status-inactive' : 'status-active');
            
            // 역할에 따라 배지 클래스 결정
            let roleClass = 'role-user';
            switch (invite.role) {
                case 'admin': roleClass = 'role-admin'; break;
                case 'labeler': roleClass = 'role-labeler'; break;
                case 'owner': roleClass = 'role-owner'; break;
                case 'user': roleClass = 'role-user'; break;
            }
            
            // 만료일 포맷
            const expiry = new Date(invite.expiry).toLocaleString();
            
            // 생성자 이름이 없을 경우 처리
            const createdBy = invite.created_by_username || '알 수 없음';
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${invite.email}</td>
                <td>${invite.username}</td>
                <td><span class="role-badge ${roleClass}">${invite.role}</span></td>
                <td>${createdBy}</td>
                <td>${expiry}</td>
                <td><span class="status-badge ${statusClass}">${status}</span></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline-info" onclick="window.inviteManagement.copyInviteLink('${invite.invite_token}')">
                            <i class="fas fa-link"></i>
                        </button>
                    </div>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }
    
    async createInvite() {
        const email = document.getElementById('inviteEmail').value;
        const username = document.getElementById('inviteUsername').value;
        const fullName = document.getElementById('inviteFullName').value;
        const role = document.getElementById('inviteRole').value;
        
        try {
            console.log(`관리자 초대 생성 시도 - 이메일: ${email}, 사용자명: ${username}, 역할: ${role}`);
            const response = await fetch('/api/admin-invites/invite-admin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',  // 쿠키 포함
                body: JSON.stringify({ email, username, fullName, role })
            });
            console.log('초대 생성 API 응답 상태:', response.status);
            
            const data = await response.json();
            
            if (data.success) {
                alert(`초대가 생성되었습니다. 초대 링크: ${data.invite.inviteUrl}`);
                const modal = bootstrap.Modal.getInstance(document.getElementById('inviteModal'));
                modal.hide();
                
                // 폼 초기화
                document.getElementById('inviteForm').reset();
                
                // 초대 목록 다시 불러오기
                await this.loadInvites();
            } else {
                alert('초대 생성에 실패했습니다: ' + data.message);
            }
        } catch (error) {
            console.error('초대 생성 오류:', error);
            alert('초대 생성 중 오류가 발생했습니다.');
        }
    }
    
    copyInviteLink(token) {
        const inviteUrl = `${window.location.origin}/register-admin?token=${token}`;
        navigator.clipboard.writeText(inviteUrl).then(() => {
            alert('초대 링크가 복사되었습니다: ' + inviteUrl);
        }).catch(err => {
            console.error('링크 복사 실패:', err);
            // 폴백으로 prompt 사용
            prompt('초대 링크를 복사하세요:', inviteUrl);
        });
    }
}

// 초대 관리 인스턴스 생성
window.inviteManagement = new InviteManagement();
