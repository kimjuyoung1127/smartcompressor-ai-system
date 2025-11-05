// static/js/ui/modal-manager.js
class ModalManager {
    async showLoginModal() {
        console.log('로그인 모달을 표시합니다.');
        
        // 기존 모달 제거
        const existingModal = document.getElementById('loginModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // 외부 모달 HTML 로드
        try {
            const response = await fetch('/static/landing-components/login-modal.html');
            // 응답 상태 확인
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const modalHtml = await response.text();
            
            // 새 모달 추가
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            // 모달 표시
            const loginModalElement = document.getElementById('loginModal');
            const modal = new bootstrap.Modal(loginModalElement);
            modal.show();
            
            // 폼 제출 이벤트 - handleLogin 함수가 존재하는 경우에만 연결
            // 모달이 표시될 때 폼 요소가 완전히 로드되기를 기다렸다가 이벤트 리스너를 연결
            setTimeout(() => {
                const loginForm = document.getElementById('loginForm');
                let loginHandler = null;
                
                // 전역 authManager가 존재하면 해당 인스턴스의 handleLogin 메서드 사용
                if (typeof authManager !== 'undefined' && typeof authManager.handleLogin === 'function') {
                    // authManager의 handleLogin 메서드를 호출하는 래퍼 함수
                    loginHandler = function(event) {
                        authManager.handleLogin(event);
                    };
                    console.log('authManager.handleLogin 메서드를 사용합니다');
                } 
                // 전역 handleLogin 함수가 존재하면 사용
                else if (typeof handleLogin === 'function') {
                    loginHandler = handleLogin;
                    console.log('전역 handleLogin 함수를 사용합니다');
                }
                
                if (loginForm && loginHandler) {
                    // 기존 이벤트 리스너가 있다면 제거
                    const newForm = loginForm.cloneNode(true);
                    loginForm.parentNode.replaceChild(newForm, loginForm);
                    newForm.addEventListener('submit', loginHandler);
                } else {
                    console.warn('handleLogin 함수를 찾을 수 없습니다. authManager:', typeof authManager, 'global handleLogin:', typeof handleLogin);
                }
            }, 100); // 짧은 지연 후 이벤트 리스너 연결
        } catch (error) {
            console.error('로그인 모달 로드 오류:', error);
            alert('로그인 모달을 로드하는 중 오류가 발생했습니다.');
        }
    }

    async showRegisterModal() {
        console.log('회원가입 모달을 표시합니다.');
        
        // 기존 모달 제거
        const existingModal = document.getElementById('registerModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // 외부 모달 HTML 로드
        try {
            const response = await fetch('/static/landing-components/register-modal.html');
            // 응답 상태 확인
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const modalHtml = await response.text();
            
            // 새 모달 추가
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            // 모달 표시
            const registerModalElement = document.getElementById('registerModal');
            const modal = new bootstrap.Modal(registerModalElement);
            modal.show();
            
            // 폼 제출 이벤트 - handleRegister 함수가 존재하는 경우에만 연결
            // 모달이 표시될 때 폼 요소가 완전히 로드되기를 기다렸다가 이벤트 리스너를 연결
            setTimeout(() => {
                const registerForm = document.getElementById('registerForm');
                let registerHandler = null;
                
                // 전역 handleRegister 함수가 존재하면 사용
                if (typeof handleRegister === 'function') {
                    registerHandler = handleRegister;
                    console.log('전역 handleRegister 함수를 사용합니다');
                }
                
                if (registerForm && registerHandler) {
                    // 기존 이벤트 리스너가 있다면 제거
                    const newForm = registerForm.cloneNode(true);
                    registerForm.parentNode.replaceChild(newForm, registerForm);
                    newForm.addEventListener('submit', registerHandler);
                } else {
                    console.warn('handleRegister 함수를 찾을 수 없습니다:', typeof handleRegister);
                }
            }, 100); // 짧은 지연 후 이벤트 리스너 연결
        } catch (error) {
            console.error('회원가입 모달 로드 오류:', error);
            alert('회원가입 모달을 로드하는 중 오류가 발생했습니다.');
        }
    }

    showPasswordResetModal() {
        console.log('비밀번호 재설정 모달을 표시합니다.');
        
        // Show the modal that's already in the page
        const modal = new bootstrap.Modal(document.getElementById('passwordResetModal'));
        modal.show();
    }
}

// 회원가입 처리
async function handleRegister(event) {
    console.log('회원가입 시작:', event);
    event.preventDefault();
    
    console.log('폼 데이터 수집 시작');
    const firstName = document.getElementById('registerName').value;
    const lastName = document.getElementById('registerLastName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const passwordConfirm = document.getElementById('registerPasswordConfirm').value;
    const phone = document.getElementById('registerPhone').value;
    const company = document.getElementById('registerCompany').value;
    const termsAgree = document.getElementById('termsAgree').checked;
    const marketingAgree = document.getElementById('marketingAgree').checked;
    
    console.log('수집된 데이터:', { 
        firstName, 
        lastName, 
        email, 
        password: password ? '***' : '', 
        passwordConfirm: passwordConfirm ? '***' : '', 
        phone, 
        company, 
        termsAgree, 
        marketingAgree 
    });
    
    // Validation
    if (!firstName || !lastName || !email || !password) {
        console.log('필수 입력 항목 검증 실패');
        alert('필수 입력 항목을 모두 입력해주세요.');
        return;
    }
    
    if (password !== passwordConfirm) {
        console.log('비밀번호 확인 불일치');
        alert('비밀번호와 비밀번호 확인이 일치하지 않습니다.');
        return;
    }
    
    if (password.length < 8) {
        console.log('비밀번호 길이 검증 실패');
        alert('비밀번호는 최소 8자 이상이어야 합니다.');
        return;
    }
    
    if (!termsAgree) {
        console.log('약관 동의 미체크');
        alert('서비스 이용 약관에 동의해주세요.');
        return;
    }
    
    console.log('모든 검증 통과, 사용자 데이터 구성 중');
    
    try {
        // 사용자 데이터 구성 - register-modal.html의 실제 필드에 맞게 구성
        const userData = {
            username: firstName + lastName || email.split('@')[0], // 이름 조합 또는 이메일 기반
            email, 
            password, // 비밀번호는 authRoutes.js에서 해시 처리됨
            full_name: firstName + ' ' + lastName,
            phone: phone || null,
            position: '', // register modal에는 없음
            company: company || '',
            industry: '', // register modal에는 없음
            company_size: '', // register modal에는 없음
            company_email: '', // register modal에는 없음
            address: '', // register modal에는 없음
            purpose: [], // register modal에는 없음
            budget: '', // register modal에는 없음
            timeline: '', // register modal에는 없음
            device_count: '', // register modal에는 없음
            email_alerts: true, // 기본값
            email_newsletter: marketingAgree || false, // 마케팅 수신 동의
            sms_alerts: false, // 기본값
            kakao_alerts: false, // 기본값
            privacy_agree: termsAgree, // 개인정보 처리 방침 동의
            terms_agree: termsAgree,   // 서비스 이용 약관 동의
            marketing_agree: marketingAgree || false, // 마케팅 정보 수신 동의
            role: 'user'  // 기본 역할
        };
        
        console.log('전송할 사용자 데이터:', userData);

        console.log('API 호출 시작: /api/auth/register');
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        console.log('API 응답 수신:', response.status);
        const data = await response.json();
        console.log('API 응답 데이터:', data);

        if (data.success) {
            console.log('회원가입 성공');
            // 모달 닫기
            const modal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
            if (modal) {
                modal.hide();
            }
            
            alert('회원가입 성공! 로그인해주세요.');
            // 전역 등록된 modalManager 인스턴스가 있을 경우 사용
            if (typeof modalManager !== 'undefined') {
                console.log('modalManager를 통해 로그인 모달 표시 시도');
                modalManager.showLoginModal();
            } else {
                // 또는 직접 로그인 모달 표시 함수가 있는 경우 호출
                if (typeof showLoginModal === 'function') {
                    console.log('전역 showLoginModal 함수 호출');
                    showLoginModal();
                } else {
                    console.log('showLoginModal 함수를 찾을 수 없음');
                }
            }
        } else {
            console.log('회원가입 실패:', data.message || '알 수 없는 오류');
            alert(data.message || '회원가입 실패');
        }
    } catch (error) {
        console.error('회원가입 오류:', error);
        alert('회원가입 중 오류가 발생했습니다.');
    }
}

// 비밀번호 재설정 처리
async function handlePasswordReset(event) {
    event.preventDefault();
    
    const email = document.getElementById('resetEmail').value;
    
    if (!email) {
        alert('이메일 주소를 입력해주세요.');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/forgot-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (data.success) {
            // 모달 닫기
            const modal = bootstrap.Modal.getInstance(document.getElementById('passwordResetModal'));
            if (modal) {
                modal.hide();
            }
            
            alert('비밀번호 재설정 링크가 이메일로 전송되었습니다.');
            showLoginModal();
        } else {
            alert(data.message || '비밀번호 재설정 요청 실패');
        }
    } catch (error) {
        console.error('비밀번호 재설정 오류:', error);
        alert('비밀번호 재설정 요청 중 오류가 발생했습니다.');
    }
}

// OAuth 로그인 처리
function googleLogin() {
    alert('구글 로그인 기능은 현재 개발 중입니다. 이메일 로그인을 이용해주세요.');
    // 실제 구현은 OAuth 라이브러리를 사용하여 구글 로그인 창을 띄우는 방식으로 구현
}

// 로그인 성공 모달 표시
function showLoginSuccessModal() {
    // 기존 모달 제거
    const existingModal = document.getElementById('loginSuccessModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 성공 모달 생성
    const modalHTML = `
        <div class="modal fade" id="loginSuccessModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0 shadow-lg">
                    <div class="modal-body text-center p-5">
                        <div class="mb-4">
                            <div class="success-animation mb-3">
                                <i class="fas fa-check-circle text-success" style="font-size: 4rem;"></i>
                            </div>
                            <h3 class="text-success mb-3">로그인 성공!</h3>
                            <p class="text-muted mb-4">Signalcraft AI 진단 서비스에 오신 것을 환영합니다.</p>
                        </div>
                        
                        <div class="row g-3 mb-4">
                            <div class="col-6">
                                <div class="card border-0 bg-light">
                                    <div class="card-body text-center">
                                        <i class="fas fa-brain text-primary mb-2" style="font-size: 2rem;"></i>
                                        <h6>AI 진단</h6>
                                        <small class="text-muted">압축기 상태 분석</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="card border-0 bg-light">
                                    <div class="card-body text-center">
                                        <i class="fas fa-chart-line text-success mb-2" style="font-size: 2rem;"></i>
                                        <h6>실시간 모니터링</h6>
                                        <small class="text-muted">24시간 감시</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary btn-lg" onclick="startDiagnosis()">
                                <i class="fas fa-play me-2"></i>진단 시작하기
                            </button>
                            <button class="btn btn-outline-secondary" onclick="closeLoginSuccessModal()">
                                나중에 시작하기
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 모달 표시
    const modal = new bootstrap.Modal(document.getElementById('loginSuccessModal'));
    modal.show();
    
    // 애니메이션 효과
    setTimeout(() => {
        const checkIcon = document.querySelector('#loginSuccessModal .fa-check-circle');
        if (checkIcon) {
            checkIcon.style.animation = 'bounceIn 0.6s ease-out';
        }
    }, 100);
}

// 로그인 성공 모달 닫기
function closeLoginSuccessModal() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('loginSuccessModal'));
    if (modal) {
        modal.hide();
    }
}

// 전역 이벤트 리스너 설정
document.addEventListener('DOMContentLoaded', function() {
    // 비밀번호 재설정 폼 제출 이벤트
    const passwordResetForm = document.getElementById('passwordResetForm');
    if (passwordResetForm) {
        passwordResetForm.addEventListener('submit', handlePasswordReset);
    }
});