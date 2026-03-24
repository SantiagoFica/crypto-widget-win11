@echo off
echo Instalando PyInstaller...
pip install pyinstaller --quiet

echo Empaquetando Crypto Widget...
pyinstaller --noconfirm --onefile --windowed ^
  --name "CryptoWidget" ^
  --add-data "app;app" ^
  main.py

echo.
echo Listo! El ejecutable esta en: dist\CryptoWidget.exe
pause
