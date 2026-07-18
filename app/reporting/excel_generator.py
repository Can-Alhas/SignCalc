import pandas as pd
from datetime import datetime
import io

class ExcelGenerator:
    """Excel rapor oluşturucu"""
    
    def generate_offer(self, price_data, contour_data=None):
        """Excel teklif oluştur"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Özet Sayfası
            summary_data = {
                'Parametre': ['Toplam Alan (mm²)', 'Toplam Çevre (mm)', 'Malzeme Katsayısı (TL/mm²)', 
                             'İşçilik Katsayısı (TL/mm)', 'Fire Oranı', 'Malzeme Maliyeti (TL)',
                             'İşçilik Maliyeti (TL)', 'TOPLAM FİYAT (TL)'],
                'Değer': [
                    f"{price_data['area_mm2']:.1f}",
                    f"{price_data['perimeter_mm']:.1f}",
                    f"{price_data['material_cost']:.3f}",
                    f"{price_data['labor_cost']:.3f}",
                    f"%{int((price_data['fire_rate']-1)*100)}",
                    f"{price_data['raw_material']:.2f}",
                    f"{price_data['labor']:.2f}",
                    f"{price_data['total']:.2f}"
                ]
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Özet', index=False)
            
            # Parça Detayları
            if contour_data:
                df_parts = pd.DataFrame(contour_data)
                df_parts.to_excel(writer, sheet_name='Parça Detayları', index=False)
            
            # Firma Bilgileri
            info_data = {
                'Bilgi': ['Firma', 'Tarih', 'Geçerlilik'],
                'Değer': ['SignCalc Otomasyon', datetime.now().strftime('%d.%m.%Y %H:%M'), '15 Gün']
            }
            df_info = pd.DataFrame(info_data)
            df_info.to_excel(writer, sheet_name='Bilgiler', index=False)
        
        output.seek(0)
        return output
