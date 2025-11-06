const DatabaseService = require('../../database/database_service');
const db = new DatabaseService();

// 세션 검증 미들웨어
const authenticateSession = async (req, res, next) => {
    try {
        const sessionId = req.cookies.sessionId;

        if (!sessionId) {
            return res.status(401).json({ 
                success: false, 
                message: '로그인이 필요합니다.' 
            });
        }

        const session = await db.getSession(sessionId);
        
        if (!session) {
            return res.status(401).json({ 
                success: false, 
                message: '유효하지 않은 세션입니다.' 
            });
        }

        // sess 데이터에서 사용자 정보 추출
        const sessData = session.sess;
        
        req.user = {
            userId: sessData.user_id || sessData.user?.id,
            username: sessData.user?.username,
            email: sessData.user?.email,
            role: sessData.user?.role,
            roles: sessData.user?.roles || [sessData.user?.role]
        };
        next();
    } catch (error) {
        console.error('세션 검증 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '세션 검증 중 오류가 발생했습니다.' 
        });
    }
};

module.exports = {
    authenticateSession
};