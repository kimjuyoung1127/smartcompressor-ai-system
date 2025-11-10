/**
 * API 통신 레이어
 * 모든 API 요청을 처리하고 에러를 일관성 있게 관리
 */

class APIError extends Error {
    constructor(code, message, details, statusCode) {
        super(message);
        this.name = 'APIError';
        this.code = code;
        this.details = details;
        this.statusCode = statusCode;
        this.timestamp = new Date().toISOString();
    }
}

class API {
    constructor() {
        this.baseURL = CONFIG.API_BASE_URL;
        this.timeout = CONFIG.API_TIMEOUT;
    }
    
    /**
     * HTTP 요청 실행
     */
    async request(endpoint, options = {}) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), this.timeout);
        
        try {
            const url = endpoint.startsWith('http') ? endpoint : `${this.baseURL}${endpoint}`;
            
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            clearTimeout(timeout);
            
            // 응답 파싱
            const data = await response.json();
            
            // 권한 오류 처리 (403 Forbidden)
            if (response.status === 403) {
                Utils.log.warn('403 Forbidden - 권한 없음');
                window.location.href = CONFIG.PAGES.UPGRADE;
                throw new APIError(
                    'PERMISSION_DENIED',
                    '접근 권한이 없습니다',
                    data.error?.message,
                    403
                );
            }
            
            // 인증 오류 처리 (401 Unauthorized)
            if (response.status === 401) {
                Utils.log.warn('401 Unauthorized - 로그인 필요');
                window.location.href = CONFIG.AUTH.LOGIN_URL;
                throw new APIError(
                    'UNAUTHORIZED',
                    '로그인이 필요합니다',
                    null,
                    401
                );
            }
            
            // 서버 에러 처리 (500+)
            if (response.status >= 500) {
                throw new APIError(
                    'SERVER_ERROR',
                    '서버 오류가 발생했습니다',
                    data.error?.message,
                    response.status
                );
            }
            
            // 성공하지 않은 응답
            if (!data.success) {
                throw new APIError(
                    data.error?.code || 'UNKNOWN_ERROR',
                    data.error?.message || '알 수 없는 오류가 발생했습니다',
                    data.error?.details,
                    response.status
                );
            }
            
            return {
                success: true,
                data: data.data,
                meta: data.meta,
                hasData: data.meta?.has_data !== false
            };
            
        } catch (error) {
            clearTimeout(timeout);
            
            // AbortError (타임아웃)
            if (error.name === 'AbortError') {
                throw new APIError(
                    'TIMEOUT',
                    '요청 시간이 초과되었습니다',
                    '서버 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요.'
                );
            }
            
            // APIError는 그대로 throw
            if (error instanceof APIError) {
                throw error;
            }
            
            // 네트워크 오류
            throw new APIError(
                'NETWORK_ERROR',
                '네트워크 연결을 확인해주세요',
                error.message
            );
        }
    }
    
    /**
     * GET 요청
     */
    async get(endpoint, params = {}) {
        const queryString = Object.keys(params).length > 0 
            ? '?' + Utils.objectToQueryString(params)
            : '';
        
        return this.request(endpoint + queryString, {
            method: 'GET'
        });
    }
    
    /**
     * POST 요청
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    /**
     * PUT 요청
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    /**
     * DELETE 요청
     */
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
    
    /**
     * 파일 업로드 (multipart/form-data)
     */
    async upload(endpoint, formData) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), this.timeout * 3); // 파일 업로드는 더 긴 타임아웃
        
        try {
            const url = `${this.baseURL}${endpoint}`;
            
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                signal: controller.signal,
                credentials: 'include'
                // Content-Type은 자동 설정됨
            });
            
            clearTimeout(timeout);
            
            const data = await response.json();
            
            if (!response.ok || !data.success) {
                throw new APIError(
                    data.error?.code || 'UPLOAD_ERROR',
                    data.error?.message || '파일 업로드 실패',
                    data.error?.details,
                    response.status
                );
            }
            
            return {
                success: true,
                data: data.data
            };
            
        } catch (error) {
            clearTimeout(timeout);
            
            if (error.name === 'AbortError') {
                throw new APIError(
                    'TIMEOUT',
                    '업로드 시간이 초과되었습니다'
                );
            }
            
            if (error instanceof APIError) {
                throw error;
            }
            
            throw new APIError(
                'UPLOAD_ERROR',
                '파일 업로드 중 오류가 발생했습니다',
                error.message
            );
        }
    }
}

// 전역 API 인스턴스
window.api = new API();
window.APIError = APIError;
