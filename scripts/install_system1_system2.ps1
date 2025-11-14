# 시스템 1 & 2 필수 패키지 설치 스크립트 (Windows PowerShell용)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "시스템 1 & 2 필수 패키지 설치" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# pip 업그레이드
Write-Host "📦 pip 업그레이드 중..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# 필수 패키지 설치
Write-Host ""
Write-Host "📦 필수 패키지 설치 중..." -ForegroundColor Yellow
pip install streamlit>=1.28.0 `
            Pillow>=10.0.0 `
            pandas>=2.0.0 `
            numpy>=1.24.0 `
            matplotlib>=3.7.0 `
            scipy>=1.11.0 `
            scikit-learn>=1.3.0

# 설치 확인
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "설치 확인" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

python -c "import streamlit; print('✅ streamlit:', streamlit.__version__)" 
if ($LASTEXITCODE -ne 0) { Write-Host "❌ streamlit 설치 실패" -ForegroundColor Red }

python -c "import PIL; print('✅ Pillow:', PIL.__version__)"
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Pillow 설치 실패" -ForegroundColor Red }

python -c "import pandas; print('✅ pandas:', pandas.__version__)"
if ($LASTEXITCODE -ne 0) { Write-Host "❌ pandas 설치 실패" -ForegroundColor Red }

python -c "import numpy; print('✅ numpy:', numpy.__version__)"
if ($LASTEXITCODE -ne 0) { Write-Host "❌ numpy 설치 실패" -ForegroundColor Red }

python -c "import matplotlib; print('✅ matplotlib:', matplotlib.__version__)"
if ($LASTEXITCODE -ne 0) { Write-Host "❌ matplotlib 설치 실패" -ForegroundColor Red }

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ 설치 완료!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "시스템 1 실행 방법:" -ForegroundColor Yellow
Write-Host "  streamlit run ai\advanced_labeling_tool.py" -ForegroundColor White
Write-Host ""
Write-Host "시스템 2 데모 실행:" -ForegroundColor Yellow
Write-Host "  python scripts\run_system1_system2_demo.py" -ForegroundColor White
Write-Host ""

