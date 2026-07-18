from setuptools import setup, find_packages

setup(
    name="signcalc",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.28.0",
        "opencv-python-headless>=4.8.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "reportlab>=4.0.0",
        "openpyxl>=3.1.5",
        "pandas>=2.0.0",
        "PyMuPDF>=1.23.0",
        "matplotlib>=3.7.0",
        "streamlit-image-coordinates>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "signcalc=app.main:main",
        ],
    },
    python_requires=">=3.8",
)
