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

    answer = input(
        "Confirmer la suppression complète ? [o/N] : "
    ).strip().lower()

    if answer not in ("o", "oui"):
        print("Annulation.")
        return 0

    if ollama_available() and model_available(MODEL):
        subprocess.run(["ollama", "rm", MODEL])

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

        self.loading_value = 0
        self.loading_target = 0
        self.loading_timer = None

        self.typing_timer = None
        self.typing_row = None
        self.typing_label = None
        self.typing_dots = 0

        self.install_css()
        self.show_loading_page()


    # ========================================================
    # CSS
    # ========================================================

    def install_css(self):

        css = Gtk.CssProvider()

        css.load_from_data(b"""
        .loading-page {
            background: #202124;
        }

        .loading-title {
            color: #ffffff;
            font-weight: bold;
        }

        .loading-subtitle {
            color: #dddddd;
        }

        .loading-status {
            color: #ffffff;
            font-weight: bold;
        }

        .loading-detail {
            color: #bbbbbb;
        }

        .chat-area {
            background: #f5f5f7;
            padding: 12px;
        }

        .bubble {
            padding: 10px 14px;
            border-radius: 18px;
            margin: 4px;
        }

        .user-bubble {
            background: #007aff;
            color: #ffffff;
        }

        .assistant-bubble {
            background: #22a447;
            color: #ffffff;
        }

        .bubble-user-name {
            color: #ffffff;
            font-weight: bold;
        }

        .bubble-assistant-name {
            color: #ffffff;
            font-weight: bold;
        }

        .message-text {
            color: #ffffff;
        }

        .typing-bubble {
            background: #22a447;
            color: #ffffff;
            padding: 10px 14px;
            border-radius: 18px;
        }

        .typing-text {
            color: #ffffff;
        }

        .send-button {
            padding: 8px 18px;
            border-radius: 14px;
        }

        entry {
            border-radius: 20px;
            padding: 10px 14px;
        }
        """)

        display = self.get_display()

        if display is not None:
            Gtk.StyleContext.add_provider_for_display(
                display,
                css,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )


    # ========================================================
    # PAGE DE CHARGEMENT
    # ========================================================

    def show_loading_page(self):

        while self.main.get_first_child():
            self.main.remove(
                self.main.get_first_child()
            )

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18
        )

        box.add_css_class("loading-page")
        box.set_halign(Gtk.Align.FILL)
        box.set_valign(Gtk.Align.FILL)
        box.set_hexpand(True)
        box.set_vexpand(True)

        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18
        )

        content.set_halign(Gtk.Align.CENTER)
        content.set_valign(Gtk.Align.CENTER)

        logo = Gtk.Label(label="🐶")
        logo.set_markup(
            '<span size="60000">🐶</span>'
        )

        title = Gtk.Label(
            label="Upeelechien 5.6"
        )
        title.add_css_class("loading-title")
        title.set_markup(
            '<span size="26000" weight="bold">'
            'Upeelechien 5.6'
            '</span>'
        )

        subtitle = Gtk.Label(
            label="Préparation de votre assistant local..."
        )
        subtitle.add_css_class("loading-subtitle")

        self.status_label = Gtk.Label(
            label="Initialisation..."
        )
        self.status_label.add_css_class(
            "loading-status"
        )

        self.progress = Gtk.ProgressBar()
        self.progress.set_fraction(0.0)
        self.progress.set_show_text(True)
        self.progress.set_text("0 %")
        self.progress.set_size_request(450, -1)

        self.loading_detail = Gtk.Label(
            label="Cette opération peut prendre plusieurs minutes."
        )
        self.loading_detail.add_css_class(
            "loading-detail"
        )
        self.loading_detail.set_wrap(True)
        self.loading_detail.set_justify(
            Gtk.Justification.CENTER
        )

        content.append(logo)
        content.append(title)
        content.append(subtitle)
        content.append(self.status_label)
        content.append(self.progress)
        content.append(self.loading_detail)

        box.append(content)

        self.main.append(box)

        self.loading_value = 0
        self.loading_target = 0

        self.loading_timer = GLib.timeout_add(
            30,
            self.animate_loading
        )

        threading.Thread(
            target=self.installation_thread,
            daemon=True
        ).start()


    def animate_loading(self):

        if not hasattr(self, "progress"):
            return False

        if self.loading_value < self.loading_target:
            self.loading_value += 0.35

            if self.loading_value > self.loading_target:
                self.loading_value = self.loading_target

            self.progress.set_fraction(
                self.loading_value / 100
            )

            self.progress.set_text(
                f"{int(self.loading_value)} %"
            )

        return True


    def update_loading(
        self,
        percent,
        status,
        detail
    ):

        def update():

            self.loading_target = percent

            self.status_label.set_text(
                status
            )

            self.loading_detail.set_text(
                detail
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

        time.sleep(0.5)

        if not ollama_installed():

            self.update_loading(
                15,
                "Installation d'Ollama",
                "Installation du moteur local..."
            )

            if not install_ollama():
                self.installation_error(
                    "Impossible d'installer Ollama."
                )
                return

        self.update_loading(
            30,
            "Démarrage d'Ollama",
            "Démarrage du serveur local..."
        )

        if not start_ollama():
            self.installation_error(
                "Impossible de démarrer Ollama."
            )
            return

        self.update_loading(
            42,
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
            78,
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
            94,
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

            self.loading_target = self.loading_value

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

        if self.loading_timer is not None:
            GLib.source_remove(
                self.loading_timer
            )
            self.loading_timer = None

        while self.main.get_first_child():
            self.main.remove(
                self.main.get_first_child()
            )

        header = Gtk.HeaderBar()

        title = Gtk.Label(
            label="🐶 Upeelechien"
        )

        header.set_title_widget(title)

        self.main.append(header)

        self.messages_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8
        )

        self.messages_box.set_vexpand(True)
        self.messages_box.set_valign(
            Gtk.Align.START
        )

        self.messages_box.add_css_class(
            "chat-area"
        )

        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_vexpand(True)
        self.scrolled.set_hexpand(True)
        self.scrolled.set_child(
            self.messages_box
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
        bottom.set_margin_start(8)
        bottom.set_margin_end(8)

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

        bottom.append(self.entry)
        bottom.append(send)

        self.main.append(bottom)

        self.write_chat(
            "Upeelechien",
            "Bonjour ! Je suis Upeelechien 5.6, "
            "une IA française développée par Marin."
        )

        self.scroll_to_bottom()

        return False


    def scroll_to_bottom(self):

        def scroll():

            if not hasattr(self, "scrolled"):
                return False

            adjustment = (
                self.scrolled.get_vadjustment()
            )

            adjustment.set_value(
                adjustment.get_upper()
                - adjustment.get_page_size()
            )

            return False

        GLib.idle_add(scroll)


    def write_chat(
        self,
        speaker,
        message
    ):

        if not hasattr(
            self,
            "messages_box"
        ):
            return

        row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL
        )

        row.set_hexpand(True)

        bubble = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=3
        )

        bubble.set_margin_top(4)
        bubble.set_margin_bottom(4)
        bubble.set_margin_start(8)
        bubble.set_margin_end(8)

        bubble.add_css_class(
            "bubble"
        )

        name = Gtk.Label(
            label=speaker,
            xalign=0
        )

        text = Gtk.Label(
            label=message,
            xalign=0
        )

        text.set_wrap(True)
        text.set_wrap_mode(
            Gtk.WrapMode.WORD_CHAR
        )
        text.set_selectable(True)
        text.set_max_width_chars(65)

        if speaker == "Vous":

            bubble.add_css_class(
                "user-bubble"
            )

            name.add_css_class(
                "bubble-user-name"
            )

            text.add_css_class(
                "message-text"
            )

            row.set_halign(
                Gtk.Align.END
            )

        else:

            bubble.add_css_class(
                "assistant-bubble"
            )

            name.add_css_class(
                "bubble-assistant-name"
            )

            text.add_css_class(
                "message-text"
            )

            row.set_halign(
                Gtk.Align.START
            )

        bubble.append(name)
        bubble.append(text)

        row.append(bubble)

        self.messages_box.append(row)

        self.scroll_to_bottom()


    # ========================================================
    # ANIMATION "L'IA ÉCRIT"
    # ========================================================

    def show_typing(self):

        if self.typing_row is not None:
            return

        self.typing_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL
        )

        self.typing_row.set_halign(
            Gtk.Align.START
        )

        bubble = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL
        )

        bubble.add_css_class(
            "typing-bubble"
        )

        self.typing_label = Gtk.Label(
            label="Upeelechien écrit"
        )

        self.typing_label.add_css_class(
            "typing-text"
        )

        bubble.append(
            self.typing_label
        )

        self.typing_row.append(
            bubble
        )

        self.messages_box.append(
            self.typing_row
        )

        self.typing_dots = 0

        self.typing_timer = GLib.timeout_add(
            350,
            self.animate_typing
        )

        self.scroll_to_bottom()


    def animate_typing(self):

        if self.typing_label is None:
            return False

        self.typing_dots = (
            self.typing_dots + 1
        ) % 4

        dots = "." * self.typing_dots

        self.typing_label.set_text(
            "Upeelechien écrit" + dots
        )

        return True


    def hide_typing(self):

        if self.typing_timer is not None:

            GLib.source_remove(
                self.typing_timer
            )

            self.typing_timer = None

        if self.typing_row is not None:

            self.messages_box.remove(
                self.typing_row
            )

            self.typing_row = None

        self.typing_label = None


    # ========================================================
    # ENVOI
    # ========================================================

    def send_message(self, widget):

        prompt = self.entry.get_text().strip()

        if not prompt:
            return

        self.entry.set_text("")

        self.write_chat(
            "Vous",
            prompt
        )

        self.show_typing()

        threading.Thread(
            target=self.ask_ollama,
            args=(prompt,),
            daemon=True
        ).start()


    # ========================================================
    # OLLAMA GENERATE
    # ========================================================

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

            answer = (
                "Erreur : impossible de contacter Ollama."
            )

        except Exception as error:

            answer = f"Erreur : {error}"

        GLib.idle_add(
            self.finish_response,
            answer
        )


    def finish_response(self, answer):

        self.hide_typing()

        self.write_chat(
            "Upeelechien",
            answer
        )

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
