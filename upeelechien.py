#!/usr/bin/env python3

import json
import os
import shutil
import subprocess
import sys
import threading
import urllib.error
import urllib.request

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib


APP_NAME = "Upeelechien"
VERSION = "2.4"
MODEL = "upeelechien-2"
OLLAMA_URL = "http://127.0.0.1:11434"


def ollama_available():
    try:
        with urllib.request.urlopen(
            f"{OLLAMA_URL}/api/tags",
            timeout=3
        ) as response:
            return response.status == 200
    except Exception:
        return False


def model_available():
    try:
        with urllib.request.urlopen(
            f"{OLLAMA_URL}/api/tags",
            timeout=3
        ) as response:
            data = json.loads(response.read().decode())
            return any(
                model.get("name", "").split(":")[0] == MODEL
                or model.get("name") == MODEL
                for model in data.get("models", [])
            )
    except Exception:
        return False


def show_help():
    print(f"""Upeelechien {VERSION}

Utilisation :
  upeelechien              Lance l'interface graphique
  upeelechien --help       Affiche cette aide
  upeelechien --version    Affiche la version
  upeelechien --status     Vérifie Ollama et le modèle
  upeelechien --model      Affiche le modèle utilisé
  upeelechien --remove-model
                           Supprime le modèle Upeelechien d'Ollama
  upeelechien --uninstall  Désinstalle Upeelechien
  upeelechien --purge      Désinstalle Upeelechien et supprime ses données

Modèle :
  {MODEL}

Serveur Ollama :
  {OLLAMA_URL}
""")


def show_version():
    print(f"{APP_NAME} {VERSION}")


def show_model():
    print(f"Modèle : {MODEL}")


def show_status():
    print(f"{APP_NAME} {VERSION}")
    print()

    if ollama_available():
        print("✅ Ollama : accessible")
    else:
        print("❌ Ollama : inaccessible")

    if model_available():
        print(f"✅ Modèle : {MODEL}")
    else:
        print(f"❌ Modèle : {MODEL} absent")


def remove_model():
    print(f"Suppression du modèle {MODEL}...")

    if not ollama_available():
        print("❌ Impossible de contacter Ollama.")
        print("Lancez Ollama avec : ollama serve")
        return 1

    result = subprocess.run(
        ["ollama", "rm", MODEL],
        text=True
    )

    if result.returncode == 0:
        print(f"✅ Modèle {MODEL} supprimé.")
        return 0

    print("❌ Impossible de supprimer le modèle.")
    return result.returncode


def uninstall():
    print("Désinstallation de Upeelechien")
    print()
    print("Cette commande ne supprime pas Ollama.")
    print("Elle ne supprime pas non plus vos autres modèles.")
    print()

    answer = input("Confirmer la désinstallation ? [o/N] : ").strip().lower()

    if answer not in ("o", "oui"):
        print("Annulation.")
        return 0

    print()

    if shutil.which("apt"):
        print("Suppression du paquet Debian...")
        result = subprocess.run(
            ["sudo", "apt", "remove", "-y", "upeelechien"]
        )

        if result.returncode == 0:
            print("✅ Upeelechien a été désinstallé.")
            return 0

    if shutil.which("flatpak"):
        print("Suppression du paquet Flatpak...")
        subprocess.run(
            ["flatpak", "uninstall", "-y", "io.github.mdp2014.Upeelechien"]
        )

    print("⚠️ Désinstallation automatique terminée.")
    print("Si nécessaire, utilisez le gestionnaire de paquets de votre système.")

    return 0


def purge():
    print("SUPPRESSION COMPLÈTE DE UPEELECHIEN")
    print()
    print("Cette opération peut supprimer :")
    print("- l'application Upeelechien")
    print("- le modèle Ollama upeelechien-2")
    print("- les données de configuration locales")
    print()
    print("Ollama lui-même ne sera PAS supprimé.")
    print()

    answer = input("Confirmer la suppression complète ? [o/N] : ").strip().lower()

    if answer not in ("o", "oui"):
        print("Annulation.")
        return 0

    print()
    remove_model()

    config_paths = [
        os.path.expanduser("~/.config/upeelechien"),
        os.path.expanduser("~/.local/share/upeelechien"),
        os.path.expanduser("~/.cache/upeelechien"),
    ]

    for path in config_paths:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
            print(f"🗑️ Supprimé : {path}")

    if shutil.which("apt"):
        subprocess.run(
            ["sudo", "apt", "remove", "-y", "upeelechien"]
        )

    if shutil.which("flatpak"):
        subprocess.run(
            ["flatpak", "uninstall", "-y", "io.github.mdp2014.Upeelechien"]
        )

    print()
    print("✅ Suppression complète terminée.")
    return 0


class UpeelechienWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        super().__init__(application=app)

        self.set_title("Upeelechien")
        self.set_default_size(900, 650)

        main = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0
        )
        self.set_child(main)

        header = Gtk.HeaderBar()

        title = Gtk.Label(label="🐶 Upeelechien")
        header.set_title_widget(title)

        main.append(header)

        self.chat = Gtk.TextView()
        self.chat.set_editable(False)
        self.chat.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(self.chat)

        main.append(scrolled)

        bottom = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )
        bottom.set_margin_top(8)
        bottom.set_margin_bottom(8)
        bottom.set_margin_start(8)
        bottom.set_margin_end(8)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Écrivez votre message...")
        self.entry.set_hexpand(True)
        self.entry.connect("activate", self.send_message)

        send = Gtk.Button(label="Envoyer")
        send.connect("clicked", self.send_message)

        bottom.append(self.entry)
        bottom.append(send)

        main.append(bottom)

        self.write_chat(
            "Upeelechien",
            "Bonjour ! Je suis Upeelechien 5.6, "
            "une IA française développée par Marin."
        )

    def write_chat(self, speaker, message):
        buffer = self.chat.get_buffer()
        end = buffer.get_end_iter()

        buffer.insert(
            end,
            f"{speaker} :\n{message}\n\n"
        )

    def send_message(self, widget):
        prompt = self.entry.get_text().strip()

        if not prompt:
            return

        self.entry.set_text("")
        self.write_chat("Vous", prompt)

        thread = threading.Thread(
            target=self.ask_ollama,
            args=(prompt,),
            daemon=True
        )
        thread.start()

    def ask_ollama(self, prompt):
        payload = json.dumps({
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "think": False
        }).encode()

        request = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=payload,
            headers={
                "Content-Type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=120
            ) as response:
                data = json.loads(
                    response.read().decode()
                )

            answer = data.get(
                "response",
                "Aucune réponse."
            )

        except urllib.error.URLError:
            answer = "Erreur : impossible de contacter Ollama."

        except Exception as error:
            answer = f"Erreur : {error}"

        GLib.idle_add(
            self.write_chat,
            "Upeelechien",
            answer
        )


class UpeelechienApplication(Gtk.Application):

    def __init__(self):
        super().__init__(
            application_id="io.github.mdp2014.Upeelechien"
        )

    def do_activate(self):
        window = UpeelechienWindow(self)
        window.present()


def main():
    if "--help" in sys.argv:
        show_help()
        return 0

    if "--version" in sys.argv:
        show_version()
        return 0

    if "--status" in sys.argv:
        show_status()
        return 0

    if "--model" in sys.argv:
        show_model()
        return 0

    if "--remove-model" in sys.argv:
        return remove_model()

    if "--uninstall" in sys.argv:
        return uninstall()

    if "--purge" in sys.argv:
        return purge()

    app = UpeelechienApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
