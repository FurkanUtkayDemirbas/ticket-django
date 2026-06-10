#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PANEL_DIR="$ROOT_DIR/panel"
TS="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$ROOT_DIR/deploy_backups/$TS"

echo "==================================================="
echo "MYKEEP TICKET SISTEMI - OTOMATIK GUNCELLEME ARACI"
echo "==================================================="
echo ""

echo "[1/5] Canli veritabani yedekleniyor..."
mkdir -p "$BACKUP_DIR"
if [ -f "$PANEL_DIR/db.sqlite3" ]; then
    cp -p "$PANEL_DIR/db.sqlite3" "$BACKUP_DIR/db.sqlite3"
    echo "    db.sqlite3 yedeklendi."
else
    echo "    db.sqlite3 bulunamadi, yedek atlandi."
fi
if [ -f "$ROOT_DIR/identifier.sqlite" ]; then
    cp -p "$ROOT_DIR/identifier.sqlite" "$BACKUP_DIR/identifier.sqlite"
    echo "    identifier.sqlite yedeklendi."
fi
echo ""

echo "[2/5] GitHub'dan en yeni kodlar cekiliyor..."
git -C "$ROOT_DIR" checkout -- panel/db.sqlite3 identifier.sqlite >/dev/null 2>&1 || true
git -C "$ROOT_DIR" pull origin main
echo ""

echo "[3/5] Canli veritabani geri yukleniyor..."
if [ -f "$BACKUP_DIR/db.sqlite3" ]; then
    cp -p "$BACKUP_DIR/db.sqlite3" "$PANEL_DIR/db.sqlite3"
    echo "    db.sqlite3 korundu."
fi
if [ -f "$BACKUP_DIR/identifier.sqlite" ]; then
    cp -p "$BACKUP_DIR/identifier.sqlite" "$ROOT_DIR/identifier.sqlite"
    echo "    identifier.sqlite korundu."
fi
echo ""

echo "[4/5] Veritabani guncellemeleri (Migration) yapiliyor..."
cd "$PANEL_DIR"
python manage.py migrate
echo ""

echo "[5/5] Statik dosyalar (Tasarim, CSS, JS) toplaniyor..."
python manage.py collectstatic --noinput
echo ""

echo "Guncelleme islemi basariyla tamamlandi!"
echo "Veritabani yedegi: $BACKUP_DIR"
echo "Lutfen sunucunuzu (IIS, Gunicorn, Nginx vb.) yeniden baslatin."
echo "==================================================="
