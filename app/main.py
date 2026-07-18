import streamlit as st
import cv2
import sys
import os
from datetime import datetime

# Proje kök dizinini ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# UI modülleri
from ui.sidebar import render_sidebar
from ui.file_upload import render_file_upload
from ui.calibration import render_calibration
from ui.results import render_results
from ui.nesting import render_nesting
from ui.reports import render_reports

# İş mantığı modülleri
from processors.image_processor import ImageProcessor
from utils.calibration import Calibration
from utils.logger import logger
from price_engine.calculator import PriceCalculator
from database.db_manager import DatabaseManager

# Sayfa ayarları
st.set_page_config(page_title="SignCalc", page_icon="🧮", layout="wide")

st.title("🧮 SignCalc - Akıllı Tabela Fiyat Otomasyonu")
st.caption("PNG, JPG, SVG, DXF, PDF, AI, EPS | Ölçek kalibrasyonu | Nesting optimizasyonu")

# Veritabanı
db = DatabaseManager()

# Session state
if 'calibrated' not in st.session_state:
    st.session_state.calibrated = False
if 'calib' not in st.session_state:
    st.session_state.calib = Calibration()
if 'price_calc' not in st.session_state:
    default_material = db.get_default_material()
    default_labor = db.get_default_labor()
    default_fire = db.get_default_fire()
    
    material = db.get_material_by_name(default_material)
    labor = db.get_labor_by_name(default_labor)
    fire = db.get_fire_by_name(default_fire)
    
    st.session_state.price_calc = PriceCalculator(
        material_cost=material[2] if material else 0.045,
        labor_cost=labor[2] if labor else 0.012,
        fire_rate=fire[2] if fire else 1.10
    )
if 'click_points' not in st.session_state:
    st.session_state.click_points = []
if 'processor' not in st.session_state:
    st.session_state.processor = None
if 'nesting_result' not in st.session_state:
    st.session_state.nesting_result = None

logger.info("Uygulama başlatıldı")

# Sidebar
material_cost, labor_cost, fire_rate = render_sidebar()
st.session_state.price_calc.update_parameters(material_cost, labor_cost, fire_rate)

# Dosya yükleme
img, img_rgb, svg_paths = render_file_upload()

if img is not None and img_rgb is not None:
    # Görüntü işleme
    processor = ImageProcessor(img, svg_paths)
    processor.process()
    st.session_state.processor = processor
    
    img_contours = processor.draw_contours(img_rgb)
    st.info(f"🔍 {processor.get_contour_count()} adet nesne tespit edildi.")
    
    # Kalibrasyon
    calibrated = render_calibration(img_contours)
    
    # Kalibrasyon tamamlandıysa sonuçları göster
    if calibrated:
        calib = st.session_state.calib
        
        # KALİBRASYON KONTROLÜ
        if calib.pixel_per_mm is None or not calib.is_calibrated:
            st.error("❌ Kalibrasyon hatası! Lütfen tekrar kalibrasyon yapın.")
        else:
            total_area_px = processor.get_total_area()
            total_perimeter_px = processor.get_total_perimeter()
            
            area_mm2, _ = calib.pixel_to_mm2(total_area_px)
            perimeter_mm, _ = calib.pixel_to_mm(total_perimeter_px)
            
            # Değerlerin geçerli olduğundan emin ol
            if area_mm2 is None or perimeter_mm is None:
                st.error("❌ Ölçüm hatası! Lütfen tekrar deneyin.")
            else:
                price_result = st.session_state.price_calc.calculate(area_mm2, perimeter_mm)
                
                render_results(processor, calib, price_result)
                render_nesting(processor, calib)
                render_reports(processor, calib, price_result)

# Footer
st.markdown("---")
st.caption(f"🧮 SignCalc v1.0 | {datetime.now().strftime('%d.%m.%Y %H:%M')}")
