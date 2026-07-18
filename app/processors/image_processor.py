import cv2
import numpy as np

class ImageProcessor:
    """Görüntü işleme ve kontur analizi sınıfı"""
    
    def __init__(self, image, svg_paths=None):
        self.image = image
        self.height, self.width = image.shape[:2] if image is not None else (0, 0)
        self.contours = []
        self.contour_data = []
        self.total_area_px = 0
        self.total_perimeter_px = 0
        self.svg_paths = svg_paths
        
    def process(self):
        """Ana işleme fonksiyonu"""
        if self.image is None:
            return self
            
        # Gri tonlama
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # Eşikleme (threshold) - otomatik optimize
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # Konturları bul
        self.contours, _ = cv2.findContours(
            thresh, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Her konturu analiz et
        for cnt in self.contours:
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)
            
            if area > 100:  # Gürültü filtrele
                self.contour_data.append({
                    "area_px": area,
                    "perimeter_px": perimeter,
                    "contour": cnt,
                    "center": self._get_center(cnt)
                })
        
        # Toplam hesaplamaları
        self.total_area_px = sum([c["area_px"] for c in self.contour_data])
        self.total_perimeter_px = sum([c["perimeter_px"] for c in self.contour_data])
        
        return self
    
    def _get_center(self, contour):
        """Konturun merkezini bul"""
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return (cx, cy)
        return (0, 0)
    
    def draw_contours(self, image, color=(0, 255, 0)):
        """Konturları görsel üzerine çiz"""
        img_copy = image.copy()
        
        for data in self.contour_data:
            cv2.drawContours(img_copy, [data["contour"]], -1, color, 2)
            
            # Merkeze alan bilgisini yaz
            cx, cy = data["center"]
            if cx != 0 and cy != 0:
                cv2.putText(
                    img_copy, 
                    f"{int(data['area_px'])}px", 
                    (cx-20, cy), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.4, 
                    (255, 0, 0), 
                    1
                )
        return img_copy
    
    def get_contours(self):
        """Kontur verilerini döndür"""
        return self.contour_data
    
    def get_total_area(self):
        """Toplam alanı döndür (piksel²)"""
        return self.total_area_px
    
    def get_total_perimeter(self):
        """Toplam çevreyi döndür (piksel)"""
        return self.total_perimeter_px
    
    def get_contour_count(self):
        """Kontur sayısını döndür"""
        return len(self.contour_data)
    
    def get_contour_summary(self):
        """Tüm konturların özetini döndür"""
        summary = []
        for i, data in enumerate(self.contour_data):
            summary.append({
                "index": i + 1,
                "area_px": data["area_px"],
                "perimeter_px": data["perimeter_px"],
                "center": data["center"]
            })
        return summary
