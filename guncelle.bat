@echo off
setlocal
set ROOT_DIR=%~dp0
set PANEL_DIR=%ROOT_DIR%panel

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i
set BACKUP_DIR=%ROOT_DIR%deploy_backups\%TS%

echo ===================================================
echo MYKEEP TICKET SISTEMI - OTOMATIK GUNCELLEME ARACI
echo ===================================================
echo.

echo [1/5] Canli veritabani yedekleniyor...
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
if exist "%PANEL_DIR%\db.sqlite3" (
    copy /Y "%PANEL_DIR%\db.sqlite3" "%BACKUP_DIR%\db.sqlite3" >nul
    echo     db.sqlite3 yedeklendi.
) else (
    echo     db.sqlite3 bulunamadi, yedek atlandi.
)
if exist "%ROOT_DIR%identifier.sqlite" (
    copy /Y "%ROOT_DIR%identifier.sqlite" "%BACKUP_DIR%\identifier.sqlite" >nul
    echo     identifier.sqlite yedeklendi.
)
echo.

echo [2/5] GitHub'dan en yeni kodlar cekiliyor...
git -C "%ROOT_DIR%" checkout -- panel/db.sqlite3 identifier.sqlite >nul 2>nul
git -C "%ROOT_DIR%" pull origin main
if errorlevel 1 (
    echo Git guncellemesi basarisiz oldu. Veritabani yedegi su klasorde: %BACKUP_DIR%
    pause
    exit /b 1
)
echo.

echo [3/5] Canli veritabani geri yukleniyor...
if exist "%BACKUP_DIR%\db.sqlite3" (
    copy /Y "%BACKUP_DIR%\db.sqlite3" "%PANEL_DIR%\db.sqlite3" >nul
    echo     db.sqlite3 korundu.
)
if exist "%BACKUP_DIR%\identifier.sqlite" (
    copy /Y "%BACKUP_DIR%\identifier.sqlite" "%ROOT_DIR%identifier.sqlite" >nul
    echo     identifier.sqlite korundu.
)
echo.

echo [4/5] Veritabani guncellemeleri (Migration) yapiliyor...
pushd "%PANEL_DIR%"
python manage.py migrate
if errorlevel 1 (
    popd
    echo Migration basarisiz oldu. Veritabani yedegi su klasorde: %BACKUP_DIR%
    pause
    exit /b 1
)
echo.

echo [5/5] Statik dosyalar (Tasarim, CSS, JS) toplaniyor...
python manage.py collectstatic --noinput
if errorlevel 1 (
    popd
    echo Statik dosyalar toplanirken hata olustu.
    pause
    exit /b 1
)
popd
echo.

echo Guncelleme islemi basariyla tamamlandi!
echo Veritabani yedegi: %BACKUP_DIR%
echo Lutfen sunucunuzu (IIS, Gunicorn, Waitress vb.) yeniden baslatin.
echo ===================================================
pause
