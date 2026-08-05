@echo off
REM ============================================================
REM  HikmahYT - Windows build script
REM  Produces a ready-to-ship app in dist\HikmahYT\
REM ============================================================
setlocal

cd /d "%~dp0"

REM Keep in sync with version_info.txt and ui/main_window.py APP_VERSION
set VERSION=5.0.0
set ZIP_NAME=HikmahYT-v5-pro-win64.zip

echo [1/4] Installing build dependencies...
python -m pip install -r requirements.txt -r requirements-build.txt
if errorlevel 1 goto :error

echo [2/4] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/4] Building HikmahYT.exe (v%VERSION%)...
python -m PyInstaller --noconfirm --clean HikmahYT.spec
if errorlevel 1 goto :error

REM Remove the intermediate build folder - its HikmahYT.exe is NOT runnable
REM on its own and only causes confusion. Use dist\HikmahYT\HikmahYT.exe.
echo [4/4] Removing intermediate build folder...
for /l %%i in (1,1,5) do (
  if exist build (
    rmdir /s /q build 2>nul
    if not exist build goto :buildclean
    ping -n 3 127.0.0.1 >nul
  )
)
:buildclean

REM Package the app as a single distributable zip. Uses .NET ZipFile (not
REM Compress-Archive) with retries to survive antivirus/Defender file locks.
if exist "dist\%ZIP_NAME%" del "dist\%ZIP_NAME%"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$src = 'dist\HikmahYT'; $zip = Join-Path (Get-Location) ('dist' + [IO.Path]::DirectorySeparatorChar + '%ZIP_NAME%');" ^
  "Add-Type -AssemblyName System.IO.Compression.FileSystem;" ^
  "$ok = $false;" ^
  "for ($i = 0; $i -lt 10 -and -not $ok; $i++) {" ^
  "  try { [IO.Compression.ZipFile]::CreateFromDirectory($src, $zip, [IO.Compression.CompressionLevel]::Optimal, $false); $ok = $true }" ^
  "  catch { Start-Sleep -Seconds 2 }" ^
  "};" ^
  "if (-not $ok) { Write-Error 'Failed to create zip'; exit 1 }"
if errorlevel 1 goto :error

echo.
echo ============================================================
echo  Build complete!
echo  Run:     dist\HikmahYT\HikmahYT.exe
echo  Dist:    dist\%ZIP_NAME%
echo.
echo  NOTE: keep the whole HikmahYT folder together - the exe
echo  needs the "_internal" folder next to it.
echo ============================================================
goto :eof

:error
echo.
echo Build FAILED.
exit /b 1
