#!/bin/bash
set -e

VERSION_FILE="VERSION"
CHANGELOG="debian/changelog"

if [ ! -f "$VERSION_FILE" ]; then
    echo "2.0" > "$VERSION_FILE"
    echo "📦 Version initialisée : 2.0"
else
    CURRENT=$(tr -d '[:space:]' < "$VERSION_FILE")

    if [[ "$CURRENT" == "1."* ]]; then
        NEW_VERSION="2.0"
    elif [[ "$CURRENT" =~ ^([0-9]+)\.([0-9]+)$ ]]; then
        MAJOR="${BASH_REMATCH[1]}"
        MINOR="${BASH_REMATCH[2]}"
        NEW_VERSION="$MAJOR.$((MINOR + 1))"
    else
        echo "❌ Version invalide : $CURRENT"
        exit 1
    fi

    echo "$NEW_VERSION" > "$VERSION_FILE"
    echo "🐶 Version actuelle : $CURRENT"
    echo "🚀 Nouvelle version : $NEW_VERSION"
    echo "✅ Version mise à jour : $NEW_VERSION"
fi

VERSION=$(tr -d '[:space:]' < "$VERSION_FILE")

# Synchronisation automatique du changelog Debian
if [ -f "$CHANGELOG" ]; then
    sed -i -E "1s/^upeelechien \([^)]*\)/upeelechien ($VERSION)/" "$CHANGELOG"
fi

echo "📦 Version : $VERSION"
