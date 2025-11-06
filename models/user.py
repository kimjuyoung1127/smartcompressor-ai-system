import hashlib
import secrets
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class User:
    def __init__(self, id, email, password_hash, name, phone=None, company=None, marketing_agree=False, created_at=None, updated_at=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.name = name
        self.phone = phone
        self.company = company
        self.marketing_agree = marketing_agree
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def hash_password(password):
        """비밀번호 해시화"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password, password_hash):
        """비밀번호 검증"""
        return User.hash_password(password) == password_hash

    @staticmethod
    def register(email, password, name, phone=None, company=None, marketing_agree=False):
        """회원가입"""
        try:
            password_hash = User.hash_password(password)
            user_id = create_user(email, password_hash, name, phone, company, marketing_agree)
            return user_id
        except Exception as e:
            return None

    @staticmethod
    def login(email, password):
        """로그인 - PostgreSQL과 bcrypt 사용"""
        try:
            # PostgreSQL 연결
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', 5432),
                database=os.getenv('DB_NAME', 'smartcompressor_ai'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '')
            )
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # 이메일로 사용자 조회
            cursor.execute("""
                SELECT id, username, email, password_hash, full_name, role, is_active
                FROM users 
                WHERE email = %s AND is_active = true
            """, (email,))
            
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not user_data:
                return {
                    'success': False,
                    'message': '이메일 또는 비밀번호가 올바르지 않습니다.'
                }
            
            # bcrypt로 비밀번호 검증
            try:
                password_hash = user_data['password_hash']
                if isinstance(password_hash, bytes):
                    password_hash = password_hash.decode('utf-8')
                
                if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                    token = secrets.token_urlsafe(32)
                    return {
                        'success': True,
                        'user': {
                            'id': user_data['id'],
                            'email': user_data['email'],
                            'name': user_data.get('full_name') or user_data.get('username', ''),
                            'company': '',
                            'role': user_data.get('role', 'user')
                        },
                        'token': token
                    }
                else:
                    return {
                        'success': False,
                        'message': '이메일 또는 비밀번호가 올바르지 않습니다.'
                    }
            except Exception as hash_error:
                # bcrypt 검증 실패 시 SHA256으로 폴백 (기존 사용자 호환성)
                if User.verify_password(password, password_hash):
                    token = secrets.token_urlsafe(32)
                    return {
                        'success': True,
                        'user': {
                            'id': user_data['id'],
                            'email': user_data['email'],
                            'name': user_data.get('full_name') or user_data.get('username', ''),
                            'company': '',
                            'role': user_data.get('role', 'user')
                        },
                        'token': token
                    }
                else:
                    return {
                        'success': False,
                        'message': '이메일 또는 비밀번호가 올바르지 않습니다.'
                    }
                    
        except psycopg2.Error as db_error:
            return {
                'success': False,
                'message': f'데이터베이스 오류: {str(db_error)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'로그인 오류: {str(e)}'
            }

    @staticmethod
    def get_by_token(token):
        """토큰으로 사용자 정보 조회"""
        try:
            # 임시 토큰 조회
            if token == 'admin_token_123':
                return {
                    'id': 1,
                    'email': 'admin@signalcraft.kr',
                    'name': '관리자',
                    'company': 'Signalcraft'
                }
            return None
        except Exception as e:
            return None

    @staticmethod
    def logout(token):
        """로그아웃"""
        try:
            # 임시 로그아웃 처리
            return True
        except Exception as e:
            return False

class UserSession:
    def __init__(self, id, user_id, token, created_at, expires_at):
        self.id = id
        self.user_id = user_id
        self.token = token
        self.created_at = created_at
        self.expires_at = expires_at

    @staticmethod
    def create(user_id, token):
        """새 세션 생성"""
        try:
            return UserSession(1, user_id, token, datetime.now(), datetime.now())
        except Exception as e:
            return None

    @staticmethod
    def get_by_token(token):
        """토큰으로 세션 조회"""
        try:
            # 임시 세션 조회
            if token == 'admin_token_123':
                return UserSession(1, 1, token, datetime.now(), datetime.now())
            return None
        except Exception as e:
            return None
