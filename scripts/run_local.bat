@echo off
echo Starting ResumeRadar services...
echo.

:: Start each service in its own window
start "Auth Service (8001)" cmd /k "cd /d %~dp0..\services\auth-service && ..\..\venv\Scripts\activate && set DB_SCHEMA=auth_db && uvicorn app.main:app --port 8001 --reload"

start "Profile Service (8002)" cmd /k "cd /d %~dp0..\services\profile-service && ..\..\venv\Scripts\activate && set DB_SCHEMA=profile_db && uvicorn app.main:app --port 8002 --reload"

start "Matcher Service (8003)" cmd /k "cd /d %~dp0..\services\matcher-service && ..\..\venv\Scripts\activate && set DB_SCHEMA=matcher_db && uvicorn app.main:app --port 8003 --reload"

start "Tracker Service (8004)" cmd /k "cd /d %~dp0..\services\tracker-service && ..\..\venv\Scripts\activate && set DB_SCHEMA=tracker_db && uvicorn app.main:app --port 8004 --reload"

start "Analytics Service (8005)" cmd /k "cd /d %~dp0..\services\analytics-service && ..\..\venv\Scripts\activate && set DB_SCHEMA=analytics_db && uvicorn app.main:app --port 8005 --reload"

echo.
echo All services starting in separate windows.
echo Auth:      http://localhost:8001
echo Profile:   http://localhost:8002
echo Matcher:   http://localhost:8003
echo Tracker:   http://localhost:8004
echo Analytics: http://localhost:8005
echo.
echo Close the windows to stop services.