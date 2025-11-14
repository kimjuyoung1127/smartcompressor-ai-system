// Tesla & Starbucks inspired Mobile App JavaScript

class TeslaMobileApp {
    constructor() {
        this.isOnline = navigator.onLine;
        this.currentSection = 'dashboard';
        this.charts = {};
        this.notifications = [];
        this.paymentData = [];
        this.monitoringData = {
            temperature: [],
            efficiency: [],
            power: []
        };
        
        this.init();
    }

    async init() {
        console.log('🚀 Tesla Mobile App 초기화 시작');
        
        this.setupEventListeners();
        await this.initPWA();
        await this.loadInitialData();
        this.hideLoadingScreen();
        this.startRealTimeUpdates();
        
        console.log('✅ Tesla Mobile App 초기화 완료');
    }

    setupEventListeners() {
        // 네비게이션
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                this.navigateToSection(section);
            });
        });

        // 액션 버튼들
        document.getElementById('diagnoseBtn')?.addEventListener('click', () => {
            this.startDiagnosis();
        });

        document.getElementById('controlBtn')?.addEventListener('click', () => {
            this.showControlPanel();
        });

        // 모니터링 컨트롤
        document.querySelectorAll('.control-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchMonitoringType(e.currentTarget.dataset.type);
            });
        });

        // 탭 전환
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.currentTarget.dataset.tab);
            });
        });

        // 백 버튼들
        document.querySelectorAll('.back-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.navigateToSection('dashboard');
            });
        });

        // 온라인/오프라인 상태
        window.addEventListener('online', () => {
            this.handleOnlineStatus(true);
        });

        window.addEventListener('offline', () => {
            this.handleOnlineStatus(false);
        });

        // 푸시 알림 테스트
        document.getElementById('testDiagnosisNotification')?.addEventListener('click', () => {
            this.testPushNotification('diagnosis');
        });

        document.getElementById('testPaymentNotification')?.addEventListener('click', () => {
            this.testPushNotification('payment');
        });
    }

    async initPWA() {
        console.log('PWA 초기화 시작');
        
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.ready;
                console.log('✅ Service Worker 준비 완료:', registration);
                
                // 서비스 워커 상태 확인
                if (registration.active) {
                    console.log('✅ 활성화된 서비스 워커:', registration.active.state);
                }
                
                // 알림 권한 요청
                await this.requestNotificationPermission();
                
                // 백그라운드 동기화 등록
                if ('sync' in window.ServiceWorkerRegistration.prototype) {
                    console.log('백그라운드 동기화 지원 확인');
                    await registration.sync.register('offline-data-sync');
                    console.log('오프라인 데이터 동기화 등록 완료');
                }
            } catch (error) {
                console.error('❌ Service Worker 오류:', error);
                console.error('오류 세부 정보:', {
                    message: error.message,
                    stack: error.stack,
                    name: error.name
                });
            }
        } else {
            console.error('❌ Service Worker를 지원하지 않는 브라우저입니다.');
        }

        // PWA 설치 프롬프트
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('앱 설치 프롬프트 이벤트 발생');
            console.log('사용 가능한 플랫폼:', e.platforms);
            
            e.preventDefault();
            deferredPrompt = e;
            
            // 설치 가능 상태를 UI에 반영
            this.showInstallPrompt(deferredPrompt);
        });
        
        // 앱 설치 완료 이벤트
        window.addEventListener('appinstalled', () => {
            console.log('🎉 앱 설치 완료 이벤트 발생');
            this.showToast('앱이 성공적으로 설치되었습니다!', 'success');
        });
    }

    async requestNotificationPermission() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                console.log('✅ 푸시 알림 권한 허용됨');
                return true;
            } else {
                console.log('❌ 푸시 알림 권한 거부됨');
                return false;
            }
        }
        return false;
    }

    showInstallPrompt(deferredPrompt) {
        this.showToast('앱을 홈 화면에 설치하시겠습니까?', 'install');
    }

    async loadInitialData() {
        try {
            await this.loadDashboardData();
            await this.loadPaymentData();
            await this.loadNotificationData();
            this.initMonitoringChart();
        } catch (error) {
            console.error('❌ 초기 데이터 로드 실패:', error);
            this.showToast('데이터 로드에 실패했습니다', 'error');
        }
    }

    async loadDashboardData() {
        try {
            const response = await fetch('/api/dashboard/summary');
            if (response.ok) {
                const data = await response.json();
                this.updateDashboardUI(data);
            }
        } catch (error) {
            console.error('대시보드 데이터 로드 실패:', error);
            this.loadOfflineDashboardData();
        }
    }

    updateDashboardUI(data) {
        if (data.compressor_status) {
            this.updateCompressorStatus(data.compressor_status);
        }
        if (data.realtime_data) {
            this.updateRealtimeData(data.realtime_data);
        }
        if (data.payment_summary) {
            this.updatePaymentSummary(data.payment_summary);
        }
    }

    updateCompressorStatus(status) {
        const statusBadge = document.getElementById('compressorStatusBadge');
        const statusText = statusBadge?.querySelector('.status-text');
        const statusIndicator = statusBadge?.querySelector('.status-indicator');

        if (statusText && statusIndicator) {
            statusText.textContent = status.status;
            statusIndicator.className = `status-indicator ${status.status.toLowerCase()}`;
        }

        // 상태별 색상 적용
        if (status.status === '정상') {
            statusIndicator.style.background = 'var(--status-normal)';
        } else if (status.status === '경고') {
            statusIndicator.style.background = 'var(--status-warning)';
        } else if (status.status === '이상') {
            statusIndicator.style.background = 'var(--status-error)';
        }
    }

    updateRealtimeData(data) {
        const tempElement = document.getElementById('temperatureValue');
        if (tempElement && data.temperature) {
            tempElement.textContent = `${data.temperature}°C`;
        }

        const efficiencyElement = document.getElementById('efficiencyValue');
        if (efficiencyElement && data.efficiency) {
            efficiencyElement.textContent = `${Math.round(data.efficiency * 100)}%`;
        }

        const powerElement = document.getElementById('powerValue');
        if (powerElement && data.power_consumption) {
            powerElement.textContent = `${data.power_consumption}W`;
        }

        const vibrationElement = document.getElementById('vibrationValue');
        if (vibrationElement && data.vibration) {
            vibrationElement.textContent = data.vibration;
        }
    }

    updatePaymentSummary(summary) {
        const todayRevenue = document.getElementById('todayRevenue');
        if (todayRevenue && summary.today_revenue) {
            todayRevenue.textContent = `₩${summary.today_revenue.toLocaleString()}`;
        }

        const transactionCount = document.getElementById('transactionCount');
        if (transactionCount && summary.transaction_count) {
            transactionCount.textContent = `${summary.transaction_count}건`;
        }

        const averagePayment = document.getElementById('averagePayment');
        if (averagePayment && summary.average_payment) {
            averagePayment.textContent = `₩${Math.round(summary.average_payment).toLocaleString()}`;
        }
    }

    async loadPaymentData() {
        try {
            const response = await fetch('/api/mobile_app/payments');
            if (response.ok) {
                const data = await response.json();
                this.paymentData = data.payments || [];
                this.updatePaymentList();
            }
        } catch (error) {
            console.error('결제 데이터 로드 실패:', error);
        }
    }

    updatePaymentList() {
        const paymentList = document.getElementById('recentPaymentsList');
        if (!paymentList) return;

        paymentList.innerHTML = '';

        this.paymentData.slice(0, 5).forEach(payment => {
            const paymentItem = document.createElement('div');
            paymentItem.className = 'payment-item';
            paymentItem.innerHTML = `
                <div class="payment-info">
                    <div class="payment-method">${payment.method}</div>
                    <div class="payment-time">${this.formatTime(payment.timestamp)}</div>
                </div>
                <div class="payment-amount">₩${payment.amount.toLocaleString()}</div>
            `;
            paymentList.appendChild(paymentItem);
        });
    }

    async loadNotificationData() {
        try {
            const response = await fetch('/api/notifications/history');
            if (response.ok) {
                const data = await response.json();
                this.notifications = data.notifications || [];
                this.updateNotificationBadge();
                this.updateNotificationHistory();
            }
        } catch (error) {
            console.error('알림 데이터 로드 실패:', error);
        }
    }

    updateNotificationBadge() {
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            const unreadCount = this.notifications.filter(n => !n.read).length;
            badge.textContent = unreadCount;
            badge.style.display = unreadCount > 0 ? 'block' : 'none';
        }
    }

    updateNotificationHistory() {
        const historyList = document.getElementById('notificationHistory');
        if (!historyList) return;

        historyList.innerHTML = '';

        this.notifications.slice(0, 10).forEach(notification => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.innerHTML = `
                <div class="notification-content">
                    <h5>${notification.title}</h5>
                    <p>${notification.message}</p>
                    <small>${this.formatTime(notification.timestamp)}</small>
                </div>
                <div class="notification-status">
                    <i class="fas fa-${notification.read ? 'check' : 'circle'}"></i>
                </div>
            `;
            historyList.appendChild(historyItem);
        });
    }

    initMonitoringChart() {
        const ctx = document.getElementById('monitoringChart');
        if (!ctx) return;

        this.charts.monitoring = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '온도',
                    data: [],
                    borderColor: '#00D4AA',
                    backgroundColor: 'rgba(0, 212, 170, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        display: false
                    },
                    y: {
                        display: false
                    }
                },
                elements: {
                    point: {
                        radius: 0
                    }
                }
            }
        });

        this.loadMonitoringData('temperature');
    }

    switchMonitoringType(type) {
        document.querySelectorAll('.control-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-type="${type}"]`).classList.add('active');

        this.loadMonitoringData(type);
    }

    loadMonitoringData(type) {
        const chart = this.charts.monitoring;
        if (!chart) return;

        let color, label;
        switch (type) {
            case 'temperature':
                color = '#00D4AA';
                label = '온도';
                break;
            case 'efficiency':
                color = '#007AFF';
                label = '효율성';
                break;
            case 'power':
                color = '#FF9500';
                label = '전력';
                break;
        }

        chart.data.datasets[0].label = label;
        chart.data.datasets[0].borderColor = color;
        chart.data.datasets[0].backgroundColor = color + '20';
        chart.update();
    }

    async startDiagnosis() {
        console.log('🔍 진단 시작');
        
        this.navigateToSection('diagnosis');
        this.animateDiagnosisProgress();
        
        try {
            const response = await fetch('/api/ai/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    store_id: 'store_001',
                    analysis_type: 'compressor_door_status'
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.showDiagnosisResult(result);
            } else {
                throw new Error('진단 실패');
            }
        } catch (error) {
            console.error('진단 오류:', error);
            this.showDiagnosisError();
        }
    }

    animateDiagnosisProgress() {
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.querySelector('.progress-text');
        const description = document.querySelector('.progress-description');
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 100) progress = 100;
            
            progressFill.style.background = `conic-gradient(var(--sbux-light-green) ${progress * 3.6}deg, var(--tesla-gray-800) 0deg)`;
            progressText.textContent = `${Math.round(progress)}%`;
            
            if (progress >= 100) {
                clearInterval(interval);
                description.textContent = '진단 완료!';
            }
        }, 200);
    }

    showDiagnosisResult(result) {
        const progressDiv = document.getElementById('diagnosisProgress');
        const resultDiv = document.getElementById('diagnosisResult');
        
        if (progressDiv && resultDiv) {
            progressDiv.style.display = 'none';
            resultDiv.style.display = 'block';
            
            const status = result.status || '정상';
            const confidence = result.confidence || 0.95;
            
            document.getElementById('diagnosisStatus').textContent = status;
            document.getElementById('diagnosisConfidence').textContent = `${Math.round(confidence * 100)}%`;
            
            const resultIcon = resultDiv.querySelector('.result-icon i');
            if (status === '정상') {
                resultIcon.className = 'fas fa-check-circle';
                resultIcon.style.color = 'var(--status-normal)';
            } else if (status === '경고') {
                resultIcon.className = 'fas fa-exclamation-triangle';
                resultIcon.style.color = 'var(--status-warning)';
            } else {
                resultIcon.className = 'fas fa-times-circle';
                resultIcon.style.color = 'var(--status-error)';
            }
        }
    }

    showDiagnosisError() {
        this.showToast('진단 중 오류가 발생했습니다', 'error');
        this.navigateToSection('dashboard');
    }

    navigateToSection(section) {
        document.querySelectorAll('section').forEach(sec => {
            sec.style.display = 'none';
        });

        const targetSection = document.getElementById(`${section}Section`);
        if (targetSection) {
            targetSection.style.display = 'block';
        }

        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`)?.classList.add('active');

        this.currentSection = section;
    }

    switchTab(tabName) {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });

        document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');
        document.getElementById(`${tabName}Tab`)?.classList.add('active');
    }

    startRealTimeUpdates() {
        setInterval(() => {
            if (this.isOnline) {
                this.loadDashboardData();
                this.loadNotificationData();
            }
        }, 5000);

        setInterval(() => {
            this.updateMonitoringData();
        }, 1000);
    }

    updateMonitoringData() {
        const chart = this.charts.monitoring;
        if (!chart) return;

        const now = new Date();
        const timeLabel = now.toLocaleTimeString('ko-KR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        const newValue = Math.random() * 100;

        chart.data.labels.push(timeLabel);
        chart.data.datasets[0].data.push(newValue);

        if (chart.data.labels.length > 20) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.update('none');
    }

    handleOnlineStatus(isOnline) {
        this.isOnline = isOnline;
        
        const statusIndicator = document.getElementById('connectionStatus');
        if (statusIndicator) {
            const icon = statusIndicator.querySelector('i');
            if (isOnline) {
                icon.className = 'fas fa-wifi';
                icon.style.color = 'var(--status-normal)';
            } else {
                icon.className = 'fas fa-wifi-slash';
                icon.style.color = 'var(--status-error)';
                this.showOfflineModal();
            }
        }
    }

    showOfflineModal() {
        const modal = new bootstrap.Modal(document.getElementById('offlineModal'));
        modal.show();
    }

    async testPushNotification(type) {
        try {
            const response = await fetch('/api/notifications/test-push', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: type,
                    user_id: 'test_user'
                })
            });

            if (response.ok) {
                this.showToast('푸시 알림 테스트 완료', 'success');
            } else {
                throw new Error('푸시 알림 테스트 실패');
            }
        } catch (error) {
            console.error('푸시 알림 테스트 오류:', error);
            this.showToast('푸시 알림 테스트 실패', 'error');
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--tesla-gray-800);
            color: var(--tesla-white);
            padding: 1rem 1.5rem;
            border-radius: 8px;
            border: 1px solid var(--tesla-gray-700);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        const mainApp = document.getElementById('mainApp');
        
        if (loadingScreen && mainApp) {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
                mainApp.style.display = 'block';
                mainApp.style.animation = 'fadeIn 0.5s ease';
            }, 500);
        }
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) {
            return '방금 전';
        } else if (diff < 3600000) {
            return `${Math.floor(diff / 60000)}분 전`;
        } else if (diff < 86400000) {
            return `${Math.floor(diff / 3600000)}시간 전`;
        } else {
            return date.toLocaleDateString('ko-KR');
        }
    }

    loadOfflineDashboardData() {
        const offlineData = {
            compressor_status: {
                status: '정상',
                temperature: 25,
                efficiency: 0.95,
                power_consumption: 850,
                vibration: '정상'
            },
            payment_summary: {
                today_revenue: 125000,
                transaction_count: 23,
                average_payment: 5435
            }
        };

        this.updateDashboardUI(offlineData);
    }
}

// 앱 초기화
document.addEventListener('DOMContentLoaded', () => {
    window.teslaApp = new TeslaMobileApp();
});

// PWA 설치 이벤트
window.addEventListener('appinstalled', () => {
    console.log('✅ PWA가 설치되었습니다');
    window.teslaApp?.showToast('앱이 설치되었습니다!', 'success');
});

// 오프라인 데이터 동기화
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data.type === 'SYNC_COMPLETE') {
            console.log('✅ 오프라인 데이터 동기화 완료');
            window.teslaApp?.showToast('데이터가 동기화되었습니다', 'success');
        }
    });
}
