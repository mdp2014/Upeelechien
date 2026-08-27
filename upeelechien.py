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
VERSION = "3.4"

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

        self.main.add_css_class("app-background")

        self.set_child(self.main)

        self.progress_value = 0.0
        self.progress_target = 0.0
        self.progress_timer = None

        self.loading_animation_timer = None
        self.loading_phase = 0

        self.typing_timer = None
        self.typing_dots = 0

        self.response_buffer = ""
        self.current_ai_label = None

        self.install_css()
        self.show_loading_page()


    # ========================================================
    # CSS
    # ========================================================

    def install_css(self):

        css = Gtk.CssProvider()

        css.load_from_data(b"""
        .app-background {
            background: #202124;
        }

        .loading-background {
            background: #202124;
        }

        .loading-title {
            color: #ffffff;
            font-size: 28px;
            font-weight: bold;
        }

        .loading-subtitle {
            color: #d0d0d0;
            font-size: 15px;
        }

        .loading-status {
            color: #ffffff;
            font-size: 16px;
        }

        .loading-detail {
            color: #bdbdbd;
            font-size: 14px;
        }

        .loader {
            color: #22a447;
            font-size: 18px;
        }

        progressbar {
            min-height: 8px;
        }

        progressbar trough {
            background: #3a3a3a;
            border-radius: 8px;
        }

        progressbar progress {
            background: #22a447;
            border-radius: 8px;
        }

        .chat-background {
            background: #202124;
        }

        .messages-area {
            background: #202124;
            padding: 14px;
        }

        .bubble {
            padding: 10px 14px;
            border-radius: 18px;
            margin: 4px;
        }

        .user-bubble {
            background: #087cf5;
            color: #ffffff;
        }

        .assistant-bubble {
            background: #22a447;
            color: #ffffff;
        }

        .bubble-name {
            font-weight: bold;
            color: #ffffff;
        }

        .message-text {
            color: #ffffff;
        }

        .typing-bubble {
            background: #22a447;
            color: #ffffff;
            padding: 10px 14px;
            border-radius: 18px;
            margin: 4px;
        }

        .typing-text {
            color: #ffffff;
        }

        .input-area {
            background: #202124;
            padding: 8px;
        }

        entry {
            background: #292a2d;
            color: #ffffff;
            border-radius: 20px;
            padding: 10px 14px;
            border: 1px solid #444444;
        }

        entry:focus {
            border: 1px solid #22a447;
        }

        .send-button {
            padding: 10px 20px;
            border-radius: 18px;
        }
        """)

        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


    # ========================================================
    # PAGE INSTALLATION
    # ========================================================

    def show_loading_page(self):

        while self.main.get_first_child():
            self.main.remove(
                self.main.get_first_child()
            )

        page = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=16
        )

        page.add_css_class("loading-background")

        page.set_halign(Gtk.Align.FILL)
        page.set_valign(Gtk.Align.FILL)
        page.set_vexpand(True)

        center = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=14
        )

        center.set_halign(Gtk.Align.CENTER)
        center.set_valign(Gtk.Align.CENTER)

        logo = Gtk.Label(label="🐶")
        logo.set_markup(
            '<span size="70000">🐶</span>'
        )

        title = Gtk.Label(
            label="Upeelechien 5.6"
        )
        title.add_css_class("loading-title")

        subtitle = Gtk.Label(
            label="Préparation de votre assistant local..."
        )
        subtitle.add_css_class("loading-subtitle")

        self.status_label = Gtk.Label(
            label="Initialisation..."
        )
        self.status_label.add_css_class("loading-status")

        self.loading_spinner = Gtk.Spinner()
        self.loading_spinner.add_css_class("loader")
        self.loading_spinner.set_spinning(True)

        self.loading_animation_label = Gtk.Label(
            label="●"
        )
        self.loading_animation_label.add_css_class("loader")

        self.progress = Gtk.ProgressBar()
        self.progress.set_fraction(0.0)
        self.progress.set_show_text(True)
        self.progress.set_text("0 %")
        self.progress.set_size_request(420, -1)

        self.loading_detail = Gtk.Label(
            label="Cette opération peut prendre plusieurs minutes."
        )
        self.loading_detail.add_css_class("loading-detail")
        self.loading_detail.set_wrap(True)
        self.loading_detail.set_justify(
            Gtk.Justification.CENTER
        )

        center.append(logo)
        center.append(title)
        center.append(subtitle)
        center.append(self.loading_spinner)
        center.append(self.loading_animation_label)
        center.append(self.status_label)
        center.append(self.progress)
        center.append(self.loading_detail)

        page.append(center)

        self.main.append(page)

        self.start_loading_animation()

        threading.Thread(
            target=self.installation_thread,
            daemon=True
        ).start()


    def start_loading_animation(self):

        self.loading_phase = 0

        if self.loading_animation_timer:
            GLib.source_remove(
                self.loading_animation_timer
            )

        self.loading_animation_timer = GLib.timeout_add(
            350,
            self.animate_loading
        )


    def animate_loading(self):

        if not hasattr(
            self,
            "loading_animation_label"
        ):
            return False

        self.loading_phase = (
            self.loading_phase + 1
        ) % 4

        dots = "." * self.loading_phase

        self.loading_animation_label.set_text(
            f"●{dots}"
        )

        return True


    # ========================================================
    # PROGRESSION FLUIDE
    # ========================================================

    def update_loading(
        self,
        percent,
        status,
        detail
    ):

        def update():

            self.progress_target = float(percent)

            self.status_label.set_text(
                status
            )

            self.loading_detail.set_text(
                detail
            )

            if self.progress_timer is None:

                self.progress_timer = GLib.timeout_add(
                    25,
                    self.animate_progress
                )

            return False

        GLib.idle_add(update)


    def animate_progress(self):

        difference = (
            self.progress_target
            - self.progress_value
        )

        if abs(difference) < 0.15:

            self.progress_value = (
                self.progress_target
            )

            self.progress.set_fraction(
                self.progress_value / 100
            )

            self.progress.set_text(
                f"{int(self.progress_value)} %"
            )

            self.progress_timer = None

            return False

        self.progress_value += (
            difference * 0.08
        )

        self.progress.set_fraction(
            self.progress_value / 100
        )

        self.progress.set_text(
            f"{int(self.progress_value)} %"
        )

        return True


    # ========================================================
    # INSTALLATION
    # ========================================================

    def installation_thread(self):

        self.update_loading(
            5,
            "Vérification d'Ollama",
            "Recherche du moteur local..."
        )

        time.sleep(1)

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
            28,
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
            "Vérification de Qwen",
            f"Recherche de {QWEN_MODEL}..."
        )

        time.sleep(1)

        if not model_available(QWEN_MODEL):

            self.update_loading(
                55,
                "Téléchargement de Qwen",
                f"Téléchargement de {QWEN_MODEL}..."
            )

            if not pull_qwen():

                self.installation_error(
                    "Impossible de télécharger Qwen 1.7B."
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

            self.status_label.set_text(
                "Installation impossible"
            )

            self.loading_detail.set_text(
                message
            )

            self.progress.set_text(
                "Erreur"
            )

            if self.loading_spinner:
                self.loading_spinner.set_spinning(False)

            return False

        GLib.idle_add(show)


    # ========================================================
    # CHAT
    # ========================================================

    def show_chat(self):

        if self.loading_animation_timer:
            GLib.source_remove(
                self.loading_animation_timer
            )

            self.loading_animation_timer = None

        while self.main.get_first_child():
            self.main.remove(
                self.main.get_first_child()
            )

        page = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL
        )

        page.add_css_class("chat-background")

        header = Gtk.HeaderBar()

        title = Gtk.Label(
            label="🐶 Upeelechien"
        )

        header.set_title_widget(title)

        page.append(header)

        self.messages_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6
        )

        self.messages_box.add_css_class(
            "messages-area"
        )

        self.messages_box.set_vexpand(True)

        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_vexpand(True)
        self.scrolled.set_hexpand(True)
        self.scrolled.set_child(
            self.messages_box
        )

        page.append(self.scrolled)

        bottom = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )

        bottom.add_css_class(
            "input-area"
        )

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

        page.append(bottom)

        self.main.append(page)

        self.write_chat(
            "Upeelechien",
            "Bonjour ! Je suis Upeelechien 5.6, "
            "une IA française développée par Marin."
        )

        return False


    # ========================================================
    # BULLES
    # ========================================================

    def write_chat(
        self,
        speaker,
        message
    ):

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
        bubble.set_margin_start(4)
        bubble.set_margin_end(4)

        bubble.set_halign(
            Gtk.Align.START
            if speaker != "Vous"
            else Gtk.Align.END
        )

        name = Gtk.Label(
            label=speaker,
            xalign=0
        )

        name.add_css_class(
            "bubble-name"
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

        text.set_max_width_chars(70)

        text.add_css_class(
            "message-text"
        )

        bubble.append(name)
        bubble.append(text)

        if speaker == "Vous":

            bubble.add_css_class(
                "user-bubble"
            )

            row.set_halign(
                Gtk.Align.END
            )

        else:

            bubble.add_css_class(
                "assistant-bubble"
            )

            row.set_halign(
                Gtk.Align.START
            )

        row.append(bubble)

        self.messages_box.append(
            row
        )

        self.scroll_to_bottom()


    # ========================================================
    # SCROLL
    # ========================================================

    def scroll_to_bottom(self):

        def scroll():

            if not hasattr(
                self,
                "scrolled"
            ):
                return False

            adjustment = (
                self.scrolled
                .get_vadjustment()
            )

            adjustment.set_value(
                max(
                    0,
                    adjustment.get_upper()
                    - adjustment.get_page_size()
                )
            )

            return False

        GLib.idle_add(scroll)


    # ========================================================
    # INDICATEUR DE GENERATION
    # ========================================================

    def show_typing(self):

        if hasattr(
            self,
            "typing_row"
        ):
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
            label="Upeelechien écrit..."
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

        if not hasattr(
            self,
            "typing_label"
        ):
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

        if self.typing_timer:

            GLib.source_remove(
                self.typing_timer
            )

            self.typing_timer = None

        if hasattr(
            self,
            "typing_row"
        ):

            self.messages_box.remove(
                self.typing_row
            )

            del self.typing_row

        if hasattr(
            self,
            "typing_label"
        ):

            del self.typing_label


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

        self.response_buffer = ""
        self.current_ai_label = None

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

                first_chunk = True

                for raw_line in response:

                    if not raw_line:
                        continue

                    try:
                        data = json.loads(
                            raw_line.decode().strip()
                        )
                    except Exception:
                        continue

                    chunk = data.get(
                        "response",
                        ""
                    )

                    if chunk:

                        if first_chunk:

                            first_chunk = False

                            GLib.idle_add(
                                self.begin_streaming_response
                            )

                        GLib.idle_add(
                            self.append_stream_chunk,
                            chunk
                        )

                    if data.get(
                        "done",
                        False
                    ):
                        break

                GLib.idle_add(
                    self.finish_streaming_response
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
    # PREMIER MORCEAU
    # ========================================================

    def begin_streaming_response(self):

        self.hide_typing()

        self.current_ai_label = Gtk.Label(
            label="",
            xalign=0
        )

        self.current_ai_label.set_wrap(True)

        self.current_ai_label.set_wrap_mode(
            Gtk.WrapMode.WORD_CHAR
        )

        self.current_ai_label.set_selectable(True)

        self.current_ai_label.set_max_width_chars(
            70
        )

        self.current_ai_label.add_css_class(
            "message-text"
        )

        bubble = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=3
        )

        bubble.set_margin_top(4)
        bubble.set_margin_bottom(4)
        bubble.set_margin_start(4)
        bubble.set_margin_end(4)

        bubble.add_css_class(
            "assistant-bubble"
        )

        name = Gtk.Label(
            label="Upeelechien",
            xalign=0
        )

        name.add_css_class(
            "bubble-name"
        )

        bubble.append(name)

        bubble.append(
            self.current_ai_label
        )

        row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL
        )

        row.set_halign(
            Gtk.Align.START
        )

        row.append(
            bubble
        )

        self.messages_box.append(
            row
        )

        self.current_ai_bubble = row

        self.scroll_to_bottom()

        return False


    # ========================================================
    # AFFICHAGE PROGRESSIF
    # ========================================================

    def append_stream_chunk(self, chunk):

        if not self.current_ai_label:
            return False

        self.response_buffer += chunk

        self.current_ai_label.set_text(
            self.response_buffer
        )

        self.scroll_to_bottom()

        return False


    # ========================================================
    # FIN STREAMING
    # ========================================================

    def finish_streaming_response(self):

        self.hide_typing()

        if (
            self.current_ai_label
            and not self.response_buffer
        ):

            self.current_ai_label.set_text(
                "Aucune réponse."
            )

        self.current_ai_label = None
        self.current_ai_bubble = None

        self.scroll_to_bottom()

        return False


    def stream_error(self, message):

        self.hide_typing()

        self.write_chat(
            "Upeelechien",
            message
        )

        self.current_ai_label = None
        self.current_ai_bubble = None

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

        window = UpeelechienWindow(
            self
        )

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
