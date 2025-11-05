const express = require('express');
const router = express.Router();
const DatabaseService = require('../../services/database_service');
const { requireAdmin } = require('../middleware/rbac');

const db = new DatabaseService();

// 관리자 전용: 모든 사용자 목록 조회
router.get('/users', requireAdmin, async (req, res) => {
    try {
        const result = await db.getAllUsers();
        res.json({ success: true, users: result });
    } catch (error) {
        console.error('사용자 목록 조회 오류:', error);
        res.status(500).json({ success: false, message: '사용자 목록 조회 중 오류가 발생했습니다.' });
    }
});

// 관리자 전용: 사용자 역할 변경
router.patch('/users/:userId/role', requireAdmin, async (req, res) => {
    try {
        const userId = parseInt(req.params.userId);
        const { role } = req.body;
        const validRoles = ['admin', 'user', 'labeler', 'owner'];

        if (!validRoles.includes(role)) {
            return res.status(400).json({ success: false, message: `유효하지 않은 역할입니다. 가능한 값: ${validRoles.join(', ')}` });
        }

        // 사용자 확인
        const user = await db.getUserById(userId);
        if (!user) {
            return res.status(404).json({ success: false, message: '사용자를 찾을 수 없습니다.' });
        }

        // 역할 변경
        const updatedUser = await db.updateUserRole(userId, role);

        res.json({ success: true, message: `사용자 ${updatedUser.username}의 역할이 ${role}로 변경되었습니다.`, user: updatedUser });
    } catch (error) {
        console.error('사용자 역할 변경 오류:', error);
        res.status(500).json({ success: false, message: '사용자 역할 변경 중 오류가 발생했습니다.' });
    }
});

// 관리자 전용: 사용자 계정 활성화/비활성화
router.patch('/users/:userId/status', requireAdmin, async (req, res) => {
    try {
        const userId = parseInt(req.params.userId);
        const { isActive } = req.body;

        if (typeof isActive !== 'boolean') {
            return res.status(400).json({ success: false, message: 'isActive 값은 true 또는 false여야 합니다.' });
        }

        // 사용자 확인
        const user = await db.getUserById(userId);
        if (!user) {
            return res.status(404).json({ success: false, message: '사용자를 찾을 수 없습니다.' });
        }

        // 계정 상태 변경
        const updatedUser = await db.updateUserStatus(userId, isActive);

        res.json({ success: true, message: `사용자 ${updatedUser.username}의 계정 상태가 ${isActive ? '활성화' : '비활성화'} 되었습니다.`, user: updatedUser });
    } catch (error) {
        console.error('사용자 상태 변경 오류:', error);
        res.status(500).json({ success: false, message: '사용자 상태 변경 중 오류가 발생했습니다.' });
    }
});

// 관리자 전용: 사용자 정보 조회
router.get('/users/:userId', requireAdmin, async (req, res) => {
    try {
        const userId = parseInt(req.params.userId);
        const user = await db.getUserById(userId);

        if (!user) {
            return res.status(404).json({ success: false, message: '사용자를 찾을 수 없습니다.' });
        }

        // 민감한 정보 제외하고 반환
        const { password_hash, ...safeUser } = user;
        res.json({ success: true, user: safeUser });
    } catch (error) {
        console.error('사용자 정보 조회 오류:', error);
        res.status(500).json({ success: false, message: '사용자 정보 조회 중 오류가 발생했습니다.' });
    }
});

module.exports = router;