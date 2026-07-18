"""app/ui/sidebar.py - Arayüz bileşeni"""


import streamlit as st
from database.db_manager import DatabaseManager

def render_sidebar():
    """Sidebar'ı render et"""
    db = DatabaseManager()
    
    st.sidebar.header("⚙️ Fiyat Parametreleri")
    
    # Malzeme seçimi
    materials = db.get_materials()
    material_names = [m[1] for m in materials] if materials else ["Alüminyum"]
    default_material = db.get_default_material()
    material_index = material_names.index(default_material) if default_material in material_names else 0
    
    selected_material = st.sidebar.selectbox("Malzeme", material_names, index=material_index)
    material_data = db.get_material_by_name(selected_material)
    material_cost = material_data[2] if material_data else 0.045
    
    # İşçilik seçimi
    labor_types = db.get_labor_types()
    labor_names = [l[1] for l in labor_types] if labor_types else ["Standart Kesim"]
    default_labor = db.get_default_labor()
    labor_index = labor_names.index(default_labor) if default_labor in labor_names else 0
    
    selected_labor = st.sidebar.selectbox("İşçilik Tipi", labor_names, index=labor_index)
    labor_data = db.get_labor_by_name(selected_labor)
    labor_cost = labor_data[2] if labor_data else 0.012
    
    # Fire oranı seçimi
    fire_rates = db.get_fire_rates()
    fire_names = [f[1] for f in fire_rates] if fire_rates else ["Standart Fire"]
    default_fire = db.get_default_fire()
    fire_index = fire_names.index(default_fire) if default_fire in fire_names else 0
    
    selected_fire = st.sidebar.selectbox("Fire Oranı", fire_names, index=fire_index)
    fire_data = db.get_fire_by_name(selected_fire)
    fire_rate = fire_data[2] if fire_data else 1.10
    
    st.sidebar.markdown("---")
    st.sidebar.info("📌 1. Görsel yükle\n2. Kalibrasyon yap\n3. Fiyatı gör\n4. Nesting ile optimize et")
    
    # Yönetim Paneli
    with st.sidebar.expander("🔧 Yönetim Paneli", expanded=False):
        _render_admin_panel(db)
    
    st.sidebar.markdown("---")
    st.sidebar.caption("🪧 SignCalc v1.0")
    
    return material_cost, labor_cost, fire_rate

def _render_admin_panel(db):
    """Yönetim paneli"""
    st.subheader("🏷️ Malzeme Yönetimi")
    
    col1, col2 = st.columns(2)
    with col1:
        new_material = st.text_input("Malzeme Adı", key="new_mat_name")
    with col2:
        new_material_price = st.number_input("Fiyat (TL/mm²)", min_value=0.001, value=0.045, step=0.001, key="new_mat_price")
    
    if st.button("➕ Malzeme Ekle"):
        if new_material and new_material_price:
            try:
                db.add_material(new_material, new_material_price)
                st.success(f"✅ {new_material} eklendi!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Hata: {e}")
    
    st.subheader("🔧 İşçilik Yönetimi")
    col3, col4 = st.columns(2)
    with col3:
        new_labor = st.text_input("İşçilik Adı", key="new_labor_name")
    with col4:
        new_labor_price = st.number_input("Fiyat (TL/mm)", min_value=0.001, value=0.012, step=0.001, key="new_labor_price")
    
    if st.button("➕ İşçilik Ekle"):
        if new_labor and new_labor_price:
            try:
                db.add_labor(new_labor, new_labor_price)
                st.success(f"✅ {new_labor} eklendi!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Hata: {e}")
    
    st.subheader("🔥 Fire Oranı Yönetimi")
    col5, col6 = st.columns(2)
    with col5:
        new_fire = st.text_input("Fire Adı", key="new_fire_name")
    with col6:
        new_fire_rate = st.number_input("Oran (1.10 = %10)", min_value=1.0, value=1.10, step=0.01, key="new_fire_rate")
    
    if st.button("➕ Fire Oranı Ekle"):
        if new_fire and new_fire_rate:
            try:
                db.add_fire_rate(new_fire, new_fire_rate)
                st.success(f"✅ {new_fire} eklendi!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Hata: {e}")
