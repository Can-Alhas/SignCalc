
class PriceCalculator:
    """Fiyat hesaplama motoru"""
    
    def __init__(self, material_cost=0.045, labor_cost=0.012, fire_rate=1.10):
        self.material_cost = material_cost
        self.labor_cost = labor_cost
        self.fire_rate = fire_rate
    
    def calculate(self, area_mm2, perimeter_mm):
        """Fiyat hesapla"""
        raw_material = area_mm2 * self.material_cost
        labor = perimeter_mm * self.labor_cost
        total = (raw_material + labor) * self.fire_rate
        
        return {
            "raw_material": raw_material,
            "labor": labor,
            "total": total,
            "area_mm2": area_mm2,
            "perimeter_mm": perimeter_mm,
            "fire_rate": self.fire_rate,
            "material_cost": self.material_cost,
            "labor_cost": self.labor_cost
        }
    
    def update_parameters(self, material_cost=None, labor_cost=None, fire_rate=None):
        """Parametreleri güncelle"""
        if material_cost is not None:
            self.material_cost = material_cost
        if labor_cost is not None:
            self.labor_cost = labor_cost
        if fire_rate is not None:
            self.fire_rate = fire_rate
