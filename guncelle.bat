@echo off
echo ===================================================
echo MYKEEP TICKET SISTEMI - OTOMATIK GUNCELLEME ARACI
echo ===================================================
echo.

echo [1/4] GitHub'dan en yeni kodlar cekiliyor...
git pull origin main
echo.

echo [2/4] Veritabani guncellemeleri (Migration) yapiliyor...
python manage.py migrate
echo.

echo [3/4] Statik dosyalar (Tasarim, CSS, JS) toplaniyor...
python manage.py collectstatic --noinput
echo.

echo [4/4] Guncelleme islemi basariyla tamamlandi!
echo Lutfen sunucunuzu (IIS, Gunicorn, Waitress vb.) yeniden baslatin.
echo ===================================================
pause
