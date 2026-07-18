import sqlite3
import os
import json
from datetime import datetime

class DatabaseManager:
    """SQLite veritabanı yöneticisi"""
    
    def __init__(self, db_path="data/signcalc.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Veritabanı bağlantısı oluştur"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Veritabanını oluştur"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Malzemeler tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    price_per_mm2 REAL NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # İşçilik tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS labor (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    price_per_mm REAL NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Fire oranları tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fire_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    rate REAL NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Kullanıcı ayarları tablosu (genel ayarlar)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Varsayılan verileri ekle (eğer boşsa)
            self._insert_default_data(cursor)
            
            conn.commit()
    
    def _insert_default_data(self, cursor):
        """Varsayılan verileri ekle"""
        # Malzemeler
        default_materials = [
            ('Alüminyum', 0.045, 'Standart alüminyum levha'),
            ('Plexi', 0.032, 'Pleksiglas (Akrilik)'),
            ('LED Panel', 0.078, 'LED ışıklı panel'),
            ('Folyo', 0.015, 'Vinil folyo kaplama'),
            ('Profil', 0.056, 'Alüminyum profil')
        ]
        
        for name, price, desc in default_materials:
            cursor.execute('''
                INSERT OR IGNORE INTO materials (name, price_per_mm2, description)
                VALUES (?, ?, ?)
            ''', (name, price, desc))
        
        # İşçilik
        default_labor = [
            ('Standart Kesim', 0.012, 'Normal kesim işçiliği'),
            ('Detaylı Kesim', 0.018, 'İnce detaylı kesim'),
            ('Montaj', 0.025, 'Montaj işçiliği')
        ]
        
        for name, price, desc in default_labor:
            cursor.execute('''
                INSERT OR IGNORE INTO labor (name, price_per_mm, description)
                VALUES (?, ?, ?)
            ''', (name, price, desc))
        
        # Fire oranları
        default_fire = [
            ('Standart Fire', 1.10, 'Standart %10 fire'),
            ('Düşük Fire', 1.05, 'Düşük %5 fire'),
            ('Yüksek Fire', 1.20, 'Yüksek %20 fire')
        ]
        
        for name, rate, desc in default_fire:
            cursor.execute('''
                INSERT OR IGNORE INTO fire_rates (name, rate, description)
                VALUES (?, ?, ?)
            ''', (name, rate, desc))
        
        # Varsayılan ayarlar
        default_settings = [
            ('default_material', 'Alüminyum'),
            ('default_labor', 'Standart Kesim'),
            ('default_fire', 'Standart Fire'),
            ('company_name', 'SignCalc Otomasyon'),
            ('company_phone', '0 555 123 45 67'),
            ('company_address', 'İstanbul, Türkiye')
        ]
        
        for key, value in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value)
                VALUES (?, ?)
            ''', (key, value))
    
    # --- MATERIAL (Malzeme) İşlemleri ---
    def get_materials(self):
        """Tüm malzemeleri getir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, price_per_mm2, description FROM materials ORDER BY name')
            return cursor.fetchall()
    
    def get_material_by_name(self, name):
        """İsme göre malzeme getir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, price_per_mm2 FROM materials WHERE name = ?', (name,))
            return cursor.fetchone()
    
    def add_material(self, name, price_per_mm2, description=""):
        """Yeni malzeme ekle"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO materials (name, price_per_mm2, description)
                VALUES (?, ?, ?)
            ''', (name, price_per_mm2, description))
            conn.commit()
            return cursor.lastrowid
    
    def update_material(self, material_id, name, price_per_mm2, description=""):
        """Malzeme güncelle"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE materials 
                SET name = ?, price_per_mm2 = ?, description = ?
                WHERE id = ?
            ''', (name, price_per_mm2, description, material_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_material(self, material_id):
        """Malzeme sil"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM materials WHERE id = ?', (material_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # --- LABOR (İşçilik) İşlemleri ---
    def get_labor_types(self):
        """Tüm işçilik tiplerini getir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, price_per_mm, description FROM labor ORDER BY name')
            return cursor.fetchall()
    
    def get_labor_by_name(self, name):
        """İsme göre işçilik getir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, price_per_mm FROM labor WHERE name = ?', (name,))
            return cursor.fetchone()
    
    def add_labor(self, name, price_per_mm, description=""):
        """Yeni işçilik ekle"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO labor (name, price_per_mm, description)
                VALUES (?, ?, ?)
            ''', (name, price_per_mm, description))
            conn.commit()
            return cursor.lastrowid
    
    def update_labor(self, labor_id, name, price_per_mm, description=""):
        """İşçilik güncelle"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE labor 
                SET name = ?, price_per_mm = ?, description = ?
                WHERE id = ?
            ''', (name, price_per_mm, description, labor_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_labor(self, labor_id):
        """İşçilik sil"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM labor WHERE id = ?', (labor_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # --- FIRE RATE (Fire Oranı) İşlemleri ---
    def get_fire_rates(self):
        """Tüm fire oranlarını getir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, rate, description FROM fire_rates ORDER BY name')
            return cursor.fetchall()
    
    def get_fire_by_name(self, name):
        """İsme göre fire getir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, rate FROM fire_rates WHERE name = ?', (name,))
            return cursor.fetchone()
    
    def add_fire_rate(self, name, rate, description=""):
        """Yeni fire oranı ekle"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO fire_rates (name, rate, description)
                VALUES (?, ?, ?)
            ''', (name, rate, description))
            conn.commit()
            return cursor.lastrowid
    
    def update_fire_rate(self, fire_id, name, rate, description=""):
        """Fire oranı güncelle"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE fire_rates 
                SET name = ?, rate = ?, description = ?
                WHERE id = ?
            ''', (name, rate, description, fire_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_fire_rate(self, fire_id):
        """Fire oranı sil"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM fire_rates WHERE id = ?', (fire_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # --- SETTINGS (Ayarlar) İşlemleri ---
    def get_setting(self, key, default=None):
        """Ayarları getir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            return result[0] if result else default
    
    def set_setting(self, key, value):
        """Ayarları kaydet"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            conn.commit()
            return True
    
    def get_all_settings(self):
        """Tüm ayarları getir"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT key, value FROM settings')
            return {row[0]: row[1] for row in cursor.fetchall()}
    
    def get_default_material(self):
        """Varsayılan malzemeyi getir"""
        return self.get_setting('default_material', 'Alüminyum')
    
    def get_default_labor(self):
        """Varsayılan işçiliği getir"""
        return self.get_setting('default_labor', 'Standart Kesim')
    
    def get_default_fire(self):
        """Varsayılan fire oranını getir"""
        return self.get_setting('default_fire', 'Standart Fire')
    
    def get_company_info(self):
        """Firma bilgilerini getir"""
        return {
            'name': self.get_setting('company_name', 'SignCalc Otomasyon'),
            'phone': self.get_setting('company_phone', '0 555 123 45 67'),
            'address': self.get_setting('company_address', 'İstanbul, Türkiye')
        }
