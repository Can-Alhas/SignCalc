"""app/ui/reports.py - Arayüz bileşeni"""


import streamlit as st
from datetime import datetime
from reporting.pdf_generator import PDFGenerator
from reporting.excel_generator import ExcelGenerator

def render_reports(processor, calib, price_result):
    """PDF ve Excel rapor butonları"""
    st.subheader("📄 Adım 4: Teklif Çıktısı")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 PDF Teklif Oluştur"):
            pdf_gen = PDFGenerator()
            pdf_buffer = pdf_gen.generate_offer(price_result)
            st.download_button(
                label="💾 PDF'yi İndir",
                data=pdf_buffer,
                file_name=f"Teklif_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf"
            )
    
    with col2:
        if st.button("📊 Excel Teklif Oluştur"):
            contour_summary = processor.get_contour_summary()
            excel_data = []
            for item in contour_summary:
                area_mm2_part, _ = calib.pixel_to_mm2(item["area_px"])
                perim_mm_part, _ = calib.pixel_to_mm(item["perimeter_px"])
                excel_data.append({
                    "Parça No": item["index"],
                    "Alan (mm²)": f"{area_mm2_part:.1f}",
                    "Çevre (mm)": f"{perim_mm_part:.1f}",
                    "Merkez X": item["center"][0],
                    "Merkez Y": item["center"][1]
                })
            
            excel_gen = ExcelGenerator()
            excel_buffer = excel_gen.generate_offer(price_result, excel_data)
            st.download_button(
                label="💾 Excel'i İndir",
                data=excel_buffer,
                file_name=f"Teklif_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col3:
        if st.button("🔄 Yeni Görsel için Sıfırla"):
            st.session_state.calibrated = False
            st.session_state.click_points = []
            st.session_state.calib.reset()
            st.session_state.nesting_result = None
            st.rerun()
