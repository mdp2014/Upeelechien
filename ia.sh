#!/bin/bash

# ============================================================
# UPEELECHIEN 5.6
# ============================================================

OLLAMA_MODEL="upeelechien-5-6"
QWEN_MODEL="qwen3:1.7b"
MODELFILE="/usr/share/upeelechien/Modelfile"

# ============================================================
# INSTALLATION AU PREMIER LANCEMENT
# ============================================================

installer_ia() {

    echo
    echo "🐶 Première installation de Upeelechien"
    echo "========================================"
    echo

    # --------------------------------------------------------
    # Vérifier Ollama
    # --------------------------------------------------------

    if command -v ollama >/dev/null 2>&1; then
        echo "✅ Ollama est déjà installé."
    else
        echo "📦 Ollama n'est pas installé."
        echo "⬇️ Installation d'Ollama..."
        echo

        if ! command -v curl >/dev/null 2>&1; then
            echo "📦 Installation de curl..."
            sudo apt-get update
            sudo apt-get install -y curl
        fi

        curl -fsSL https://ollama.com/install.sh | sh

        if ! command -v ollama >/dev/null 2>&1; then
            echo "❌ Impossible d'installer Ollama."
            return 1
        fi

        echo "✅ Ollama installé."
    fi

    # --------------------------------------------------------
    # Démarrer Ollama
    # --------------------------------------------------------

    echo
    echo "⚙️ Démarrage d'Ollama..."

    if command -v systemctl >/dev/null 2>&1; then
        sudo systemctl enable --now ollama 2>/dev/null || true
    fi

    # Si le service n'existe pas, lancer Ollama nous-mêmes
    if ! curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
        echo "⏳ Démarrage du serveur Ollama..."

        ollama serve >/tmp/upeelechien-ollama.log 2>&1 &
        OLLAMA_PID=$!

        for i in {1..30}; do
            if curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
                break
            fi
            sleep 1
        done
    fi

    # --------------------------------------------------------
    # Vérifier Ollama
    # --------------------------------------------------------

    if ! curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
        echo
        echo "❌ Ollama ne répond pas."
        echo "Consulte : /tmp/upeelechien-ollama.log"
        return 1
    fi

    echo "✅ Ollama est prêt."

    # --------------------------------------------------------
    # Installer Qwen
    # --------------------------------------------------------

    echo
    echo "🧠 Vérification de Qwen3 1.7B..."

    if ollama list 2>/dev/null | awk '{print $1}' | grep -qx "$QWEN_MODEL"; then
        echo "✅ Qwen3 1.7B est déjà installé."
    else
        echo "⬇️ Téléchargement de Qwen3 1.7B..."
        echo "Cela peut prendre plusieurs minutes."
        echo

        if ! ollama pull "$QWEN_MODEL"; then
            echo
            echo "❌ Impossible de télécharger Qwen3 1.7B."
            return 1
        fi

        echo
        echo "✅ Qwen3 1.7B installé."
    fi

    # --------------------------------------------------------
    # Créer Upeelechien
    # --------------------------------------------------------

    echo
    echo "🐶 Vérification de Upeelechien..."

    if ollama list 2>/dev/null | awk '{print $1}' | grep -qx "$OLLAMA_MODEL"; then
        echo "✅ Upeelechien est déjà installé."
    else

        if [ ! -f "$MODELFILE" ]; then
            echo "❌ Modelfile introuvable :"
            echo "   $MODELFILE"
            return 1
        fi

        echo "⚙️ Création du modèle Upeelechien..."

        if ! ollama create "$OLLAMA_MODEL" -f "$MODELFILE"; then
            echo "❌ Impossible de créer Upeelechien."
            return 1
        fi

        echo "✅ Upeelechien créé."
    fi

    echo
    echo "========================================"
    echo "✅ Installation de Upeelechien terminée !"
    echo "========================================"
    echo

    return 0
}


# ============================================================
# SUPPRESSION COMPLÈTE
# ============================================================

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
        echo "⚙️ Arrêt d'Ollama..."
        sudo systemctl stop ollama 2>/dev/null || true
        sudo systemctl disable ollama 2>/dev/null || true
    fi

    # Supprimer les modèles
    if command -v ollama >/dev/null 2>&1; then

        echo "🧠 Suppression de Upeelechien..."
        ollama rm "$OLLAMA_MODEL" 2>/dev/null || true

        echo "🧠 Suppression de Qwen3 1.7B..."
        ollama rm "$QWEN_MODEL" 2>/dev/null || true

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

    # Supprimer le paquet
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


# ============================================================
# AIDE
# ============================================================

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


# ============================================================
# PREMIER LANCEMENT
# ============================================================

if ! command -v ollama >/dev/null 2>&1 || \
   ! ollama list 2>/dev/null | awk '{print $1}' | grep -qx "$OLLAMA_MODEL"; then

    installer_ia

    if [ $? -ne 0 ]; then
        echo
        echo "❌ L'installation de Upeelechien a échoué."
        echo
        exit 1
    fi
fi


# ============================================================
# LANCEMENT NORMAL
# ============================================================

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

ollama run "upeelechien-2" --think=false
