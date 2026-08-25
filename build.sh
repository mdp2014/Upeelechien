#!/bin/bash

set -e

cd "$(dirname "$0")"

echo
echo "========================================"
echo "🐶 UPEELECHIEN - BUILD"
echo "========================================"
echo

./nouvelle-version.sh

VERSION=$(sed -n '1s/^upeelechien (\([^)]*\)).*/\1/p' debian/changelog)

if [ -z "$VERSION" ]; then
    echo "❌ Impossible de récupérer la version."
    exit 1
fi

echo
echo "📦 Version : $VERSION"
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

echo
echo "========================================"
echo "✅ BUILD TERMINÉ"
echo "========================================"
echo

ls -lh "../upeelechien_${VERSION}"*.deb
