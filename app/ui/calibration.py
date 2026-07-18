import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

def render_calibration(img_contours):
    """Kalibrasyon arayüzü - Noktalar önce onaylanır, sonra kalibrasyon"""
    st.subheader("📏 Adım 1: Ölçek Kalibrasyonu")
    st.markdown("**1. veya 2. Nokta butonuna tıkla, sonra görselde noktayı işaretle**")
    
    # Session state
    if 'click_points' not in st.session_state:
        st.session_state.click_points = []
    if 'calibration_mode' not in st.session_state:
        st.session_state.calibration_mode = None
    if 'points_confirmed' not in st.session_state:
        st.session_state.points_confirmed = False
    if 'calibrated' not in st.session_state:
        st.session_state.calibrated = False
    
    points = st.session_state.click_points
    mode = st.session_state.calibration_mode
    confirmed = st.session_state.points_confirmed
    calib = st.session_state.calib
    
    # --- BUTONLAR ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔴 1. Nokta", use_container_width=True):
            st.session_state.calibration_mode = 'point1'
            st.session_state.points_confirmed = False
            st.rerun()
    
    with col2:
        if st.button("🔵 2. Nokta", use_container_width=True):
            st.session_state.calibration_mode = 'point2'
            st.session_state.points_confirmed = False
            st.rerun()
    
    with col3:
        if st.button("🗑️ Temizle", use_container_width=True):
            st.session_state.click_points = []
            st.session_state.calibration_mode = None
            st.session_state.points_confirmed = False
            st.session_state.calibrated = False
            calib.reset()
            st.rerun()
    
    with col4:
        if len(points) >= 2:
            if st.button("✅ Noktaları Onayla", use_container_width=True, type="primary"):
                st.session_state.points_confirmed = True
                st.success("✅ Noktalar onaylandı! Şimdi mm değerini girin.")
                st.rerun()
        else:
            st.button("✅ Noktaları Onayla", use_container_width=True, disabled=True)
    
    # --- MOD BİLGİSİ ---
    if mode == 'point1':
        st.info("🔴 **1. Nokta modu:** Görselde tıkla → 1. nokta güncellenir")
    elif mode == 'point2':
        st.info("🔵 **2. Nokta modu:** Görselde tıkla → 2. nokta güncellenir")
    else:
        if len(points) >= 2 and confirmed:
            st.success("✅ Noktalar onaylandı! Kalibrasyona geçebilirsiniz.")
        else:
            st.info("👆 Bir nokta modu seçin (1. Nokta veya 2. Nokta)")
    
    # --- GÖRSEL ---
    img_display = img_contours.copy()
    
    if len(points) >= 1:
        x, y = points[0]
        cv2.circle(img_display, (x, y), 10, (0, 0, 255), -1)
        cv2.circle(img_display, (x, y), 12, (255, 255, 255), 2)
        cv2.putText(img_display, "1", (x-15, y-20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    if len(points) >= 2:
        x, y = points[1]
        cv2.circle(img_display, (x, y), 10, (255, 0, 0), -1)
        cv2.circle(img_display, (x, y), 12, (255, 255, 255), 2)
        cv2.putText(img_display, "2", (x-15, y-20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        
        x1, y1 = points[0]
        x2, y2 = points[1]
        cv2.line(img_display, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
        dist = int(np.sqrt((x2-x1)**2 + (y2-y1)**2))
        mx, my = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.putText(img_display, f"{dist} px", (mx-30, my-15), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 165, 0), 2)
    
    img_pil = Image.fromarray(img_display)
    result = streamlit_image_coordinates(img_pil, key="calibration_click")
    
    # --- TIKLAMA İŞLEME ---
    if result and mode is not None and not confirmed:
        x, y = result["x"], result["y"]
        
        if mode == 'point1':
            if len(points) >= 1:
                points[0] = (x, y)
            else:
                points.append((x, y))
            st.success(f"✅ 1. Nokta: ({x}, {y})")
            st.rerun()
            
        elif mode == 'point2':
            if len(points) >= 1:
                if len(points) >= 2:
                    points[1] = (x, y)
                else:
                    points.append((x, y))
                st.success(f"✅ 2. Nokta: ({x}, {y})")
                st.rerun()
            else:
                st.warning("⚠️ Önce 1. noktayı seçin!")
    
    # --- NOKTA BİLGİLERİ ---
    st.markdown("---")
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("### 📍 Noktalar")
        if len(points) >= 1:
            st.write(f"**1. Nokta:** ({points[0][0]}, {points[0][1]})")
            if confirmed:
                st.success("✅ Onaylandı")
        else:
            st.write("**1. Nokta:** Seçilmedi")
        
        if len(points) >= 2:
            st.write(f"**2. Nokta:** ({points[1][0]}, {points[1][1]})")
            if confirmed:
                st.success("✅ Onaylandı")
        else:
            st.write("**2. Nokta:** Seçilmedi")
    
    with col_info2:
        st.markdown("### 📐 Mesafe")
        if len(points) >= 2:
            x1, y1 = points[0]
            x2, y2 = points[1]
            dist = int(np.sqrt((x2-x1)**2 + (y2-y1)**2))
            st.metric("Piksel Mesafesi", f"{dist} px")
        else:
            st.info("2 nokta seçildiğinde mesafe gösterilir")
    
    # --- KALİBRASYON ---
    st.markdown("---")
    st.subheader("📐 Kalibrasyon")
    
    if confirmed and len(points) >= 2:
        x1, y1 = points[0]
        x2, y2 = points[1]
        pixel_dist = np.sqrt((x2-x1)**2 + (y2-y1)**2)
        
        st.info(f"📏 Onaylanan mesafe: {int(pixel_dist)} px")
        
        real_mm = st.number_input(
            "Bu iki nokta arası gerçekte kaç mm?",
            min_value=1.0,
            value=50.0,
            step=1.0,
            help="Örneğin: Harf genişliği 50 mm ise 50 yazın"
        )
        
        col_cal1, col_cal2 = st.columns(2)
        with col_cal1:
            if st.button("✅ Kalibrasyonu Onayla", type="primary"):
                scale = pixel_dist / real_mm
                calib.pixel_per_mm = scale
                calib.is_calibrated = True
                st.session_state.calibrated = True
                st.success(f"✅ 1 mm = {scale:.2f} piksel")
                st.rerun()
        
        if st.session_state.calibrated:
            st.success("✅ Kalibrasyon tamamlandı! Devam edebilirsiniz.")
            
    elif len(points) >= 2 and not confirmed:
        st.info("👆 **Noktaları Onayla** butonuna tıklayarak noktaları onaylayın.")
    else:
        st.info("👆 Önce 2 nokta seçin (1. Nokta → 2. Nokta), sonra onaylayın.")
    
    return st.session_state.calibrated
