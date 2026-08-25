#!/bin/bash

# ============================================================
# UPEELECHIEN 5.6
# ============================================================

# ------------------------------------------------------------
# Désinstallation complète
# ------------------------------------------------------------

if [ "$1" = "sup" ]; then

    clear

    echo "╔══════════════════════════════════════════════╗"
    echo "║       SUPPRESSION DE UPEELECHIEN 5.6       ║"
    echo "╠══════════════════════════════════════════════╣"
    echo "║  Ollama + Qwen + Upeelechien                ║"
    echo "╚══════════════════════════════════════════════╝"
    echo

    read -p "⚠️ Supprimer Upeelechien, Ollama et Qwen ? [o/N] " REPONSE

    if [[ ! "$REPONSE" =~ ^[oO]$ ]]; then
        echo
        echo "❌ Annulation."
        exit 0
    fi

    echo
    echo "🧹 Suppression en cours..."
    echo

    # Arrêter Ollama
    if command -v systemctl >/dev/null 2>&1; then
        echo "⚙️ Arrêt du service Ollama..."
        sudo systemctl stop ollama 2>/dev/null || true
        sudo systemctl disable ollama 2>/dev/null || true
    fi

    # Supprimer les modèles
    if command -v ollama >/dev/null 2>&1; then
        echo "🧠 Suppression de Upeelechien..."
        ollama rm upeelechien-5-6 2>/dev/null || true

        echo "🧠 Suppression de Qwen3 1.7B..."
        ollama rm qwen3:1.7b 2>/dev/null || true
    fi

    # Supprimer Ollama
    echo "🗑️ Suppression d'Ollama..."

    sudo rm -f /usr/local/bin/ollama
    sudo rm -f /usr/bin/ollama
    sudo rm -f /snap/bin/ollama

    sudo rm -rf /usr/local/lib/ollama
    sudo rm -rf /usr/share/ollama
    sudo rm -rf /var/lib/ollama

    sudo rm -f /etc/systemd/system/ollama.service
    sudo rm -rf /etc/systemd/system/ollama.service.d

    sudo systemctl daemon-reload 2>/dev/null || true

    # Supprimer le paquet Upeelechien
    echo "🗑️ Suppression du paquet Upeelechien..."

    sudo dpkg --remove upeelechien 2>/dev/null || true

    echo
    echo "╔══════════════════════════════════════════════╗"
    echo "║              ✅ TERMINÉ                     ║"
    echo "╠══════════════════════════════════════════════╣"
    echo "║ Upeelechien supprimé                        ║"
    echo "║ Ollama supprimé                              ║"
    echo "║ Qwen3 1.7B supprimé                          ║"
    echo "║ Données Ollama supprimées                    ║"
    echo "╚══════════════════════════════════════════════╝"
    echo

    exit 0
fi


# ------------------------------------------------------------
# Aide
# ------------------------------------------------------------

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then

    echo
    echo "UPEELECHIEN 5.6"
    echo
    echo "Utilisation :"
    echo
    echo "  upeelechien"
    echo "      Lance Upeelechien."
    echo
    echo "  upeelechien sup"
    echo "      Supprime Upeelechien, Ollama et Qwen3 1.7B."
    echo
    echo "  upeelechien --help"
    echo "      Affiche cette aide."
    echo

    exit 0
fi


# ------------------------------------------------------------
# Lancement normal
# ------------------------------------------------------------

clear

echo "╔══════════════════════════════════════════════╗"
echo "║              UPEELECHIEN 5.6                ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  Modèle : Qwen3 1.7B                        ║"
echo "║  Thinking : OFF ⚡                           ║"
echo "║                                              ║"
echo "║  IA française 🇫🇷                           ║"
echo "║  Développeur : Marin le BG 😎              ║"
echo "║                                              ║"
echo "╚══════════════════════════════════════════════╝"
echo

ollama run upeelechien-5-6 --think=false
