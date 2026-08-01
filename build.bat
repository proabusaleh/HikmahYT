@echo off
REM ============================================================
REM  HikmahYT - Windows build script
REM  Produces a ready-to-ship app in dist\HikmahYT\
REM ============================================================
setlocal

cd /d "%~dp0"

echo [1/4] Installing build dependencies...
python -m pip install -r requirements.txt -r requirements-build.txt
if errorlevel 1 goto :error

echo [2/4] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/4] Building HikmahYT.exe...
python -m PyInstaller --noconfirm --clean HikmahYT.spec
if errorlevel 1 goto :error

REM Remove the intermediate build folder - its HikmahYT.exe is NOT runnable
REM on its own and only causes confusion. Use dist\HikmahYT\HikmahYT.exe.
echo [4/4] Removing intermediate build folder...
if exist build rmdir /s /q build

REM Package the app as a single distributable zip
if exist "dist\HikmahYT-v1.0.0-win64.zip" del "dist\HikmahYT-v1.0.0-win64.zip"
powershell -NoProfile -Command "Compress-Archive -Path 'dist\HikmahYT' -DestinationPath 'dist\HikmahYT-v1.0.0-win64.zip' -Force"

echo.
echo ============================================================
echo  Build complete!
echo  Run:     dist\HikmahYT\HikmahYT.exe
echo  Dist:    dist\HikmahYT-v1.0.0-win64.zip
echo.
echo  NOTE: keep the whole HikmahYT folder together - the exe
echo  needs the "_internal" folder next to it.
echo ============================================================
goto :eof

:error
echo.
echo Build FAILED.
exit /b 1
