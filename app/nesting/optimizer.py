
import numpy as np
import cv2
import random
from typing import List, Dict, Tuple

class NestingOptimizer:
    """Nesting (Yuvalama) optimizasyon sınıfı - BASİT VE KESİN"""
    
    def __init__(self, sheet_width_mm=500, sheet_height_mm=500):
        self.sheet_width_mm = sheet_width_mm
        self.sheet_height_mm = sheet_height_mm
        self.placed_parts = []
        self.used_area = 0
        self.waste_percentage = 0
        self.random_placed_parts = []
        self.random_used_area = 0
        self.random_waste_percentage = 0
        
    def prepare_parts(self, contour_data, pixel_per_mm):
        """Kontur verilerini nesting için hazırla"""
        parts = []
        for i, data in enumerate(contour_data):
            # Konturun minimum dikdörtgenini bul
            contour = data["contour"]
            rect = cv2.minAreaRect(contour)
            width = rect[1][0]
            height = rect[1][1]
            
            # Piksel -> mm dönüşümü
            width_mm = max(width / pixel_per_mm, 5)
            height_mm = max(height / pixel_per_mm, 5)
            
            # Alan (mm²)
            area_mm2 = data["area_px"] / (pixel_per_mm ** 2)
            
            parts.append({
                "id": i + 1,
                "contour": contour,
                "width_mm": width_mm,
                "height_mm": height_mm,
                "area_mm2": area_mm2,
                "center": data["center"],
                "rect": rect,
                "rotated": False
            })
        
        # Büyükten küçüğe sırala
        parts.sort(key=lambda x: x["area_mm2"], reverse=True)
        return parts
    
    def _random_place_simple(self, grid: np.ndarray, part: Dict) -> Tuple[int, int]:
        """ÇOK BASİT: Parçayı tamamen rastgele bir yere yerleştir"""
        sheet_h, sheet_w = grid.shape
        w = int(part["width_mm"])
        h = int(part["height_mm"])
        
        if w > sheet_w or h > sheet_h:
            return None
        
        # 500 defa rastgele dene
        for _ in range(500):
            x = random.randint(0, sheet_w - w)
            y = random.randint(0, sheet_h - h)
            
            # Bu alan boş mu?
            if np.sum(grid[y:y+h, x:x+w]) == 0:
                return (x, y)
        
        # Hiç yer bulunamadı
        return None
    
    def _nesting_place(self, grid: np.ndarray, part: Dict) -> Tuple[int, int]:
        """NESTING: Parçayı en uygun yere yerleştir (sol-üstten başlayarak)"""
        sheet_h, sheet_w = grid.shape
        w = int(part["width_mm"])
        h = int(part["height_mm"])
        
        if w > sheet_w or h > sheet_h:
            return None
        
        # Grid üzerinde soldan sağa, yukarıdan aşağıya tara
        for y in range(sheet_h - h + 1):
            for x in range(sheet_w - w + 1):
                if np.sum(grid[y:y+h, x:x+w]) == 0:
                    return (x, y)
        
        return None
    
    def optimize(self, parts: List[Dict]) -> Dict:
        """Ana nesting optimizasyonu"""
        if not parts:
            return {"error": "Parça bulunamadı!"}
        
        # === NESTING (OPTİMİZE) - Sol-üstten yerleştir ===
        grid_opt = np.zeros((int(self.sheet_height_mm), int(self.sheet_width_mm)))
        placed_opt = []
        
        for part in parts:
            pos = self._nesting_place(grid_opt, part)
            if pos:
                x, y = pos
                w = int(part["width_mm"])
                h = int(part["height_mm"])
                grid_opt[y:y+h, x:x+w] = 1
                placed_opt.append({
                    "part": part,
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h
                })
        
        # === RASTGELE YERLEŞTİRME ===
        grid_rand = np.zeros((int(self.sheet_height_mm), int(self.sheet_width_mm)))
        placed_rand = []
        
        for part in parts:
            pos = self._random_place_simple(grid_rand, part)
            if pos:
                x, y = pos
                w = int(part["width_mm"])
                h = int(part["height_mm"])
                grid_rand[y:y+h, x:x+w] = 1
                placed_rand.append({
                    "part": part,
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h
                })
        
        # === HESAPLAMALAR ===
        sheet_area = self.sheet_width_mm * self.sheet_height_mm
        
        used_opt = np.sum(grid_opt)
        used_rand = np.sum(grid_rand)
        
        waste_opt = ((sheet_area - used_opt) / sheet_area) * 100
        waste_rand = ((sheet_area - used_rand) / sheet_area) * 100
        
        savings = waste_rand - waste_opt
        savings_pct = (savings / waste_rand) * 100 if waste_rand > 0 else 0
        
        self.placed_parts = placed_opt
        self.random_placed_parts = placed_rand
        
        return {
            "total_parts": len(parts),
            "sheet_area_mm2": sheet_area,
            
            "nesting": {
                "used_area_mm2": used_opt,
                "waste_percentage": waste_opt,
                "placed_parts": placed_opt,
                "grid": grid_opt,
                "placed_count": len(placed_opt)
            },
            
            "random": {
                "used_area_mm2": used_rand,
                "waste_percentage": waste_rand,
                "placed_parts": placed_rand,
                "grid": grid_rand,
                "placed_count": len(placed_rand)
            },
            
            "comparison": {
                "savings": savings,
                "savings_percentage": savings_pct
            }
        }
    
    def draw_result(self, grid: np.ndarray, parts: List[Dict], scale=2) -> np.ndarray:
        """Sonucu görselleştir"""
        sheet_h, sheet_w = grid.shape
        scaled_w = int(sheet_w * scale)
        scaled_h = int(sheet_h * scale)
        
        img = np.ones((scaled_h, scaled_w, 3), dtype=np.uint8) * 255
        
        # Dolu alanları yeşil yap
        for y in range(sheet_h):
            for x in range(sheet_w):
                if grid[y, x] == 1:
                    cv2.rectangle(img, (x*scale, y*scale), ((x+1)*scale, (y+1)*scale), (200, 230, 200), -1)
        
        # Parçaları çiz
        colors = [
            (255, 50, 50), (50, 200, 50), (50, 50, 255),
            (255, 200, 0), (255, 0, 200), (0, 200, 255),
            (200, 100, 0), (100, 0, 200)
        ]
        
        for i, placed in enumerate(parts):
            color = colors[i % len(colors)]
            x = placed["x"] * scale
            y = placed["y"] * scale
            w = placed["width"] * scale
            h = placed["height"] * scale
            
            cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
            cv2.putText(img, f"#{placed['part']['id']}", (x+3, y+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        cv2.rectangle(img, (0, 0), (scaled_w-1, scaled_h-1), (0, 0, 0), 3)
        return img
    
    def draw_comparison(self, result: Dict, scale=2) -> Tuple[np.ndarray, np.ndarray]:
        """Karşılaştırma görselleri"""
        img_nesting = self.draw_result(result["nesting"]["grid"], result["nesting"]["placed_parts"], scale)
        img_random = self.draw_result(result["random"]["grid"], result["random"]["placed_parts"], scale)
        return img_nesting, img_random
