세션 확인 시작 - API 호출 전
admin-panel:468 세션 확인 API 응답 상태: 200
admin-panel:477 세션 확인 응답 데이터: {success: true, message: '세션이 유효합니다.', user: {…}}
admin-panel:501 사용자 목록 불러오기 시도 - API 호출 전
admin-panel:502  GET http://localhost:3000/api/admin-users/users 401 (Unauthorized)
loadUsers @ admin-panel:502
showSection @ admin-panel:759
(익명) @ admin-panel:939이 오류 이해하기
admin-panel:505 API 응답 수신: 401
admin-panel:507 API 응답 데이터: {success: false, error: 'Unauthorized', message: '로그인이 필요합니다.'}
admin-panel:510 401 인증 오류 발생 - 세션 또는 권한 문제