@echo off
echo ====================================================================
echo             BloomCare Gynecology System Launcher
echo ====================================================================
echo.
echo Installing requirements...
pip install -r requirements.txt
echo.
echo Starting Django Development Server...
cd backend
python manage.py runserver
pause
