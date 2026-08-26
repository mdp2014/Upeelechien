#!/usr/bin/env python3

import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib


APP_NAME = "Upeelechien"
VERSION = "3.1"

MODEL = "upeelechien-5-6"
QWEN_MODEL = "qwen3:1.7b"

OLLAMA_URL = "http://127.0.0.1:11434"
MODELFILE = "/usr/share/upeelechien/Modelfile"


# ============================================================
# OLLAMA
# ============================================================

def ollama_available():
    try:
        with urllib.request.urlopen(
            f"{OLLAMA_URL}/api/tags",
            timeout=3
        ) as response:
            return response.status == 200
    except Exception:
        return False


def ollama_installed():
    return shutil.which("ollama") is not None


def get_models():
    try:
        with urllib.request.urlopen(
            f"{OLLAMA_URL}/api/tags",
            timeout=5
        ) as response:
            data = json.loads(response.read().decode())
            return data.get("models", [])
    except Exception:
        return []


def model_available(model_name):
    for model in get_models():
        name = model.get("name", "")

        if name == model_name:
            return True

        if name.split(":")[0] == model_name:
            return True

    return False


def start_ollama():
    if ollama_available():
        return True

    if not ollama_installed():
        return False

    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
    except Exception:
        return False

    for _ in range(30):
        if ollama_available():
            return True

        time.sleep(1)

    return False


def install_ollama():
    if ollama_installed():
        return True

    try:
        result = subprocess.run(
            [
                "pkexec",
                "bash",
                "-c",
                "curl -fsSL https://ollama.com/install.sh | sh"
            ],
            timeout=300
        )

        return (
            result.returncode == 0
            and ollama_installed()
        )

    except Exception:
        return False


def pull_qwen():
    if model_available(QWEN_MODEL):
        return True

    try:
        result = subprocess.run(
            ["ollama", "pull", QWEN_MODEL],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=1800
        )

        return result.returncode == 0

    except Exception:
        return False


def create_upeelechien_model():
    if model_available(MODEL):
        return True

    if not os.path.exists(MODELFILE):
        return False

    try:
        result = subprocess.run(
            [
                "ollama",
                "create",
                MODEL,
                "-f",
                MODELFILE
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=1800
        )

        return result.returncode == 0

    except Exception:
        return False


# ============================================================
# COMMANDES TERMINAL
# ============================================================

def show_help():
    print(f"""
Upeelechien {VERSION}

Utilisation :

upeelechien
    Lance l'interface graphique

upeelechien --help
    Affiche cette aide

upeelechien --version
    Affiche la version

upeelechien --status
    Vérifie Ollama et les modèles

upeelechien --model
    Affiche le modèle utilisé

upeelechien --remove-model
    Supprime le modèle Upeelechien

upeelechien --uninstall
    Désinstalle Upeelechien

upeelechien --purge
    Désinstalle Upeelechien et ses données

Modèle :
{MODEL}

Qwen :
{QWEN_MODEL}

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

    if model_available(QWEN_MODEL):
        print(f"✅ Qwen : {QWEN_MODEL}")
    else:
        print(f"❌ Qwen : {QWEN_MODEL} absent")

    if model_available(MODEL):
        print(f"✅ Upeelechien : {MODEL}")
    else:
        print(f"❌ Upeelechien : {MODEL} absent")


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

    answer = input(
        "Confirmer la désinstallation ? [o/N] : "
    ).strip().lower()

    if answer not in ("o", "oui"):
        print("Annulation.")
        return 0

    if shutil.which("apt"):
        result = subprocess.run(
            ["sudo", "apt", "remove", "-y", "upeelechien"]
        )

        if result.returncode == 0:
            print("✅ Upeelechien a été désinstallé.")
            return 0

    if shutil.which("flatpak"):
        subprocess.run(
            [
                "flatpak",
                "uninstall",
                "-y",
                "io.github.mdp2014.Upeelechien"
            ]
        )

    return 0


def purge():
    print("SUPPRESSION COMPLÈTE DE UPEELECHIEN")
    print()
    print("Cette opération peut supprimer :")
    print("- l'application Upeelechien")
    print(f"- le modèle {MODEL}")
    print("- les données locales")
    print()
    print("Ollama lui-même ne sera PAS supprimé.")
    print()

    answer = input(
        "Confirmer la suppression complète ? [o/N] : "
    ).strip().lower()

    if answer not in ("o", "oui"):
        print("Annulation.")
        return 0

    print()

    if ollama_available() and model_available(MODEL):
        subprocess.run(
            ["ollama", "rm", MODEL]
        )

    config_paths = [
        os.path.expanduser("~/.config/upeelechien"),
        os.path.expanduser("~/.local/share/upeelechien"),
        os.path.expanduser("~/.cache/upeelechien"),
    ]

    for path in config_paths:
        if os.path.exists(path):
            shutil.rmtree(
                path,
                ignore_errors=True
            )
            print(f"🗑️ Supprimé : {path}")

    if shutil.which("apt"):
        subprocess.run(
            ["sudo", "apt", "remove", "-y", "upeelechien"]
        )

    if shutil.which("flatpak"):
        subprocess.run(
            [
                "flatpak",
                "uninstall",
                "-y",
                "io.github.mdp2014.Upeelechien"
            ]
        )

    print()
    print("✅ Suppression complète terminée.")

    return 0


# ============================================================
# FENÊTRE
# ============================================================

class UpeelechienWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        super().__init__(application=app)

        self.set_title("Upeelechien")
        self.set_default_size(900, 700)

        self.main = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL
        )

        self.set_child(self.main)

        self.loading_animation = 0
        self.loading_timer = None

        self.show_loading_page()


    # ========================================================
    # CSS
    # ========================================================

    def install_css(self):

        css = Gtk.CssProvider()

        css.load_from_data(b"""
        .chat-background {
            background: #f5f5f7;
        }

        .bubble {
            padding: 10px 14px;
            border-radius: 18px;
            margin: 4px;
        }

        .user-bubble {
            background: #007aff;
            color: white;
        }

        .assistant-bubble {
            background: #ffffff;
            color: #111111;
        }

        .bubble-user-name {
            font-weight: bold;
            color: white;
        }

        .bubble-assistant-name {
            font-weight: bold;
        }

        .typing {
            padding: 10px 14px;
            border-radius: 18px;
            background: #ffffff;
        }

        .loading-title {
            font-weight: bold;
        }

        .send-button {
            padding: 8px 18px;
        }

        entry {
            border-radius: 20px;
            padding: 10px 14px;
        }
        """)

        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


    # ========================================================
    # PAGE DE CHARGEMENT
    # ========================================================

    def show_loading_page(self):

        self.install_css()

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18
        )

        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        logo = Gtk.Label(label="🐶")
        logo.set_markup(
            '<span size="65000">🐶</span>'
        )

        title = Gtk.Label(
            label="Upeelechien 5.6"
        )

        title.add_css_class("loading-title")

        title.set_markup(
            '<span size="28000" weight="bold">'
            'Upeelechien 5.6'
            '</span>'
        )

        subtitle = Gtk.Label(
            label="Préparation de votre assistant local..."
        )

        self.status_label = Gtk.Label(
            label="Initialisation..."
        )

        self.progress = Gtk.ProgressBar()
        self.progress.set_fraction(0.0)
        self.progress.set_show_text(True)
        self.progress.set_text("0 %")
        self.progress.set_size_request(420, -1)

        self.loading_detail = Gtk.Label(
            label="Veuillez patienter..."
        )

        box.append(logo)
        box.append(title)
        box.append(subtitle)
        box.append(self.status_label)
        box.append(self.progress)
        box.append(self.loading_detail)

        self.main.append(box)

        threading.Thread(
            target=self.installation_thread,
            daemon=True
        ).start()


    def update_loading(
        self,
        percent,
        status,
        detail
    ):

        def update():

            self.status_label.set_text(status)
            self.loading_detail.set_text(detail)

            self.progress.set_fraction(
                percent / 100
            )

            self.progress.set_text(
                f"{percent} %"
            )

            return False

        GLib.idle_add(update)


    # ========================================================
    # INSTALLATION
    # ========================================================

    def installation_thread(self):

        self.update_loading(
            5,
            "Vérification d'Ollama",
            "Recherche du moteur local..."
        )

        if not ollama_installed():

            self.update_loading(
                10,
                "Installation d'Ollama",
                "Une autorisation système peut être demandée..."
            )

            if not install_ollama():
                self.installation_error(
                    "Impossible d'installer Ollama."
                )
                return

        self.update_loading(
            25,
            "Démarrage d'Ollama",
            "Démarrage du serveur local..."
        )

        if not start_ollama():
            self.installation_error(
                "Impossible de démarrer Ollama."
            )
            return

        self.update_loading(
            40,
            "Vérification de Qwen3",
            f"Recherche de {QWEN_MODEL}..."
        )

        if not model_available(QWEN_MODEL):

            self.update_loading(
                50,
                "Téléchargement de Qwen3",
                f"Téléchargement de {QWEN_MODEL}..."
            )

            if not pull_qwen():
                self.installation_error(
                    "Impossible de télécharger Qwen3 1.7B."
                )
                return

        self.update_loading(
            75,
            "Création de Upeelechien",
            "Application du Modelfile..."
        )

        if not model_available(MODEL):

            if not create_upeelechien_model():
                self.installation_error(
                    "Impossible de créer le modèle Upeelechien."
                )
                return

        self.update_loading(
            95,
            "Finalisation",
            "Vérification du modèle..."
        )

        if not model_available(MODEL):
            self.installation_error(
                "Le modèle Upeelechien n'a pas été créé."
            )
            return

        self.update_loading(
            100,
            "Installation terminée",
            "Upeelechien est prêt."
        )

        time.sleep(1)

        GLib.idle_add(
            self.show_chat
        )


    def installation_error(self, message):

        def show():

            self.status_label.set_text(
                "Installation impossible"
            )

            self.loading_detail.set_text(
                message
            )

            self.progress.set_text(
                "Erreur"
            )

            return False

        GLib.idle_add(show)


    # ========================================================
    # CHAT
    # ========================================================

    def show_chat(self):

        while self.main.get_first_child():
            self.main.remove(
                self.main.get_first_child()
            )

        header = Gtk.HeaderBar()

        title = Gtk.Label(
            label="🐶 Upeelechien"
        )

        title.set_markup(
            '<b>🐶 Upeelechien</b>'
        )

        header.set_title_widget(title)

        self.main.append(header)

        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_vexpand(True)

        self.chat_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8
        )

        self.chat_box.set_margin_top(16)
        self.chat_box.set_margin_bottom(16)
        self.chat_box.set_margin_start(16)
        self.chat_box.set_margin_end(16)

        self.scrolled.set_child(
            self.chat_box
        )

        self.main.append(
            self.scrolled
        )

        bottom = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )

        bottom.set_margin_top(8)
        bottom.set_margin_bottom(8)
        bottom.set_margin_start(12)
        bottom.set_margin_end(12)

        self.entry = Gtk.Entry()

        self.entry.set_placeholder_text(
            "Écrivez votre message..."
        )

        self.entry.set_hexpand(True)

        self.entry.connect(
            "activate",
            self.send_message
        )

        send = Gtk.Button(
            label="Envoyer"
        )

        send.add_css_class(
            "send-button"
        )

        send.connect(
            "clicked",
            self.send_message
        )

        self.send_button = send

        bottom.append(self.entry)
        bottom.append(send)

        self.main.append(bottom)

        self.write_bubble(
            "Upeelechien",
            "Bonjour ! Je suis Upeelechien 5.6, "
            "une IA française développée par Marin.",
            False
        )

        self.entry.grab_focus()

        return False


    # ========================================================
    # BULLES
    # ========================================================

    def write_bubble(
        self,
        speaker,
        message,
        is_user
    ):

        row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL
        )

        if is_user:
            row.set_halign(Gtk.Align.END)
        else:
            row.set_halign(Gtk.Align.START)

        bubble = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=3
        )

        bubble.set_margin_start(8)
        bubble.set_margin_end(8)

        if is_user:
            bubble.add_css_class("bubble")
            bubble.add_css_class("user-bubble")
        else:
            bubble.add_css_class("bubble")
            bubble.add_css_class("assistant-bubble")

        name = Gtk.Label(
            label=speaker
        )

        name.set_halign(Gtk.Align.START)

        if is_user:
            name.add_css_class(
                "bubble-user-name"
            )
        else:
            name.add_css_class(
                "bubble-assistant-name"
            )

        label = Gtk.Label(
            label=message
        )

        label.set_wrap(True)
        label.set_wrap_mode(
            Gtk.WrapMode.WORD_CHAR
        )
        label.set_selectable(True)
        label.set_xalign(0)

        bubble.append(name)
        bubble.append(label)

        row.append(bubble)

        self.chat_box.append(row)

        self.scroll_to_bottom()

        return label


    # ========================================================
    # SCROLL
    # ========================================================

    def scroll_to_bottom(self):

        def scroll():

            adjustment = (
                self.scrolled
                .get_vadjustment()
            )

            adjustment.set_value(
                adjustment.get_upper()
            )

            return False

        GLib.idle_add(scroll)


    # ========================================================
    # LOADER
    # ========================================================

    def show_typing(self):

        row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL
        )

        row.set_halign(Gtk.Align.START)

        self.typing_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=3
        )

        self.typing_box.add_css_class(
            "typing"
        )

        self.typing_label = Gtk.Label(
            label="Upeelechien écrit..."
        )

        self.dots_label = Gtk.Label(
            label="●"
        )

        self.typing_box.append(
            self.typing_label
        )

        self.typing_box.append(
            self.dots_label
        )

        row.append(
            self.typing_box
        )

        self.chat_box.append(row)

        self.typing_row = row

        self.loading_animation = 0

        self.loading_timer = GLib.timeout_add(
            350,
            self.animate_typing
        )

        self.scroll_to_bottom()


    def animate_typing(self):

        if not hasattr(
            self,
            "typing_box"
        ):
            return False

        self.loading_animation += 1

        dots = (
            "●"
            * ((self.loading_animation % 3) + 1)
        )

        self.dots_label.set_text(
            dots
        )

        return True


    def hide_typing(self):

        if self.loading_timer:
            GLib.source_remove(
                self.loading_timer
            )

            self.loading_timer = None

        if hasattr(
            self,
            "typing_row"
        ):
            self.chat_box.remove(
                self.typing_row
            )

            del self.typing_row

        self.scroll_to_bottom()


    # ========================================================
    # ENVOI
    # ========================================================

    def send_message(self, widget):

        prompt = self.entry.get_text().strip()

        if not prompt:
            return

        self.entry.set_text("")

        self.entry.set_sensitive(False)
        self.send_button.set_sensitive(False)

        self.write_bubble(
            "Vous",
            prompt,
            True
        )

        self.show_typing()

        threading.Thread(
            target=self.ask_ollama,
            args=(prompt,),
            daemon=True
        ).start()


    # ========================================================
    # STREAMING OLLAMA
    # ========================================================

    def ask_ollama(self, prompt):

        payload = json.dumps({
            "model": MODEL,
            "prompt": prompt,
            "stream": True,
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
                timeout=300
            ) as response:

                first_token = True
                assistant_label = None

                for raw_line in response:

                    line = raw_line.decode(
                        "utf-8"
                    ).strip()

                    if not line:
                        continue

                    data = json.loads(line)

                    token = data.get(
                        "response",
                        ""
                    )

                    if token:

                        if first_token:

                            first_token = False

                            GLib.idle_add(
                                self.hide_typing
                            )

                            GLib.idle_add(
                                self.create_stream_bubble
                            )

                        GLib.idle_add(
                            self.append_stream_text,
                            token
                        )

                    if data.get(
                        "done",
                        False
                    ):
                        break

                GLib.idle_add(
                    self.finish_stream
                )

        except urllib.error.URLError:

            GLib.idle_add(
                self.stream_error,
                "Erreur : impossible de contacter Ollama."
            )

        except Exception as error:

            GLib.idle_add(
                self.stream_error,
                f"Erreur : {error}"
            )


    # ========================================================
    # BULLE STREAMING
    # ========================================================

    def create_stream_bubble(self):

        row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL
        )

        row.set_halign(
            Gtk.Align.START
        )

        bubble = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=3
        )

        bubble.add_css_class(
            "bubble"
        )

        bubble.add_css_class(
            "assistant-bubble"
        )

        bubble.set_margin_start(8)
        bubble.set_margin_end(8)

        name = Gtk.Label(
            label="Upeelechien"
        )

        name.set_halign(
            Gtk.Align.START
        )

        name.add_css_class(
            "bubble-assistant-name"
        )

        self.stream_label = Gtk.Label(
            label=""
        )

        self.stream_label.set_wrap(True)
        self.stream_label.set_wrap_mode(
            Gtk.WrapMode.WORD_CHAR
        )
        self.stream_label.set_selectable(True)
        self.stream_label.set_xalign(0)

        bubble.append(name)
        bubble.append(
            self.stream_label
        )

        row.append(bubble)

        self.chat_box.append(row)

        self.stream_text = ""

        self.scroll_to_bottom()

        return False


    def append_stream_text(self, token):

        if not hasattr(
            self,
            "stream_text"
        ):
            return False

        self.stream_text += token

        self.stream_label.set_text(
            self.stream_text
        )

        self.scroll_to_bottom()

        return False


    def finish_stream(self):

        self.entry.set_sensitive(True)
        self.send_button.set_sensitive(True)

        self.entry.grab_focus()

        self.scroll_to_bottom()

        return False


    def stream_error(self, message):

        self.hide_typing()

        self.write_bubble(
            "Upeelechien",
            message,
            False
        )

        self.entry.set_sensitive(True)
        self.send_button.set_sensitive(True)

        self.entry.grab_focus()

        return False


# ============================================================
# APPLICATION
# ============================================================

class UpeelechienApplication(Gtk.Application):

    def __init__(self):

        super().__init__(
            application_id="io.github.mdp2014.Upeelechien"
        )


    def do_activate(self):

        window = UpeelechienWindow(self)

        window.present()


# ============================================================
# MAIN
# ============================================================

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
