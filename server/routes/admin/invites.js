const express = require('express');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const router = express.Router();
const DatabaseService = require('../../../database/database_service');
const { requireAdmin } = require('../../middleware/rbac');
const { authenticateSession } = require('../../middleware/auth');

const db = new DatabaseService();

// 모든 라우트에 세션 인증 미들웨어 적용
router.use(authenticateSession);

// 관리자 전용: 관리자 초대 링크 생성
router.post('/invite-admin', requireAdmin, async (req, res) => {
    try {
        const { email, username, fullName, role = 'admin' } = req.body;
        const validRoles = ['admin', 'user', 'labeler', 'owner'];

        if (!validRoles.includes(role)) {
            return res.status(400).json({ success: false, message: `유효하지 않은 역할입니다. 가능한 값: ${validRoles.join(', ')}` });
        }

        if (!email || !username) {
            return res.status(400).json({ success: false, message: '이메일과 사용자명은 필수입니다.' });
        }

        // 이메일/사용자명 중복 확인
        const existingUser = await db.getUserByEmail(email);
        if (existingUser) {
            return res.status(409).json({ success: false, message: '이미 존재하는 이메일입니다.' });
        }

        const existingUsername = await db.getUserByUsername(username);
        if (existingUsername) {
            return res.status(409).json({ success: false, message: '이미 존재하는 사용자명입니다.' });
        }

        // 초대 토큰 생성
        const inviteToken = crypto.randomBytes(32).toString('hex');
        const expiry = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24시간 유효

        // 초대 정보 저장
        const client = await db.pool.connect();
        try {
            const result = await client.query(`
                INSERT INTO admin_invites (email, username, full_name, role, invite_token, expiry, created_by)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING *
            `, [email, username, fullName || username, role, inviteToken, expiry, req.user.userId]);

            // 실제 사용자 생성은 초대 링크를 통해 이루어짐
            // 이메일 전송 대신 직접 토큰을 반환하여 사용자가 사용할 수 있도록 함
            return res.json({
                success: true,
                message: '관리자 초대가 생성되었습니다.',
                invite: {
                    email: result.rows[0].email,
                    username: result.rows[0].username,
                    role: result.rows[0].role,
                    inviteToken: result.rows[0].invite_token,
                    expiry: result.rows[0].expiry,
                    inviteUrl: `${process.env.BASE_URL || 'http://localhost:3000'}/register-admin?token=${result.rows[0].invite_token}`
                }
            });
        } finally {
            client.release();
        }
    } catch (error) {
        console.error('관리자 초대 생성 오류:', error);
        res.status(500).json({ success: false, message: '관리자 초대 생성 중 오류가 발생했습니다.' });
    }
});

// 관리자 초대 토큰으로 등록 처리 (로그인 필요 없음)
router.post('/register-admin', async (req, res) => {
    try {
        const { token, password, confirmPassword } = req.body;

        if (!token) {
            return res.status(400).json({ success: false, message: '초대 토큰이 필요합니다.' });
        }

        if (password !== confirmPassword) {
            return res.status(400).json({ success: false, message: '비밀번호가 일치하지 않습니다.' });
        }

        if (password.length < 6) {
            return res.status(400).json({ success: false, message: '비밀번호는 최소 6자 이상이어야 합니다.' });
        }

        // 유효한 초대 토큰 확인
        const client = await db.pool.connect();
        try {
            const inviteResult = await client.query(
                'SELECT * FROM admin_invites WHERE invite_token = $1 AND expiry > NOW() AND is_used = false',
                [token]
            );

            if (inviteResult.rows.length === 0) {
                return res.status(400).json({ success: false, message: '유효하지 않거나 만료된 초대 토큰입니다.' });
            }

            const invite = inviteResult.rows[0];

            // 비밀번호 해시
            const saltRounds = 10;
            const passwordHash = await bcrypt.hash(password, saltRounds);

            // 사용자 생성
            const newUserResult = await client.query(`
                INSERT INTO users (username, email, password_hash, role, full_name)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, username, email, role, created_at
            `, [invite.username, invite.email, passwordHash, invite.role, invite.full_name]);

            // 초대 토큰 사용 처리
            await client.query('UPDATE admin_invites SET is_used = true, used_at = NOW() WHERE id = $1', [invite.id]);

            res.json({
                success: true,
                message: '관리자 등록이 완료되었습니다.',
                user: {
                    id: newUserResult.rows[0].id,
                    username: newUserResult.rows[0].username,
                    email: newUserResult.rows[0].email,
                    role: newUserResult.rows[0].role
                }
            });
        } finally {
            client.release();
        }
    } catch (error) {
        console.error('관리자 등록 오류:', error);
        res.status(500).json({ success: false, message: '관리자 등록 중 오류가 발생했습니다.' });
    }
});

// 관리자 전용: 초대 목록 조회
router.get('/invites', requireAdmin, async (req, res) => {
    try {
        const client = await db.pool.connect();
        try {
            // 최근 50개의 초대 내역 조회
            const result = await client.query(`
                SELECT 
                    ai.*, 
                    u.username as created_by_username
                FROM admin_invites ai
                LEFT JOIN users u ON ai.created_by = u.id
                ORDER BY ai.created_at DESC
                LIMIT 50
            `);

            res.json({ success: true, invites: result.rows });
        } finally {
            client.release();
        }
    } catch (error) {
        console.error('초대 목록 조회 오류:', error);
        res.status(500).json({ success: false, message: '초대 목록 조회 중 오류가 발생했습니다.' });
    }
});

// 관리자 전용: 사용자 생성 (기존 등록 방식과는 별도로 즉시 계정 생성)
router.post('/create-user', requireAdmin, async (req, res) => {
    try {
        const { username, email, password, role = 'user', fullName } = req.body;
        const validRoles = ['admin', 'user', 'labeler', 'owner'];

        if (!validRoles.includes(role)) {
            return res.status(400).json({ success: false, message: `유효하지 않은 역할입니다. 가능한 값: ${validRoles.join(', ')}` });
        }

        if (!email || !username || !password) {
            return res.status(400).json({ success: false, message: '이메일, 사용자명, 비밀번호는 필수입니다.' });
        }

        // 이메일/사용자명 중복 확인
        const existingUser = await db.getUserByEmail(email);
        if (existingUser) {
            return res.status(409).json({ success: false, message: '이미 존재하는 이메일입니다.' });
        }

        const existingUsername = await db.getUserByUsername(username);
        if (existingUsername) {
            return res.status(409).json({ success: false, message: '이미 존재하는 사용자명입니다.' });
        }

        // 비밀번호 해시
        const saltRounds = 10;
        const passwordHash = await bcrypt.hash(password, saltRounds);

        // 사용자 생성
        const newUser = await db.createUser({
            username,
            email,
            password_hash: passwordHash,
            full_name: fullName || username,
            role,
            phone: null,
            additional_info: {}
        });

        res.json({
            success: true,
            message: `${role} 사용자가 생성되었습니다.`,
            user: {
                id: newUser.id,
                username: newUser.username,
                email: newUser.email,
                role: newUser.role,
                created_at: newUser.created_at
            }
        });
    } catch (error) {
        console.error('사용자 생성 오류:', error);
        res.status(500).json({ success: false, message: '사용자 생성 중 오류가 발생했습니다.' });
    }
});

// 데이터베이스에 초대 테이블 생성을 위한 초기화 (필요시)
db.initializeAdminInviteTable = async function() {
    const client = await this.pool.connect();
    try {
        // admin_invites 테이블 생성
        await client.query(`
            CREATE TABLE IF NOT EXISTS admin_invites (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                username VARCHAR(50) NOT NULL,
                full_name VARCHAR(100),
                role VARCHAR(20) DEFAULT 'admin',
                invite_token VARCHAR(255) UNIQUE NOT NULL,
                expiry TIMESTAMPTZ NOT NULL,
                is_used BOOLEAN DEFAULT false,
                used_at TIMESTAMPTZ,
                created_by INTEGER REFERENCES users(id),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // 인덱스 생성
        await client.query(`
            CREATE INDEX IF NOT EXISTS idx_admin_invites_token ON admin_invites(invite_token);
            CREATE INDEX IF NOT EXISTS idx_admin_invites_expiry ON admin_invites(expiry);
            CREATE INDEX IF NOT EXISTS idx_admin_invites_used ON admin_invites(is_used);
        `);
    } finally {
        client.release();
    }
};

// 애플리케이션 시작 시 테이블 확인
db.initializeAdminInviteTable().catch(console.error);

module.exports = router;