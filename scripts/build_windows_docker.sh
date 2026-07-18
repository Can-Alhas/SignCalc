#!/bin/bash
# Docker ile Windows EXE build

echo "🐳 Windows EXE build (Docker ile)..."

docker run --rm \
    -v $(pwd):/workspace \
    -w /workspace \
    cdrx/pyinstaller-windows:python3 \
    bash -c "
        pip install -r requirements.txt &&
        pyinstaller \
            --name=SignCalc \
            --onefile \
            --windowed \
            --add-data 'app;app' \
            --add-data 'data;data' \
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
    "

echo "✅ Windows EXE oluşturuldu: dist/SignCalc.exe"
