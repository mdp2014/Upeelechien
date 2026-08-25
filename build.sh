#!/bin/bash

set -e

cd "$(dirname "$0")"

echo
echo "========================================"
echo "🐶 UPEELECHIEN - BUILD"
echo "========================================"
echo

./nouvelle-version.sh

VERSION=$(dpkg-parsechangelog -S Version 2>/dev/null || true)

if [ -z "$VERSION" ]; then
    echo "❌ Impossible de déterminer la version."
    exit 1
fi

echo "📦 Version : $VERSION"
echo

echo "🔎 Validation AppStream..."
appstreamcli validate com.upeelechien.Upeelechien.metainfo.xml

echo
echo "🧹 Nettoyage..."
rm -rf debian/upeelechien
rm -f ../upeelechien_*.deb
rm -f ../upeelechien_*.buildinfo
rm -f ../upeelechien_*.changes
rm -f ../upeelechien_*.dsc
rm -f ../upeelechien_*.tar.xz

echo
echo "🔨 Construction du paquet Debian..."
echo

dpkg-buildpackage -us -uc

DEB="../upeelechien_${VERSION}_amd64.deb"

echo
echo "🔎 Vérification du paquet..."
dpkg-deb --info "$DEB" | grep -E 'Package|Version|Architecture'

echo
echo "📂 Vérification des fichiers..."
dpkg-deb -c "$DEB" | grep -E \
'usr/bin/upeelechien|applications/upeelechien.desktop|metainfo/|icons/|Modelfile'

echo
echo "========================================"
echo "✅ BUILD TERMINÉ"
echo "========================================"
echo
ls -lh "$DEB"
