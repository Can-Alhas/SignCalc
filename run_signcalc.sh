#!/bin/bash

echo "🧮 SignCalc Başlatılıyor..."
echo ""

# Python kontrol et
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 bulunamadı!"
    echo "Lütfen Python 3.8+ kurun: https://python.org"
    exit 1
fi

# Gerekli paketleri kontrol et
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "📦 Gerekli paketler kuruluyor..."
    pip install -r requirements.txt
fi

# Uygulamayı başlat
echo "🚀 SignCalc başlatılıyor..."
streamlit run app/main.py --server.port=8501
