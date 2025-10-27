#!/usr/bin/env python3
"""
커스터머 대시보드 라우트
"""

from flask import Blueprint, session, redirect, render_template

# 블루프린트 생성
customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

@customer_bp.route('/dashboard')
def customer_dashboard():
    # 로그인 체크
    if not session.get('user_id'):
        return redirect('/login')
    
    return render_template('customer/dashboard.html')
