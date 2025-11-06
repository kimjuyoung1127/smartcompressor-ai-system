#!/usr/bin/env python3
"""
GitHub PR 변경사항 분석 및 코드 리뷰 도구
PR diff 파일을 분석하여 잠재적 문제점을 찾습니다.
"""

import re
import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple

class PRReviewer:
    """PR 코드 리뷰 클래스"""
    
    def __init__(self, diff_file: str):
        self.diff_file = diff_file
        self.issues = []
        self.warnings = []
        self.suggestions = []
        
    def analyze(self) -> Dict:
        """PR diff 파일 분석"""
        if not os.path.exists(self.diff_file):
            print(f"❌ 오류: 파일을 찾을 수 없습니다: {self.diff_file}")
            return {}
        
        with open(self.diff_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        self._check_security_issues(content)
        self._check_error_handling(content)
        self._check_code_quality(content)
        self._check_potential_bugs(content)
        self._check_performance(content)
        
        return {
            'issues': self.issues,
            'warnings': self.warnings,
            'suggestions': self.suggestions
        }
    
    def _check_security_issues(self, content: str):
        """보안 취약점 체크"""
        security_patterns = [
            (r'eval\s*\(', '보안 위험: eval() 사용 - 코드 주입 위험'),
            (r'exec\s*\(', '보안 위험: exec() 사용 - 코드 주입 위험'),
            (r'os\.system\s*\(', '보안 위험: os.system() 사용 - 셸 명령어 주입 위험'),
            (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', '보안 위험: subprocess with shell=True'),
            (r'password\s*=\s*["\']', '보안 위험: 하드코딩된 비밀번호 발견'),
            (r'api[_-]?key\s*=\s*["\']', '보안 위험: 하드코딩된 API 키 발견'),
            (r'sql.*\+.*request\.', 'SQL Injection 위험: 문자열 연결로 SQL 쿼리 구성'),
            (r'document\.cookie', '보안 위험: 쿠키 직접 조작'),
            (r'innerHTML\s*=', 'XSS 위험: innerHTML 사용'),
        ]
        
        for pattern, message in security_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                self.issues.append({
                    'type': '보안',
                    'severity': '높음',
                    'line': line_num,
                    'message': message,
                    'code': match.group()
                })
    
    def _check_error_handling(self, content: str):
        """에러 처리 체크"""
        error_patterns = [
            (r'try:\s*$', None),  # try 블록 확인
            (r'except\s*:', '경고: 일반적인 except 사용 - 구체적인 예외 타입 지정 권장'),
            (r'catch\s*\([^)]*\)\s*\{', '경고: 일반적인 catch 사용 - 구체적인 예외 타입 지정 권장'),
            (r'if\s*\([^)]+\)\s*\{[^}]*\}\s*//\s*TODO.*error', '경고: 에러 처리 TODO 주석'),
        ]
        
        for pattern, message in error_patterns:
            if message:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    self.warnings.append({
                        'type': '에러 처리',
                        'line': line_num,
                        'message': message
                    })
        
        # try 없이 위험한 코드 사용
        risky_patterns = [
            (r'open\s*\([^)]+\)(?!.*with)', '경고: 파일 열기 후 close() 호출 누락 가능성'),
            (r'\.json\(\)(?!.*\.catch)', '경고: Promise 에러 처리 누락 가능성'),
        ]
        
        for pattern, message in risky_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                self.warnings.append({
                    'type': '에러 처리',
                    'line': line_num,
                    'message': message
                })
    
    def _check_code_quality(self, content: str):
        """코드 품질 체크"""
        quality_patterns = [
            (r'console\.log\s*\(', '제안: console.log 제거 또는 로깅 라이브러리 사용'),
            (r'print\s*\(', '제안: print 대신 로깅 라이브러리 사용'),
            (r'#\s*TODO', '제안: TODO 주석 해결 필요'),
            (r'#\s*FIXME', '제안: FIXME 주석 해결 필요'),
            (r'#\s*HACK', '제안: HACK 주석 - 임시 해결책 확인 필요'),
            (r'debugger;', '제안: debugger 문 제거'),
            (r'var\s+\w+', '제안: var 대신 let/const 사용'),
        ]
        
        for pattern, message in quality_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                self.suggestions.append({
                    'type': '코드 품질',
                    'line': line_num,
                    'message': message
                })
    
    def _check_potential_bugs(self, content: str):
        """잠재적 버그 체크"""
        bug_patterns = [
            (r'==\s*null', '경고: == null 대신 === null 사용 권장'),
            (r'!=\s*null', '경고: != null 대신 !== null 사용 권장'),
            (r'for\s*\([^)]*\)\s*\{[^}]*\}\s*//.*undefined', '경고: undefined 체크 누락 가능성'),
            (r'setTimeout\s*\([^,)]+\s*,', None),  # setTimeout 확인
            (r'setInterval\s*\([^,)]+\s*,', None),  # setInterval 확인
        ]
        
        for pattern, message in bug_patterns:
            if message:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    self.warnings.append({
                        'type': '잠재적 버그',
                        'line': line_num,
                        'message': message
                    })
    
    def _check_performance(self, content: str):
        """성능 문제 체크"""
        perf_patterns = [
            (r'for\s*\([^)]*\)\s*\{[^}]*\.innerHTML', '성능: 반복문 내 innerHTML 사용 - 성능 저하 가능'),
            (r'for\s*\([^)]*\)\s*\{[^}]*querySelector', '성능: 반복문 내 querySelector 사용 - 성능 저하 가능'),
            (r'N\+1', '성능: N+1 쿼리 문제 가능성'),
        ]
        
        for pattern, message in perf_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                self.warnings.append({
                    'type': '성능',
                    'line': line_num,
                    'message': message
                })
    
    def print_report(self):
        """리뷰 결과 출력"""
        print("=" * 80)
        print("📊 PR 코드 리뷰 결과")
        print("=" * 80)
        print()
        
        if self.issues:
            print("🔴 발견된 문제점 (높은 우선순위)")
            print("-" * 80)
            for issue in self.issues:
                print(f"  [{issue['type']}] {issue['message']}")
                print(f"    위치: 라인 {issue['line']}")
                print(f"    코드: {issue['code']}")
                print()
        else:
            print("✅ 심각한 문제점 없음")
            print()
        
        if self.warnings:
            print("⚠️  경고 사항")
            print("-" * 80)
            for warning in self.warnings:
                print(f"  [{warning['type']}] {warning['message']}")
                if 'line' in warning:
                    print(f"    위치: 라인 {warning['line']}")
                print()
        else:
            print("✅ 경고 사항 없음")
            print()
        
        if self.suggestions:
            print("💡 개선 제안")
            print("-" * 80)
            for suggestion in self.suggestions:
                print(f"  [{suggestion['type']}] {suggestion['message']}")
                if 'line' in suggestion:
                    print(f"    위치: 라인 {suggestion['line']}")
                print()
        else:
            print("✅ 개선 제안 없음")
            print()
        
        print("=" * 80)
        print(f"총 발견: {len(self.issues)} 문제점, {len(self.warnings)} 경고, {len(self.suggestions)} 제안")
        print("=" * 80)

def main():
    if len(sys.argv) < 2:
        print("사용법: python3 analyze_pr_changes.py <PR_DIFF_FILE>")
        print("또는: ./review_pr.sh <PR_NUMBER> 실행 후 생성된 diff 파일 경로 사용")
        sys.exit(1)
    
    diff_file = sys.argv[1]
    reviewer = PRReviewer(diff_file)
    reviewer.analyze()
    reviewer.print_report()

if __name__ == "__main__":
    main()

