#!/bin/bash

set -e

CHANGELOG="debian/changelog"

if [ ! -f "$CHANGELOG" ]; then
    echo "❌ debian/changelog introuvable."
    exit 1
fi

# Récupérer la dernière version
VERSION=$(sed -n '1s/^upeelechien (\([^)]*\)).*/\1/p' "$CHANGELOG")

if [ -z "$VERSION" ]; then
    echo "❌ Impossible de trouver la version."
    exit 1
fi

# Séparer majeure et mineure
MAJOR="${VERSION%%.*}"
MINOR="${VERSION##*.}"

# Incrémenter la version mineure
NEW_MINOR=$((MINOR + 1))
NEW_VERSION="${MAJOR}.${NEW_MINOR}"

echo "🐶 Version actuelle : $VERSION"
echo "🚀 Nouvelle version : $NEW_VERSION"

DATE=$(date -R)

TMP=$(mktemp)

{
    echo "upeelechien (${NEW_VERSION}) unstable; urgency=medium"
    echo
    echo "  * Nouvelle version de Upeelechien."
    echo
    echo " -- Marin <marin.depibrac@gmail.com>  $DATE"
    echo
    cat "$CHANGELOG"
} > "$TMP"

mv "$TMP" "$CHANGELOG"

echo
echo "✅ Version mise à jour : $NEW_VERSION"
