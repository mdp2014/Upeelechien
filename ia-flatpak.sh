#!/bin/bash

OLLAMA_URL="http://127.0.0.1:11434"
OLLAMA_MODEL="upeelechien-2"

echo "🐶 Upeelechien"
echo "=============="
echo
echo "⚡ Mode Flatpak"
echo

# Vérifier Ollama
if ! curl -sf "$OLLAMA_URL/api/tags" >/dev/null 2>&1; then
    echo "❌ Le serveur Ollama n'est pas accessible."
    echo
    echo "Vérifiez avec :"
    echo "  systemctl status ollama"
    exit 1
fi

echo "✅ Ollama accessible."
echo "🤖 Modèle : $OLLAMA_MODEL"
echo "🚀 Upeelechien est prêt."
echo

while true; do
    printf "Vous : "
    IFS= read -r PROMPT

    [ "$PROMPT" = "/quit" ] && break
    [ -z "$PROMPT" ] && continue

    echo
    echo "Upeelechien :"

    RESPONSE=$(python3 - "$OLLAMA_URL/api/generate" "$PROMPT" <<'PY'
import json
import sys
import urllib.request
import urllib.error

url = sys.argv[1]
prompt = sys.argv[2]

payload = {
    "model": "upeelechien-2",
    "prompt": prompt,
    "stream": False,
    "think": False
}

request = urllib.request.Request(
    url,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(request, timeout=300) as response:
        data = json.load(response)

    print(data.get("response", ""))

except urllib.error.HTTPError as e:
    print(f"❌ Ollama : HTTP {e.code}")
    print(e.read().decode(errors="replace"))

except Exception as e:
    print(f"❌ Erreur : {e}")
PY
)

    printf '%s\n' "$RESPONSE"
    echo
done
