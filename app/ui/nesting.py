"""app/ui/nesting.py - Arayüz bileşeni"""


import streamlit as st
import pandas as pd
from nesting.optimizer import NestingOptimizer

def render_nesting(processor, calib):
    """Nesting arayüzü"""
    st.subheader("📐 Adım 3.5: Nesting (Yuvalama) Optimizasyonu")
    st.markdown("""
    **Nesting**, parçaları en az malzeme israfıyla bir levhaya yerleştirme optimizasyonudur.
    Aşağıda **Nesting (Optimize)** ile **Rastgele Yerleştirme** karşılaştırmasını görebilirsin.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        sheet_width = st.number_input("Levha Genişliği (mm)", min_value=100, value=400, step=50)
        sheet_height = st.number_input("Levha Yüksekliği (mm)", min_value=100, value=400, step=50)
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🧩 Nesting Hesapla ve Karşılaştır", type="primary"):
            if st.session_state.calibrated:
                _calculate_nesting(processor, calib, sheet_width, sheet_height)
            else:
                st.warning("⚠️ Lütfen önce kalibrasyon yapın!")

def _calculate_nesting(processor, calib, sheet_width, sheet_height):
    """Nesting hesaplama"""
    optimizer = NestingOptimizer(sheet_width, sheet_height)
    
    contour_data = processor.get_contours()
    parts = optimizer.prepare_parts(contour_data, calib.pixel_per_mm)
    
    if not parts:
        st.warning("⚠️ Yerleştirilecek parça bulunamadı!")
        return
    
    st.write(f"📦 **{len(parts)}** parça bulundu, yerleştiriliyor...")
    
    result = optimizer.optimize(parts)
    st.session_state.nesting_result = result
    
    if "error" in result:
        st.error(f"❌ {result['error']}")
        return
    
    # Sonuçları göster
    _show_nesting_results(result, optimizer)

def _show_nesting_results(result, optimizer):
    """Nesting sonuçlarını göster"""
    nesting = result["nesting"]
    random_res = result["random"]
    comp = result["comparison"]
    
    st.subheader("📊 Karşılaştırma Sonuçları")
    st.caption(f"🧩 Nesting: {nesting['placed_count']}/{result['total_parts']} parça | 🎲 Rastgele: {random_res['placed_count']}/{result['total_parts']} parça")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        delta_val = random_res['waste_percentage'] - nesting['waste_percentage']
        st.metric("🧩 Nesting İsrafı", f"%{nesting['waste_percentage']:.1f}", delta=f"-{delta_val:.1f}%" if delta_val > 0 else f"+{abs(delta_val):.1f}%", delta_color="inverse")
    with col2:
        st.metric("🎲 Rastgele İsrafı", f"%{random_res['waste_percentage']:.1f}")
    with col3:
        st.metric("💰 Malzeme Tasarrufu", f"%{comp['savings_percentage']:.1f}", delta="Tasarruf!" if comp['savings_percentage'] > 5 else "Tasarruf Yok", delta_color="normal")
    
    if comp['savings_percentage'] > 5:
        st.success(f"✅ **{comp['savings_percentage']:.1f}% malzeme tasarrufu!**")
    else:
        st.info(f"ℹ️ Tasarruf yok veya çok az! 💡 Öneri: Levha boyutunu küçült veya daha fazla parça içeren görsel yükle.")
    
    # Görsel karşılaştırma
    st.subheader("🖼️ Görsel Karşılaştırma")
    img_nesting, img_random = optimizer.draw_comparison(result, scale=2)
    
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        st.image(img_nesting, caption="🧩 Nesting (Optimize)", use_container_width=True)
        st.caption(f"İsraf: %{nesting['waste_percentage']:.1f} | Kullanılan: {nesting['used_area_mm2']:.0f} mm²")
    with col_img2:
        st.image(img_random, caption="🎲 Rastgele Yerleştirme", use_container_width=True)
        st.caption(f"İsraf: %{random_res['waste_percentage']:.1f} | Kullanılan: {random_res['used_area_mm2']:.0f} mm²")
    
    # Parça listesi
    with st.expander("📋 Yerleştirilen Parçalar (Detaylı)"):
        col_list1, col_list2 = st.columns(2)
        with col_list1:
            st.caption("🧩 Nesting Yerleşimi")
            if nesting["placed_parts"]:
                df = pd.DataFrame([{
                    "Parça #": p['part']['id'], "X": p['x'], "Y": p['y'], "Genişlik": p['width'], "Yükseklik": p['height']
                } for p in nesting["placed_parts"]])
                st.dataframe(df, use_container_width=True)
        with col_list2:
            st.caption("🎲 Rastgele Yerleşim")
            if random_res["placed_parts"]:
                df = pd.DataFrame([{
                    "Parça #": p['part']['id'], "X": p['x'], "Y": p['y'], "Genişlik": p['width'], "Yükseklik": p['height']
                } for p in random_res["placed_parts"]])
                st.dataframe(df, use_container_width=True)
