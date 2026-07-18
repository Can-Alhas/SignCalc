from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import io

class PDFGenerator:
    """PDF teklif oluşturucu"""
    
    def __init__(self, company_name="SignCalc Otomasyon"):
        self.company_name = company_name
    
    def generate_offer(self, price_data):
        """Teklif PDF'i oluştur"""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Başlık
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "TEKLİF")
        
        # Firma bilgileri
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, self.company_name)
        c.drawString(50, height - 85, "Tabela ve Reklam Üretimi")
        c.drawString(50, height - 100, f"Tarih: {datetime.now().strftime('%d.%m.%Y')}")
        
        # Çizgi
        c.line(50, height - 110, width - 50, height - 110)
        
        # Ölçümler
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 140, "ÖLÇÜM SONUÇLARI")
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 160, f"Toplam Alan: {price_data['area_mm2']:.1f} mm²")
        c.drawString(50, height - 175, f"Toplam Çevre: {price_data['perimeter_mm']:.1f} mm")
        
        # Fiyat Hesaplama
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 210, "FİYAT HESAPLAMA")
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 230, f"Malzeme ({price_data['material_cost']:.3f} TL/mm²): {price_data['raw_material']:.2f} TL")
        c.drawString(50, height - 245, f"İşçilik ({price_data['labor_cost']:.3f} TL/mm): {price_data['labor']:.2f} TL")
        c.drawString(50, height - 260, f"Fire Oranı: %{int((price_data['fire_rate']-1)*100)}")
        
        # Çizgi
        c.line(50, height - 275, width - 50, height - 275)
        
        # Toplam Fiyat
        c.setFont("Helvetica-Bold", 16)
        c.setFillColorRGB(0, 0.5, 0)
        c.drawString(50, height - 310, f"TOPLAM FİYAT: {price_data['total']:.2f} TL")
        c.setFillColorRGB(0, 0, 0)
        
        # Alt bilgi
        c.setFont("Helvetica", 8)
        c.drawString(50, 50, "Bu teklif otomatik olarak oluşturulmuştur.")
        c.drawString(50, 35, "Geçerlilik süresi 15 gündür.")
        
        c.save()
        buffer.seek(0)
        return buffer
