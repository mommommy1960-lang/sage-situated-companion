@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Commons Live Ensemble
color 0B

set "APPDIR=%LOCALAPPDATA%\CommonsLiveEnsemble"
set "CODEDIR=%APPDIR%\code"
set "VENV=%APPDIR%\venv"
set "ZIPFILE=%TEMP%\commons-live-ensemble.zip"
set "EXTRACT=%TEMP%\commons-live-ensemble-extract"
set "REPOZIP=https://github.com/mommommy1960-lang/sage-situated-companion/archive/refs/heads/livecast-ai-mvp.zip"

echo.
echo ======================================================
echo        COMMONS LIVE ENSEMBLE - ONE CLICK START
echo ======================================================
echo.

if not exist "%APPDIR%" mkdir "%APPDIR%"

rem Keep a permanent copy and put a shortcut on the Desktop.
if /I not "%~f0"=="%APPDIR%\START COMMONS LIVE ENSEMBLE.bat" (
  copy /Y "%~f0" "%APPDIR%\START COMMONS LIVE ENSEMBLE.bat" >nul 2>&1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws=New-Object -ComObject WScript.Shell; $p=[Environment]::GetFolderPath('Desktop'); $s=$ws.CreateShortcut((Join-Path $p 'Commons Live Ensemble.lnk')); $s.TargetPath='%APPDIR%\START COMMONS LIVE ENSEMBLE.bat'; $s.WorkingDirectory='%APPDIR%'; $s.IconLocation='shell32.dll,220'; $s.Save()" >nul 2>&1

rem Download the app automatically the first time.
if not exist "%CODEDIR%\START_LIVECAST.py" (
  echo [1/4] Getting your Live Ensemble app...
  if exist "%EXTRACT%" rmdir /S /Q "%EXTRACT%"
  if exist "%ZIPFILE%" del /Q "%ZIPFILE%"
  mkdir "%EXTRACT%" >nul 2>&1
  powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing '%REPOZIP%' -OutFile '%ZIPFILE%'; Expand-Archive -Force '%ZIPFILE%' '%EXTRACT%'" 
  if errorlevel 1 goto :downloadfail
  for /d %%D in ("%EXTRACT%\sage-situated-companion-*") do (
    if exist "%CODEDIR%" rmdir /S /Q "%CODEDIR%"
    mkdir "%CODEDIR%" >nul 2>&1
    xcopy "%%~fD\*" "%CODEDIR%\" /E /I /Q /Y >nul
  )
)

rem Find Python, or install it automatically with winget when available.
echo [2/4] Checking the engine...
set "PYEXE="
if exist "%VENV%\Scripts\python.exe" goto :havevenv

where py >nul 2>&1
if not errorlevel 1 (
  py -3 -c "import sys; print(sys.version)" >nul 2>&1
  if not errorlevel 1 set "PYLAUNCH=py -3"
)
if defined PYLAUNCH goto :makevenv

where python >nul 2>&1
if not errorlevel 1 (
  python -c "import sys; print(sys.version)" >nul 2>&1
  if not errorlevel 1 set "PYLAUNCH=python"
)
if defined PYLAUNCH goto :makevenv

echo Python is not installed. Installing it for you...
where winget >nul 2>&1
if errorlevel 1 goto :pythonfail
winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements --silent

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
  if exist "%%~fD\python.exe" set "PYEXE=%%~fD\python.exe"
)
if not defined PYEXE goto :pythonfail
goto :makevenvexe

:makevenv
echo [3/4] Preparing the private app environment...
%PYLAUNCH% -m venv "%VENV%"
if errorlevel 1 goto :fail
goto :havevenv

:makevenvexe
echo [3/4] Preparing the private app environment...
"%PYEXE%" -m venv "%VENV%"
if errorlevel 1 goto :fail

:havevenv
if not exist "%VENV%\.livecast_ready" (
  echo [4/4] Installing the Live Ensemble pieces. First launch can take a few minutes...
  "%VENV%\Scripts\python.exe" -m pip install --disable-pip-version-check --upgrade pip
  "%VENV%\Scripts\python.exe" -m pip install --disable-pip-version-check -r "%CODEDIR%\apps\livecast\requirements.txt"
  if errorlevel 1 goto :fail
  echo ready>"%VENV%\.livecast_ready"
) else (
  echo [4/4] Everything is ready.
)

echo.
echo Starting your show control room now...
echo A browser window will open. Use the big START TIKTOK LISTENER button there.
echo.
cd /d "%CODEDIR%"
"%VENV%\Scripts\python.exe" START_LIVECAST.py
goto :end

:downloadfail
echo.
echo I could not download the Live Ensemble from GitHub.
echo Check that this computer is online, then double-click this button again.
goto :pausefail

:pythonfail
echo.
echo I could not install Python automatically on this Windows computer.
echo Nothing was damaged. Keep this window open and show the message to Sage.
goto :pausefail

:fail
echo.
echo The launcher hit an installation error. Nothing was deleted from your personal files.
echo Keep this window open and show the error above to Sage.

:pausefail
pause

:end
endlocal
