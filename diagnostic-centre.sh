#!/bin/bash

LOG="$HOME/upeelechien-centre.log"

{
echo "=========================================="
echo " DIAGNOSTIC UPEELECHIEN / GNOME SOFTWARE"
echo "=========================================="
echo

echo "=== SYSTEME ==="
lsb_release -a 2>/dev/null || true
echo
gnome-software --version 2>/dev/null || true
echo
appstreamcli --version 2>/dev/null || true
echo

echo "=== PAQUET INSTALLE ==="
dpkg-query -W -f='Package: ${Package}\nVersion: ${Version}\nStatus: ${Status}\n' upeelechien 2>&1 || true
echo

echo "=== FICHIERS INSTALLES ==="
dpkg -L upeelechien 2>/dev/null | grep -E 'desktop|metainfo|icon|Modelfile|usr/bin' || true
echo

echo "=== DESKTOP ==="
cat /usr/share/applications/upeelechien.desktop 2>/dev/null || true
echo

echo "=== METADATA APPSTREAM ==="
cat /usr/share/metainfo/com.upeelechien.Upeelechien.metainfo.xml 2>/dev/null || true
echo

echo "=== VALIDATION APPSTREAM ==="
appstreamcli validate /usr/share/metainfo/com.upeelechien.Upeelechien.metainfo.xml 2>&1 || true
echo

echo "=== CACHE APPSTREAM ==="
ls -lh /var/cache/swcatalog/ 2>/dev/null || true
echo

echo "=== RECHERCHE UPEELECHIEN DANS APPSTREAM ==="
appstreamcli search Upeelechien 2>&1 || true
echo

echo "=== ICONES ==="
ls -lh /usr/share/icons/hicolor/512x512/apps/upeelechien.png 2>&1 || true
file /usr/share/icons/hicolor/512x512/apps/upeelechien.png 2>&1 || true
echo

echo "=== DESKTOP DATABASE ==="
desktop-file-validate /usr/share/applications/upeelechien.desktop 2>&1 || true
echo

echo "=== JOURNAL GNOME SOFTWARE ==="
journalctl --user --since "2 hours ago" --no-pager 2>/dev/null \
  | grep -iE 'gnome-software|appstream|upeelechien|packagekit' || true
echo

echo "=== JOURNAL PACKAGEKIT ==="
journalctl --since "2 hours ago" --no-pager 2>/dev/null \
  | grep -iE 'packagekit|appstream|upeelechien' || true
echo

echo "=== PROCESSUS ==="
ps aux | grep -E 'gnome-software|packagekit' | grep -v grep || true
echo

echo "=========================================="
echo " FIN DU DIAGNOSTIC"
echo "=========================================="

} 2>&1 | tee "$LOG"

echo
echo "Diagnostic enregistré dans :"
echo "$LOG"
