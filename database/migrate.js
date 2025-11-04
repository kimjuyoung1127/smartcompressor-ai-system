/**
 * 데이터베이스 마이그레이션 실행 스크립트
 * 
 * 사용법:
 *   node database/migrate.js
 *   node database/migrate.js --rollback
 *   node database/migrate.js --status
 */

const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

class MigrationRunner {
    constructor() {
        this.pool = new Pool({
            user: process.env.DB_USER || 'postgres',
            host: process.env.DB_HOST || 'localhost',
            database: process.env.DB_NAME || 'smartcompressor_ai',
            password: process.env.DB_PASSWORD || 'password',
            port: process.env.DB_PORT || 5432,
        });
        
        this.migrationsDir = path.join(__dirname, 'migrations');
    }

    async init() {
        const client = await this.pool.connect();
        try {
            // 마이그레이션 상태 관리 테이블 생성
            await client.query(`
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(255) PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            `);
            console.log('✅ 마이그레이션 테이블 초기화 완료');
        } finally {
            client.release();
        }
    }

    async getAppliedMigrations() {
        const client = await this.pool.connect();
        try {
            const result = await client.query(
                'SELECT version FROM schema_migrations ORDER BY version'
            );
            return result.rows.map(row => row.version);
        } finally {
            client.release();
        }
    }

    async getMigrationFiles() {
        if (!fs.existsSync(this.migrationsDir)) {
            return [];
        }
        
        const files = fs.readdirSync(this.migrationsDir)
            .filter(file => file.endsWith('.sql'))
            .sort();
        
        return files;
    }

    async runMigration(filename) {
        const filePath = path.join(this.migrationsDir, filename);
        const sql = fs.readFileSync(filePath, 'utf8');
        const version = filename.replace('.sql', '');

        const client = await this.pool.connect();
        try {
            await client.query('BEGIN');
            
            // 마이그레이션 실행
            await client.query(sql);
            
            // 실행 기록 저장
            await client.query(
                'INSERT INTO schema_migrations (version) VALUES ($1) ON CONFLICT DO NOTHING',
                [version]
            );
            
            await client.query('COMMIT');
            console.log(`✅ 마이그레이션 적용 완료: ${filename}`);
            return true;
        } catch (error) {
            await client.query('ROLLBACK');
            console.error(`❌ 마이그레이션 실패: ${filename}`, error);
            throw error;
        } finally {
            client.release();
        }
    }

    async runMigrations() {
        await this.init();
        
        const applied = await this.getAppliedMigrations();
        const files = await this.getMigrationFiles();
        
        const pending = files.filter(file => {
            const version = file.replace('.sql', '');
            return !applied.includes(version);
        });

        if (pending.length === 0) {
            console.log('✅ 모든 마이그레이션이 이미 적용되었습니다.');
            return;
        }

        console.log(`📋 ${pending.length}개의 마이그레이션을 적용합니다...`);
        
        for (const file of pending) {
            await this.runMigration(file);
        }
        
        console.log('✅ 모든 마이그레이션 완료');
    }

    async showStatus() {
        await this.init();
        
        const applied = await this.getAppliedMigrations();
        const files = await this.getMigrationFiles();
        
        console.log('\n📊 마이그레이션 상태:');
        console.log('='.repeat(60));
        
        for (const file of files) {
            const version = file.replace('.sql', '');
            const status = applied.includes(version) ? '✅ 적용됨' : '⏳ 대기중';
            console.log(`${status} ${file}`);
        }
        
        console.log('='.repeat(60));
        console.log(`총 ${files.length}개 파일 중 ${applied.length}개 적용됨`);
    }

    async close() {
        await this.pool.end();
    }
}

// CLI 실행
async function main() {
    const args = process.argv.slice(2);
    const runner = new MigrationRunner();
    
    try {
        if (args.includes('--status')) {
            await runner.showStatus();
        } else {
            await runner.runMigrations();
        }
    } catch (error) {
        console.error('❌ 마이그레이션 실행 실패:', error);
        process.exit(1);
    } finally {
        await runner.close();
    }
}

if (require.main === module) {
    main();
}

module.exports = MigrationRunner;

