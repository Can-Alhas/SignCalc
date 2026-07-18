import numpy as np

class Calibration:
    """Ölçek kalibrasyonu sınıfı"""
    
    def __init__(self):
        self.points = []
        self.pixel_per_mm = None
        self.is_calibrated = False
        
    def add_point(self, x, y):
        """Nokta ekle"""
        self.points.append((x, y))
        return len(self.points)
    
    def reset(self):
        """Noktaları sıfırla"""
        self.points = []
        self.pixel_per_mm = None
        self.is_calibrated = False
    
    def get_pixel_distance(self):
        """İki nokta arasındaki piksel mesafesini hesapla"""
        if len(self.points) < 2:
            return None, "En az 2 nokta gerekli"
        
        x1, y1 = self.points[0]
        x2, y2 = self.points[1]
        distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance, None
    
    def calibrate(self, real_distance_mm):
        """Kalibrasyon yap"""
        pixel_dist, err = self.get_pixel_distance()
        if err:
            return None, err
        
        if pixel_dist == 0:
            return None, "Noktalar aynı yerde!"
        
        self.pixel_per_mm = pixel_dist / real_distance_mm
        self.is_calibrated = True
        return self.pixel_per_mm, None
    
    def pixel_to_mm(self, pixel_value):
        """Piksel -> mm dönüşümü"""
        if not self.is_calibrated or self.pixel_per_mm is None:
            return 0, "Önce kalibrasyon yapılmalı!"
        return pixel_value / self.pixel_per_mm, None
    
    def pixel_to_mm2(self, pixel_area):
        """Piksel² -> mm² dönüşümü"""
        if not self.is_calibrated or self.pixel_per_mm is None:
            return 0, "Önce kalibrasyon yapılmalı!"
        return pixel_area / (self.pixel_per_mm ** 2), None
