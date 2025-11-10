/**
 * Customer Dashboard 페이지 라우트
 * 권한: admin, premium_user만 접근 가능
 */

const express = require('express');
const router = express.Router();
const path = require('path');
const { authenticateSession } = require('../../middleware/auth');
const { requireRole } = require('../../middleware/rbac');

/**
 * 고객 대시보드 메인 페이지
 * GET /customer/dashboard
 */
router.get('/dashboard', 
    authenticateSession,
    requireRole(['admin', 'premium_user']),
    (req, res) => {
        res.sendFile(path.join(__dirname, '../../../static/customer/index.html'));
    }
);

/**
 * 권한 없을 때 업그레이드 안내 페이지
 * GET /customer/upgrade-required
 */
router.get('/upgrade-required', 
    authenticateSession,  // 로그인은 필요
    (req, res) => {
        res.sendFile(path.join(__dirname, '../../../static/customer/upgrade-required.html'));
    }
);

/**
 * 권한 확인 API
 * GET /customer/check-access
 */
router.get('/check-access',
    authenticateSession,
    (req, res) => {
        const allowedRoles = ['admin', 'premium_user'];
        const userRoles = Array.isArray(req.user.roles) 
            ? req.user.roles 
            : (req.user.role ? [req.user.role] : []);
        
        const hasAccess = allowedRoles.some(role => userRoles.includes(role));
        
        res.json({
            success: true,
            hasAccess: hasAccess,
            userRole: req.user.role,
            userRoles: userRoles,
            requiredRoles: allowedRoles
        });
    }
);

module.exports = router;
