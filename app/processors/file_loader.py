import cv2
import numpy as np
from PIL import Image
import io
import os
import tempfile
import subprocess
import streamlit as st

class FileLoader:
    """Farklı dosya formatlarını yükleme sınıfı"""
    
    @staticmethod
    def is_streamlit_cloud():
        """Streamlit Cloud ortamında mı çalışıyor?"""
        return os.environ.get('STREAMLIT_SHARING_MODE') == 'true' or \
               os.environ.get('IS_STREAMLIT_CLOUD') == 'true' or \
               'STREAMLIT_SERVER_MAX_UPLOAD_SIZE' in os.environ
    
    @staticmethod
    def load_image(uploaded_file):
        """PNG/JPG yükle"""
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        return img
    
    @staticmethod
    def load_svg(uploaded_file):
        """SVG yükle - svgpathtools ile"""
        try:
            import svgpathtools
            from svgpathtools import svg2paths
            
            with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            
            paths, attributes = svg2paths(tmp_path)
            
            from cairosvg import svg2png
            png_path = tmp_path.replace('.svg', '.png')
            svg2png(url=tmp_path, write_to=png_path)
            
            img = cv2.imread(png_path)
            
            os.unlink(tmp_path)
            if os.path.exists(png_path):
                os.unlink(png_path)
            
            return img, paths
            
        except ImportError as e:
            raise ImportError(f"SVG için gerekli kütüphane yok: {e}")
        except Exception as e:
            raise Exception(f"SVG okuma hatası: {e}")
    
    @staticmethod
    def load_dxf(uploaded_file):
        """DXF yükle - ezdxf ile"""
        try:
            import ezdxf
            from ezdxf.addons.drawing import RenderContext, Frontend
            from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
            import matplotlib.pyplot as plt
            
            with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            
            doc = ezdxf.read(tmp_path)
            msp = doc.modelspace()
            
            fig = plt.figure(figsize=(10, 10))
            ax = fig.add_axes([0, 0, 1, 1])
            ctx = RenderContext(doc)
            out = MatplotlibBackend(ax)
            Frontend(ctx, out).draw_layout(msp, finalize=True)
            
            fig.canvas.draw()
            img = np.array(fig.canvas.renderer._renderer)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            plt.close(fig)
            
            os.unlink(tmp_path)
            return img
            
        except ImportError as e:
            raise ImportError(f"DXF için gerekli kütüphane yok: {e}")
        except Exception as e:
            raise Exception(f"DXF okuma hatası: {e}")
    
    @staticmethod
    def load_pdf(uploaded_file):
        """PDF yükle - PyMuPDF ile"""
        try:
            import fitz
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            
            doc = fitz.open(tmp_path)
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            doc.close()
            os.unlink(tmp_path)
            return img
            
        except ImportError as e:
            raise ImportError(f"PDF için gerekli kütüphane yok: {e}")
        except Exception as e:
            raise Exception(f"PDF okuma hatası: {e}")
    
    @staticmethod
    def load_ai(uploaded_file):
        """AI (Adobe Illustrator) yükle - PDF uyumlu AI dosyalarını okur"""
        try:
            import fitz
            
            with tempfile.NamedTemporaryFile(suffix='.ai', delete=False) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            
            doc = fitz.open(tmp_path)
            
            if doc.page_count == 0:
                raise Exception("AI dosyası sayfa içermiyor veya PDF uyumlu değil")
            
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            doc.close()
            os.unlink(tmp_path)
            
            st.success("✅ AI dosyası başarıyla okundu!")
            return img
            
        except ImportError as e:
            raise ImportError(f"AI için gerekli kütüphane yok: {e}")
        except Exception as e:
            st.warning("⚠️ AI dosyası okunamadı. PDF uyumlu olarak kaydedilmiş olmalı.")
            st.info("💡 Adobe Illustrator'da 'PDF Uyumlu' seçeneğini işaretleyerek kaydedin.")
            raise Exception(f"AI okuma hatası: {e}")
    
    @staticmethod
    def load_eps(uploaded_file):
        """EPS yükle - Ghostscript ile (Cloud'da devre dışı)"""
        
        # Streamlit Cloud'da mı?
        if FileLoader.is_streamlit_cloud():
            st.warning("⚠️ EPS dosyaları Streamlit Cloud'da desteklenmiyor.")
            st.info("💡 Lütfen PNG, JPG, SVG veya PDF formatını kullanın.")
            raise Exception("EPS Cloud'da desteklenmiyor")
        
        try:
            from PIL import Image
            
            # Ghostscript kontrolü (sadece local'de)
            try:
                result = subprocess.run(['gs', '--version'], capture_output=True, check=True)
                st.info(f"✅ Ghostscript bulundu: {result.stdout.decode().strip()}")
            except (subprocess.SubprocessError, FileNotFoundError):
                st.warning("⚠️ Ghostscript kurulu değil! EPS dosyaları açılamayabilir.")
                st.info("💡 Ubuntu/Debian: sudo apt install ghostscript")
                st.info("💡 macOS: brew install ghostscript")
                raise Exception("Ghostscript kurulu değil!")
            
            # EPS'yi oku
            eps_image = Image.open(uploaded_file)
            
            if eps_image.mode != 'RGB':
                eps_image = eps_image.convert('RGB')
            
            width, height = eps_image.size
            if width > 2000 or height > 2000:
                eps_image.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
            
            img = np.array(eps_image)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            st.success("✅ EPS dosyası başarıyla okundu!")
            return img
            
        except ImportError as e:
            raise ImportError(f"EPS için gerekli kütüphane yok: {e}")
        except Exception as e:
            st.warning(f"⚠️ EPS okuma hatası: {str(e)}")
            raise Exception(f"EPS okuma hatası: {e}")
