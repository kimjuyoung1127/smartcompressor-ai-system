const { Pool } = require('pg');
require('dotenv').config();

// PostgreSQL 연결 설정
const pool = new Pool({
    user: process.env.DB_USER || 'postgres',
    host: process.env.DB_HOST || 'localhost',
    database: process.env.DB_NAME || 'smartcompressor_ai',
    password: process.env.DB_PASSWORD || 'signalcraft6898',
    port: process.env.DB_PORT || 5432,
});

/**
 * 사용자 역할 변경 함수
 * @param {string} identifier - 사용자명 또는 이메일
 * @param {string} newRole - 변경할 역할 ('admin', 'user', 'labeler', 등)
 */
async function updateUserRole(identifier, newRole) {
    const validRoles = ['admin', 'user', 'labeler', 'owner'];
    
    if (!validRoles.includes(newRole)) {
        throw new Error(`Invalid role. Valid roles are: ${validRoles.join(', ')}`);
    }

    const client = await pool.connect();
    try {
        // 사용자 검색 (username 또는 email로)
        const userResult = await client.query(
            `SELECT id, username, email, role FROM users WHERE username = $1 OR email = $1`,
            [identifier]
        );

        if (userResult.rows.length === 0) {
            throw new Error(`User with identifier "${identifier}" not found.`);
        }

        const user = userResult.rows[0];

        // 역할 변경
        const updateResult = await client.query(
            'UPDATE users SET role = $1 WHERE id = $2 RETURNING *',
            [newRole, user.id]
        );

        console.log(`Successfully updated user "${user.username}" (${user.email}) role from "${user.role}" to "${newRole}"`);
        return updateResult.rows[0];
    } finally {
        client.release();
    }
}

/**
 * 모든 사용자 목록 조회
 */
async function getAllUsers() {
    const client = await pool.connect();
    try {
        const result = await client.query(
            'SELECT id, username, email, role, is_active, created_at, last_login FROM users ORDER BY created_at DESC'
        );
        return result.rows;
    } finally {
        client.release();
    }
}

/**
 * 새로운 관리자 사용자 생성
 * @param {string} username - 사용자명
 * @param {string} email - 이메일
 * @param {string} password - 비밀번호 (해시되지 않은 상태)
 */
async function createAdminUser(username, email, password) {
    const bcrypt = require('bcryptjs');
    const client = await pool.connect();
    
    try {
        // 이메일/사용자명 중복 확인
        const existingUser = await client.query(
            'SELECT id FROM users WHERE username = $1 OR email = $1',
            [username]
        );
        
        if (existingUser.rows.length > 0) {
            throw new Error(`User with username "${username}" already exists.`);
        }

        // 이메일 중복 확인
        const existingEmail = await client.query(
            'SELECT id FROM users WHERE email = $1',
            [email]
        );
        
        if (existingEmail.rows.length > 0) {
            throw new Error(`User with email "${email}" already exists.`);
        }

        // 비밀번호 해시
        const saltRounds = 10;
        const passwordHash = await bcrypt.hash(password, saltRounds);

        // 관리자 사용자 생성
        const result = await client.query(
            `INSERT INTO users (username, email, password_hash, role, full_name) 
             VALUES ($1, $2, $3, 'admin', $4) RETURNING id, username, email, role, created_at`,
            [username, email, passwordHash, username]
        );

        console.log(`Successfully created admin user: "${username}" (${email})`);
        return result.rows[0];
    } finally {
        client.release();
    }
}

// 명령줄 인수 처리
async function main() {
    const args = process.argv.slice(2);
    const command = args[0];

    if (!command) {
        console.log('Usage:');
        console.log('  node admin_user_manager.js list                           # 모든 사용자 목록 조회');
        console.log('  node admin_user_manager.js promote <identifier> <role>     # 사용자 역할 변경');
        console.log('  node admin_user_manager.js create-admin <username> <email> <password>  # 관리자 생성');
        console.log('');
        console.log('Examples:');
        console.log('  node admin_user_manager.js promote johndoe admin');
        console.log('  node admin_user_manager.js promote "johndoe@gmail.com" labeler');
        console.log('  node admin_user_manager.js create-admin admin admin@example.com password123');
        return;
    }

    try {
        switch (command) {
            case 'list':
                const users = await getAllUsers();
                console.log('All users:');
                console.table(users.map(u => ({
                    id: u.id,
                    username: u.username,
                    email: u.email,
                    role: u.role,
                    active: u.is_active,
                    last_login: u.last_login
                })));
                break;

            case 'promote':
                if (args.length < 3) {
                    console.error('Usage: node admin_user_manager.js promote <identifier> <role>');
                    return;
                }
                const identifier = args[1];
                const newRole = args[2];
                await updateUserRole(identifier, newRole);
                break;

            case 'create-admin':
                if (args.length < 4) {
                    console.error('Usage: node admin_user_manager.js create-admin <username> <email> <password>');
                    return;
                }
                const username = args[1];
                const email = args[2];
                const password = args[3];
                await createAdminUser(username, email, password);
                break;

            default:
                console.error(`Unknown command: ${command}`);
                break;
        }
    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        await pool.end();
    }
}

// 이 파일이 직접 실행될 때만 main 함수 호출
if (require.main === module) {
    main();
}

module.exports = {
    updateUserRole,
    getAllUsers,
    createAdminUser
};