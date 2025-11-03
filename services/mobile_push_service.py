#!/usr/bin/env python3
"""
모바일 푸시 알림 서비스
Tesla App과 Starbucks App을 벤치마킹한 푸시 알림 시스템
"""

import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import base64
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PushNotificationType(Enum):
    """푸시 알림 타입"""
    SYSTEM = "system"
    DIAGNOSIS = "diagnosis"
    PAYMENT = "payment"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"
    PROMOTION = "promotion"
    ORDER = "order"

class PushPriority(Enum):
    """푸시 알림 우선순위"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class PushNotification:
    """푸시 알림 데이터 클래스"""
    id: str
    title: str
    body: str
    icon: str
    badge: str
    image: Optional[str] = None
    url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    priority: PushPriority = PushPriority.NORMAL
    notification_type: PushNotificationType = PushNotificationType.SYSTEM
    ttl: int = 3600  # 1시간
    silent: bool = False
    require_interaction: bool = False
    vibrate: List[int] = None
    actions: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.vibrate is None:
            self.vibrate = [200, 100, 200]
        if self.actions is None:
            self.actions = [
                {"action": "view", "title": "확인", "icon": "/static/icons/checkmark.png"},
                {"action": "dismiss", "title": "닫기", "icon": "/static/icons/close.png"}
            ]

class WebPushService:
    """Web Push 서비스 (VAPID 지원)"""
    
    def __init__(self, vapid_private_key: str, vapid_public_key: str, vapid_email: str):
        self.vapid_private_key = vapid_private_key
        self.vapid_public_key = vapid_public_key
        self.vapid_email = vapid_email
        self.private_key = serialization.load_pem_private_key(
            vapid_private_key.encode(),
            password=None
        )
    
    def generate_vapid_headers(self, endpoint: str) -> Dict[str, str]:
        """VAPID 헤더 생성"""
        try:
            # JWT 토큰 생성 (간단한 구현)
            import jwt
            import time
            
            now = int(time.time())
            payload = {
                "aud": endpoint,
                "exp": now + 3600,
                "sub": self.vapid_email,
                "iat": now
            }
            
            token = jwt.encode(payload, self.vapid_private_key, algorithm="ES256")
            
            return {
                "Authorization": f"vapid t={token}, k={self.vapid_public_key}",
                "Content-Type": "application/json"
            }
        except Exception as e:
            logger.error(f"VAPID 헤더 생성 실패: {e}")
            return {"Content-Type": "application/json"}
    
    async def send_push_notification(self, subscription: Dict[str, Any], notification: PushNotification) -> bool:
        """푸시 알림 전송"""
        try:
            endpoint = subscription.get('endpoint')
            keys = subscription.get('keys', {})
            
            if not endpoint or not keys:
                logger.error("잘못된 구독 정보")
                return False
            
            # 푸시 페이로드 생성
            payload = {
                "title": notification.title,
                "body": notification.body,
                "icon": notification.icon,
                "badge": notification.badge,
                "data": notification.data or {},
                "actions": notification.actions,
                "vibrate": notification.vibrate,
                "requireInteraction": notification.require_interaction,
                "silent": notification.silent,
                "tag": notification.id,
                "timestamp": int(datetime.now().timestamp() * 1000)
            }
            
            if notification.image:
                payload["image"] = notification.image
            
            if notification.url:
                payload["data"]["url"] = notification.url
            
            # VAPID 헤더 생성
            headers = self.generate_vapid_headers(endpoint)
            
            # 푸시 서버에 전송
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status in [200, 201]:
                        logger.info(f"푸시 알림 전송 성공: {notification.id}")
                        return True
                    else:
                        logger.error(f"푸시 알림 전송 실패: {response.status} - {await response.text()}")
                        return False
                        
        except Exception as e:
            logger.error(f"푸시 알림 전송 오류: {e}")
            return False

class FirebaseCloudMessaging:
    """Firebase Cloud Messaging 서비스"""
    
    def __init__(self, server_key: str, project_id: str):
        self.server_key = server_key
        self.project_id = project_id
        self.fcm_url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
    
    async def send_push_notification(self, token: str, notification: PushNotification) -> bool:
        """FCM 푸시 알림 전송"""
        try:
            headers = {
                "Authorization": f"Bearer {self.server_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "message": {
                    "token": token,
                    "notification": {
                        "title": notification.title,
                        "body": notification.body,
                        "image": notification.image
                    },
                    "data": notification.data or {},
                    "android": {
                        "priority": "high",
                        "notification": {
                            "icon": notification.icon,
                            "color": "#00D4AA",
                            "sound": "default",
                            "vibrate_timings": notification.vibrate,
                            "click_action": notification.url
                        }
                    },
                    "apns": {
                        "payload": {
                            "aps": {
                                "alert": {
                                    "title": notification.title,
                                    "body": notification.body
                                },
                                "badge": 1,
                                "sound": "default",
                                "mutable-content": 1
                            }
                        }
                    },
                    "webpush": {
                        "notification": {
                            "title": notification.title,
                            "body": notification.body,
                            "icon": notification.icon,
                            "badge": notification.badge,
                            "image": notification.image,
                            "actions": notification.actions,
                            "vibrate": notification.vibrate,
                            "requireInteraction": notification.require_interaction,
                            "silent": notification.silent
                        },
                        "fcm_options": {
                            "link": notification.url
                        }
                    }
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.fcm_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status in [200, 201]:
                        logger.info(f"FCM 푸시 알림 전송 성공: {notification.id}")
                        return True
                    else:
                        logger.error(f"FCM 푸시 알림 전송 실패: {response.status} - {await response.text()}")
                        return False
                        
        except Exception as e:
            logger.error(f"FCM 푸시 알림 전송 오류: {e}")
            return False

class MobilePushService:
    """모바일 푸시 알림 통합 서비스"""
    
    def __init__(self):
        self.web_push_service = None
        self.fcm_service = None
        self.subscriptions = {}  # 사용자별 구독 정보
        self.notification_history = []  # 알림 히스토리
        
        # 환경 변수에서 설정 로드
        self._initialize_services()
    
    def _initialize_services(self):
        """푸시 서비스 초기화"""
        try:
            # Web Push (VAPID) 설정
            vapid_private_key = os.getenv('VAPID_PRIVATE_KEY')
            vapid_public_key = os.getenv('VAPID_PUBLIC_KEY')
            vapid_email = os.getenv('VAPID_EMAIL', 'admin@smartcompressor.com')
            
            if vapid_private_key and vapid_public_key:
                self.web_push_service = WebPushService(
                    vapid_private_key, vapid_public_key, vapid_email
                )
                logger.info("Web Push 서비스 초기화 완료")
            
            # Firebase Cloud Messaging 설정
            fcm_server_key = os.getenv('FCM_SERVER_KEY')
            fcm_project_id = os.getenv('FCM_PROJECT_ID')
            
            if fcm_server_key and fcm_project_id:
                self.fcm_service = FirebaseCloudMessaging(fcm_server_key, fcm_project_id)
                logger.info("FCM 서비스 초기화 완료")
                
        except Exception as e:
            logger.error(f"푸시 서비스 초기화 실패: {e}")
    
    def register_subscription(self, user_id: str, subscription: Dict[str, Any]) -> bool:
        """사용자 구독 등록"""
        try:
            self.subscriptions[user_id] = subscription
            logger.info(f"사용자 구독 등록 완료: {user_id}")
            return True
        except Exception as e:
            logger.error(f"구독 등록 실패: {e}")
            return False
    
    def unregister_subscription(self, user_id: str) -> bool:
        """사용자 구독 해제"""
        try:
            if user_id in self.subscriptions:
                del self.subscriptions[user_id]
                logger.info(f"사용자 구독 해제 완료: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"구독 해제 실패: {e}")
            return False
    
    async def send_notification(self, user_id: str, notification: PushNotification) -> bool:
        """푸시 알림 전송"""
        try:
            if user_id not in self.subscriptions:
                logger.warning(f"사용자 구독 정보 없음: {user_id}")
                return False
            
            subscription = self.subscriptions[user_id]
            success = False
            
            # Web Push로 전송 시도
            if self.web_push_service and subscription.get('endpoint'):
                success = await self.web_push_service.send_push_notification(
                    subscription, notification
                )
            
            # FCM으로 전송 시도 (Web Push 실패 시)
            if not success and self.fcm_service and subscription.get('fcm_token'):
                success = await self.fcm_service.send_push_notification(
                    subscription['fcm_token'], notification
                )
            
            # 알림 히스토리에 기록
            self.notification_history.append({
                'id': notification.id,
                'user_id': user_id,
                'title': notification.title,
                'body': notification.body,
                'type': notification.notification_type.value,
                'priority': notification.priority.value,
                'sent_at': datetime.now().isoformat(),
                'success': success
            })
            
            return success
            
        except Exception as e:
            logger.error(f"푸시 알림 전송 실패: {e}")
            return False
    
    async def send_bulk_notification(self, user_ids: List[str], notification: PushNotification) -> Dict[str, bool]:
        """대량 푸시 알림 전송"""
        results = {}
        
        for user_id in user_ids:
            results[user_id] = await self.send_notification(user_id, notification)
        
        return results
    
    def create_notification(self, 
                          title: str, 
                          body: str, 
                          notification_type: PushNotificationType = PushNotificationType.SYSTEM,
                          priority: PushPriority = PushPriority.NORMAL,
                          **kwargs) -> PushNotification:
        """알림 객체 생성"""
        notification_id = f"push_{int(datetime.now().timestamp() * 1000)}"
        
        # 기본 아이콘 설정
        icon = kwargs.get('icon', '/static/icons/icon-192x192.png')
        badge = kwargs.get('badge', '/static/icons/pwa-192x192.png')
        
        # 알림 타입별 기본 설정
        if notification_type == PushNotificationType.DIAGNOSIS:
            icon = '/static/icons/diagnosis.png'
            priority = PushPriority.HIGH
        elif notification_type == PushNotificationType.EMERGENCY:
            icon = '/static/icons/emergency.png'
            priority = PushPriority.URGENT
            kwargs['require_interaction'] = True
        elif notification_type == PushNotificationType.PAYMENT:
            icon = '/static/icons/payment.png'
        elif notification_type == PushNotificationType.MAINTENANCE:
            icon = '/static/icons/maintenance.png'
        elif notification_type == PushNotificationType.PROMOTION:
            icon = '/static/icons/promotion.png'
            priority = PushPriority.LOW
        
        return PushNotification(
            id=notification_id,
            title=title,
            body=body,
            icon=icon,
            badge=badge,
            priority=priority,
            notification_type=notification_type,
            **kwargs
        )
    
    async def send_diagnosis_alert(self, user_id: str, diagnosis_result: Dict[str, Any]) -> bool:
        """진단 결과 알림 전송"""
        status = diagnosis_result.get('status', 'unknown')
        confidence = diagnosis_result.get('confidence', 0)
        
        if status == 'abnormal':
            title = "⚠️ 압축기 이상 감지"
            body = f"압축기에서 이상이 감지되었습니다. (신뢰도: {confidence:.1%})"
            priority = PushPriority.HIGH
        elif status == 'warning':
            title = "⚠️ 압축기 주의"
            body = f"압축기 상태를 확인해주세요. (신뢰도: {confidence:.1%})"
            priority = PushPriority.NORMAL
        else:
            title = "✅ 압축기 정상"
            body = f"압축기가 정상 작동 중입니다. (신뢰도: {confidence:.1%})"
            priority = PushPriority.LOW
        
        notification = self.create_notification(
            title=title,
            body=body,
            notification_type=PushNotificationType.DIAGNOSIS,
            priority=priority,
            url='/mobile_app/diagnosis',
            data=diagnosis_result
        )
        
        return await self.send_notification(user_id, notification)
    
    async def send_payment_notification(self, user_id: str, payment_data: Dict[str, Any]) -> bool:
        """결제 알림 전송"""
        amount = payment_data.get('amount', 0)
        method = payment_data.get('method', 'unknown')
        
        title = "💳 결제 완료"
        body = f"{amount:,}원이 {method}로 결제되었습니다."
        
        notification = self.create_notification(
            title=title,
            body=body,
            notification_type=PushNotificationType.PAYMENT,
            priority=PushPriority.NORMAL,
            url='/mobile_app/payments',
            data=payment_data
        )
        
        return await self.send_notification(user_id, notification)
    
    async def send_maintenance_alert(self, user_id: str, maintenance_data: Dict[str, Any]) -> bool:
        """유지보수 알림 전송"""
        equipment = maintenance_data.get('equipment', '압축기')
        maintenance_type = maintenance_data.get('type', '점검')
        
        title = "🔧 유지보수 알림"
        body = f"{equipment}의 {maintenance_type}이 필요합니다."
        
        notification = self.create_notification(
            title=title,
            body=body,
            notification_type=PushNotificationType.MAINTENANCE,
            priority=PushPriority.HIGH,
            url='/mobile_app/maintenance',
            data=maintenance_data
        )
        
        return await self.send_notification(user_id, notification)
    
    async def send_emergency_alert(self, user_id: str, emergency_data: Dict[str, Any]) -> bool:
        """긴급 알림 전송"""
        title = "🚨 긴급 상황"
        body = emergency_data.get('message', '긴급한 상황이 발생했습니다.')
        
        notification = self.create_notification(
            title=title,
            body=body,
            notification_type=PushNotificationType.EMERGENCY,
            priority=PushPriority.URGENT,
            url='/mobile_app/emergency',
            data=emergency_data,
            require_interaction=True,
            vibrate=[1000, 500, 1000, 500, 1000]
        )
        
        return await self.send_notification(user_id, notification)
    
    def get_notification_history(self, user_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """알림 히스토리 조회"""
        history = self.notification_history
        
        if user_id:
            history = [n for n in history if n['user_id'] == user_id]
        
        return sorted(history, key=lambda x: x['sent_at'], reverse=True)[:limit]
    
    def get_subscription_count(self) -> int:
        """구독자 수 조회"""
        return len(self.subscriptions)
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 조회"""
        return {
            'web_push_enabled': self.web_push_service is not None,
            'fcm_enabled': self.fcm_service is not None,
            'subscription_count': len(self.subscriptions),
            'notification_count': len(self.notification_history),
            'last_notification': self.notification_history[-1] if self.notification_history else None
        }

# 전역 인스턴스
mobile_push_service = MobilePushService()
