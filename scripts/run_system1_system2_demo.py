#!/usr/bin/env python3
"""
시스템 1 & 2 데모 실행 스크립트
로드맵 2단계 핵심 시스템 통합 데모
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_data_warehouse():
    """시스템 2: 데이터 웨어하우스 데모"""
    logger.info("=== 시스템 2: 데이터 웨어하우스 데모 시작 ===")
    
    try:
        from services.data_warehouse_service import DataWarehouseService
        
        # 웨어하우스 초기화
        warehouse = DataWarehouseService()
        logger.info("✅ 데이터 웨어하우스 초기화 완료")
        
        # 테스트 데이터 저장
        test_device_id = "demo_device_001"
        test_timestamp = datetime.now()
        
        for i in range(10):
            timestamp = test_timestamp - timedelta(hours=i)
            warehouse.store_sensor_data(
                device_id=test_device_id,
                timestamp=timestamp,
                audio_level=70.0 + (i * 2),
                temperature=25.0 + (i * 0.5),
                vibration_x=0.1 + (i * 0.01),
                vibration_y=0.2 + (i * 0.01),
                vibration_z=0.15 + (i * 0.01),
                power_consumption=1200.0 + (i * 50),
                metadata={"test": True, "iteration": i}
            )
        
        logger.info("✅ 테스트 데이터 10건 저장 완료")
        
        # 데이터 조회
        start_date = test_timestamp - timedelta(hours=12)
        end_date = test_timestamp
        
        df = warehouse.get_sensor_data_range(
            device_id=test_device_id,
            start_date=start_date,
            end_date=end_date
        )
        
        logger.info(f"✅ 데이터 조회 완료: {len(df)}건")
        if not df.empty:
            logger.info(f"   - 기간: {df['timestamp'].min()} ~ {df['timestamp'].max()}")
            logger.info(f"   - 오디오 레벨 평균: {df['audio_level'].mean():.2f}")
            logger.info(f"   - 온도 평균: {df['temperature'].mean():.2f}")
        
        # 통계 집계
        stats = warehouse.aggregate_statistics(
            device_id=test_device_id,
            date=test_timestamp.date()
        )
        
        logger.info("✅ 통계 집계 완료")
        if stats:
            for sensor_type, values in stats.items():
                logger.info(f"   - {sensor_type}: 평균={values['avg']:.2f}, "
                          f"최대={values['max']:.2f}, 최소={values['min']:.2f}")
        
        logger.info("=== 시스템 2 데모 완료 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"시스템 2 데모 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_correlation_analysis():
    """상관관계 분석 데모"""
    logger.info("=== 상관관계 분석 데모 시작 ===")
    
    try:
        from services.data_warehouse_service import DataWarehouseService
        from services.correlation_analysis_service import CorrelationAnalysisService
        
        warehouse = DataWarehouseService()
        correlation = CorrelationAnalysisService(warehouse)
        
        # 테스트용 고장 이벤트 시뮬레이션
        test_device_id = "demo_device_001"
        failure_time = datetime.now() - timedelta(days=5)
        
        failure_events = [
            {
                'timestamp': failure_time,
                'type': 'leak',
                'description': '냉매 누설 테스트'
            }
        ]
        
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        result = correlation.analyze_lead_time(
            device_id=test_device_id,
            start_date=start_date,
            end_date=end_date,
            failure_events=failure_events
        )
        
        if result:
            logger.info("✅ 상관관계 분석 완료")
            logger.info(f"   - 소리 센서 평균 선행 일수: {result['audio_sensor']['avg_lead_days']}일")
            logger.info(f"   - 소리 센서 정확도: {result['audio_sensor']['accuracy']}%")
        else:
            logger.warning("⚠️ 분석 결과가 없습니다. (데이터 부족)")
        
        logger.info("=== 상관관계 분석 데모 완료 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"상관관계 분석 데모 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_report_generation():
    """리포트 생성 데모"""
    logger.info("=== 리포트 생성 데모 시작 ===")
    
    try:
        from services.data_warehouse_service import DataWarehouseService
        from services.correlation_analysis_service import CorrelationAnalysisService
        from services.report_generator_service import ReportGeneratorService
        
        warehouse = DataWarehouseService()
        correlation = CorrelationAnalysisService(warehouse)
        generator = ReportGeneratorService(warehouse, correlation)
        
        device_ids = ["demo_device_001"]
        
        failure_events_by_device = {
            "demo_device_001": [
                {
                    'timestamp': datetime.now() - timedelta(days=5),
                    'type': 'leak',
                    'description': '냉매 누설 테스트'
                }
            ]
        }
        
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        report_result = generator.generate_industry_report(
            device_ids=device_ids,
            start_date=start_date,
            end_date=end_date,
            failure_events_by_device=failure_events_by_device,
            report_title="시그널크래프트 데모 리포트"
        )
        
        if report_result and report_result.get('files'):
            logger.info("✅ 리포트 생성 완료")
            logger.info(f"   - JSON 리포트: {report_result['files'].get('json', 'N/A')}")
            logger.info(f"   - Markdown 리포트: {report_result['files'].get('markdown', 'N/A')}")
        else:
            logger.warning("⚠️ 리포트 생성 실패 (데이터 부족)")
        
        logger.info("=== 리포트 생성 데모 완료 ===\n")
        return True
        
    except Exception as e:
        logger.error(f"리포트 생성 데모 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 데모 실행"""
    logger.info("=" * 60)
    logger.info("시스템 1 & 2 통합 데모 시작")
    logger.info("=" * 60)
    logger.info("")
    
    results = {
        'warehouse': demo_data_warehouse(),
        'correlation': demo_correlation_analysis(),
        'report': demo_report_generation()
    }
    
    logger.info("=" * 60)
    logger.info("데모 실행 결과 요약")
    logger.info("=" * 60)
    
    for name, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        logger.info(f"  {name}: {status}")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("시스템 1 사용 방법:")
    logger.info("  streamlit run ai/advanced_labeling_tool.py")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

