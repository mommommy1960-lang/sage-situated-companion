@echo off
setlocal
cd /d %~dp0

echo.
echo === Commons Live Ensemble ===
echo.

if not exist .venv\Scripts\python.exe (
  echo Creating local Python environment...
  py -m venv .venv
  if errorlevel 1 goto :fail
)

call .venv\Scripts\activate.bat

if not exist .venv\.livecast_ready (
  echo Installing Live Ensemble dependencies. This happens once...
  python -m pip install --upgrade pip
  python -m pip install -r apps\livecast\requirements.txt
  if errorlevel 1 goto :fail
  echo ready>.venv\.livecast_ready
)

python START_LIVECAST.py
goto :end

:fail
echo.
echo START FAILED. Python 3 may not be installed, or a dependency could not install.
echo Keep this window open and copy the error so it can be fixed.
pause

:end
endlocal
