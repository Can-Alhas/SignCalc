"""app/ui/results.py - Arayüz bileşeni"""


import streamlit as st
import pandas as pd

def render_results(processor, calib, price_result):
    """Ölçüm ve fiyat sonuçlarını göster"""
    st.subheader("📊 Adım 2: Ölçüm ve Fiyat")
    
    total_area_px = processor.get_total_area()
    total_perimeter_px = processor.get_total_perimeter()
    
    area_mm2, _ = calib.pixel_to_mm2(total_area_px)
    perimeter_mm, _ = calib.pixel_to_mm(total_perimeter_px)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📐 Toplam Alan", f"{area_mm2:.1f} mm²")
    with col2:
        st.metric("📏 Toplam Çevre", f"{perimeter_mm:.1f} mm")
    with col3:
        st.metric("💰 Tahmini Fiyat", f"{price_result['total']:.2f} TL")
        st.caption(f"Malzeme: {price_result['raw_material']:.2f} TL | İşçilik: {price_result['labor']:.2f} TL | Fire: %{int((price_result['fire_rate']-1)*100)}")
    
    # Parça detayları
    st.subheader("🔍 Adım 3: Tespit Edilen Parçalar")
    
    contour_summary = processor.get_contour_summary()
    if contour_summary:
        df_data = []
        for item in contour_summary:
            area_mm2_part, _ = calib.pixel_to_mm2(item["area_px"])
            perim_mm_part, _ = calib.pixel_to_mm(item["perimeter_px"])
            df_data.append({
                "Parça #": item["index"],
                "Alan (mm²)": f"{area_mm2_part:.1f}",
                "Çevre (mm)": f"{perim_mm_part:.1f}",
                "Merkez X": item["center"][0],
                "Merkez Y": item["center"][1]
            })
        st.dataframe(pd.DataFrame(df_data), use_container_width=True)
    
    return area_mm2, perimeter_mm
