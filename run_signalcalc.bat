@echo off
echo 🧮 SignCalc Başlatılıyor...
echo.

cd /d "%~dp0"

:: Python kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python bulunamadı!
    echo Lütfen Python 3.8+ kurun: https://python.org
    pause
    exit /b 1
)

:: Gerekli paketler
if not exist "venv" (
    echo 📦 Sanal ortam oluşturuluyor...
    python -m venv venv
)

echo 📦 Bağımlılıklar kontrol ediliyor...
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1

:: Uygulamayı başlat
echo 🚀 SignCalc başlatılıyor...
start http://localhost:8501
streamlit run app/main.py --server.port=8501
pause
