@echo off
chcp 65001 > nul
echo ===================================================
echo กำลังติดตั้งไลบรารี Playwright และเบราว์เซอร์ Chromium
echo ===================================================
python -m pip install --upgrade pip
python -m pip install playwright
python -m playwright install chromium
echo.
echo ===================================================
echo ติดตั้งเสร็จสมบูรณ์! กดปุ่มใดก็ได้เพื่อปิดหน้าต่างนี้
echo ===================================================
pause
