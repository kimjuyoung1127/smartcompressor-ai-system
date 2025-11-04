/**
 * RBAC (Role-Based Access Control) 미들웨어
 * 역할 기반 접근 제어를 위한 미들웨어
 */

/**
 * 특정 역할을 가진 사용자만 접근 가능하도록 제한
 * @param {Array<string>} allowedRoles - 허용할 역할 배열 (예: ['admin', 'labeler'])
 * @returns {Function} Express 미들웨어 함수
 */
function requireRole(allowedRoles) {
    return async (req, res, next) => {
        try {
            // 세션에서 사용자 정보 확인
            if (!req.user) {
                return res.status(401).json({ 
                    success: false,
                    error: 'Unauthorized',
                    message: '로그인이 필요합니다.' 
                });
            }

            // 사용자의 역할 확인 (roles 배열 또는 단일 role)
            const userRoles = Array.isArray(req.user.roles) 
                ? req.user.roles 
                : (req.user.role ? [req.user.role] : []);
            
            // 허용된 역할 중 하나라도 가지고 있는지 확인
            const hasPermission = allowedRoles.some(role => userRoles.includes(role));
            
            if (!hasPermission) {
                return res.status(403).json({ 
                    success: false,
                    error: 'Forbidden',
                    message: '접근 권한이 없습니다. 필요한 권한: ' + allowedRoles.join(', '),
                    userRoles: userRoles
                });
            }
            
            // 권한이 있으면 다음 미들웨어로
            next();
        } catch (error) {
            console.error('RBAC 미들웨어 오류:', error);
            return res.status(500).json({ 
                success: false,
                error: 'Internal Server Error',
                message: '권한 확인 중 오류가 발생했습니다.' 
            });
        }
    };
}

/**
 * 관리자만 접근 가능하도록 제한
 */
function requireAdmin(req, res, next) {
    return requireRole(['admin'])(req, res, next);
}

/**
 * 라벨러 또는 관리자만 접근 가능하도록 제한
 */
function requireLabeler(req, res, next) {
    return requireRole(['labeler', 'admin'])(req, res, next);
}

/**
 * 점주(owner) 또는 관리자만 접근 가능하도록 제한
 */
function requireOwner(req, res, next) {
    return requireRole(['owner', 'admin'])(req, res, next);
}

module.exports = {
    requireRole,
    requireAdmin,
    requireLabeler,
    requireOwner
};
