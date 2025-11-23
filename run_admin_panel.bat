@echo off
echo ========================================
echo Starting Admin Panel
echo ========================================
cd admin_panel
if not exist node_modules (
    echo Installing Node.js dependencies...
    npm install
)
echo.
echo Starting development server...
echo Admin Panel will be available at: http://localhost:5173
echo.
npm run dev
pause

