#!/bin/bash
# Linux için EXE build script'i

echo "🔨 SignCalc Linux Build Başlatılıyor..."

# Sanal ortamı kontrol et
if [ ! -d "venv" ]; then
    echo "❌ Sanal ortam bulunamadı! Önce 'python3 -m venv venv' çalıştır."
    exit 1
fi

# Sanal ortamı aktifleştir
source venv/bin/activate

# PyInstaller kontrol et
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 PyInstaller kuruluyor..."
    pip install pyinstaller
fi

# Temizlik
rm -rf build/ dist/ *.spec

# Build
echo "🔧 Linux executable oluşturuluyor..."
pyinstaller \
    --name="signcalc" \
    --onefile \
    --add-data "app:app" \
    --add-data "data:data" \
    --hidden-import=streamlit \
    --hidden-import=cv2 \
    --hidden-import=numpy \
    --hidden-import=PIL \
    --hidden-import=reportlab \
    --hidden-import=openpyxl \
    --hidden-import=pandas \
    --hidden-import=svgpathtools \
    --hidden-import=cairosvg \
    --hidden-import=ezdxf \
    --hidden-import=fitz \
    --hidden-import=matplotlib \
    --hidden-import=streamlit_image_coordinates \
    --collect-all=streamlit \
    --collect-all=opencv-python-headless \
    --collect-all=numpy \
    --collect-all=Pillow \
    --collect-all=reportlab \
    --collect-all=openpyxl \
    --collect-all=pandas \
    --collect-all=svgpathtools \
    --collect-all=cairosvg \
    --collect-all=ezdxf \
    --collect-all=PyMuPDF \
    --collect-all=matplotlib \
    --collect-all=streamlit-image-coordinates \
    --clean \
    --noconfirm \
    app/main.py

# Sonuç
if [ -f "dist/signcalc" ]; then
    echo "✅ Linux executable oluşturuldu: dist/signcalc"
    echo "📏 Boyut: $(du -h dist/signcalc | cut -f1)"
else
    echo "❌ Build başarısız!"
    exit 1
fi
