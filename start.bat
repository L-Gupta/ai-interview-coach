@echo off
REM Starts Docker Desktop if it isn't running, then brings up the whole stack.
REM Frontend: http://localhost:1500  Backend: http://localhost:1600  Database: localhost:1700
cd /d "%~dp0"

docker info >nul 2>&1
if errorlevel 1 (
    echo Docker engine is not running. Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    :wait
    timeout /t 5 /nobreak >nul
    docker info >nul 2>&1
    if errorlevel 1 goto wait
)

echo Docker engine is running. Starting containers...
docker compose up --build
