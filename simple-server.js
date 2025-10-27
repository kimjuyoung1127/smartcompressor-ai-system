// 간단한 서버로 테스트
const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// 기본 미들웨어
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 정적 파일 서빙
app.use('/static', express.static(path.join(__dirname, 'static')));
app.use(express.static(path.join(__dirname, 'static')));

// 메인 페이지
app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Signalcraft.kr - 서버 복구 중</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                    margin: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                }
                h1 { font-size: 3rem; margin-bottom: 20px; }
                p { font-size: 1.2rem; margin-bottom: 30px; }
                .status { 
                    background: rgba(0,255,0,0.2);
                    padding: 10px;
                    border-radius: 5px;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Signalcraft.kr</h1>
                <div class="status">✅ 서버가 정상적으로 실행 중입니다!</div>
                <p>서버 복구가 완료되었습니다.</p>
                <p>현재 시간: ${new Date().toLocaleString('ko-KR')}</p>
            </div>
        </body>
        </html>
    `);
});

// 헬스 체크 API
app.get('/api/health', (req, res) => {
    res.json({
        status: 'ok',
        message: 'Signalcraft.kr 서버가 정상 작동 중입니다',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// 404 처리
app.use((req, res) => {
    res.status(404).send(`
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>404 - 페이지를 찾을 수 없습니다</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                    margin: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                }
                h1 { font-size: 4rem; margin-bottom: 20px; }
                p { font-size: 1.2rem; margin-bottom: 30px; }
                a { 
                    color: #fff; 
                    text-decoration: none; 
                    background: rgba(255,255,255,0.2);
                    padding: 10px 20px;
                    border-radius: 5px;
                    display: inline-block;
                }
                a:hover { background: rgba(255,255,255,0.3); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>404</h1>
                <p>요청하신 페이지를 찾을 수 없습니다.</p>
                <a href="/">홈으로 돌아가기</a>
            </div>
        </body>
        </html>
    `);
});

// 서버 시작
const server = app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Signalcraft.kr 서버가 http://0.0.0.0:${PORT} 에서 실행 중입니다`);
    console.log(`🌐 외부 접근: http://signalcraft.kr:${PORT}`);
    console.log(`⏰ 시작 시간: ${new Date().toISOString()}`);
});

// 에러 처리
process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    server.close(() => {
        console.log('Process terminated');
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    server.close(() => {
        console.log('Process terminated');
        process.exit(0);
    });
});
