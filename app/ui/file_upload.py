import streamlit as st
import os
import cv2
import numpy as np
from processors.file_loader import FileLoader

def render_file_upload():
    """Dosya yükleme arayüzü"""
    st.subheader("📂 Adım 0: Dosya Yükleme")
    st.markdown("Desteklenen formatlar: **PNG, JPG, SVG, DXF, PDF, AI, EPS**")
    
    uploaded_file = st.file_uploader(
        "Tabela Görseli Yükle", 
        type=["png", "jpg", "jpeg", "svg", "dxf", "pdf", "ai", "eps"]
    )
    
    if uploaded_file is None:
        st.info("📂 Lütfen bir dosya yükleyin")
        return None, None, None
    
    file_name = uploaded_file.name
    file_ext = os.path.splitext(file_name)[1].lower()
    
    st.success(f"✅ Dosya yüklendi: {file_name}")
    
    # Değişkenleri baştan tanımla
    img = None
    svg_paths = None
    
    try:
        # Dosya formatına göre yükle
        if file_ext in ['.png', '.jpg', '.jpeg']:
            img = FileLoader.load_image(uploaded_file)
            st.info("🖼️ PNG/JPG dosyası okundu")
            
        elif file_ext == '.svg':
            img, svg_paths = FileLoader.load_svg(uploaded_file)
            st.info("✅ SVG dosyası başarıyla okundu! Vektör verileri işleniyor...")
            
        elif file_ext == '.dxf':
            img = FileLoader.load_dxf(uploaded_file)
            st.info("✅ DXF dosyası başarıyla okundu!")
            
        elif file_ext == '.pdf':
            img = FileLoader.load_pdf(uploaded_file)
            st.info("✅ PDF dosyası başarıyla okundu!")
            
        elif file_ext == '.ai':
            img = FileLoader.load_ai(uploaded_file)
            st.info("✅ AI (Adobe Illustrator) dosyası başarıyla okundu!")
            st.caption("💡 AI dosyasının 'PDF Uyumlu' olarak kaydedilmiş olması gerekir.")
            
        elif file_ext == '.eps':
            try:
                img = FileLoader.load_eps(uploaded_file)
                st.info("✅ EPS dosyası başarıyla okundu!")
                st.caption("💡 EPS dosyaları Ghostscript ile render edilir.")
            except Exception as e:
                if "Ghostscript" in str(e):
                    st.error("❌ Ghostscript kurulu değil! Lütfen terminalden kurun:")
                    st.code("sudo apt install ghostscript  # Ubuntu/Debian")
                    st.code("brew install ghostscript      # macOS")
                    return None, None, None
                raise e
            
        else:
            st.error(f"❌ Desteklenmeyen dosya formatı: {file_ext}")
            return None, None, None
        
        if img is not None:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return img, img_rgb, svg_paths
        else:
            st.error("❌ Görsel okunamadı!")
            return None, None, None
            
    except Exception as e:
        st.error(f"❌ Hata: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None, None, None
