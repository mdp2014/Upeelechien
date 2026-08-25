import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib
import json
import threading
import urllib.request
import urllib.error


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "upeelechien-2"


class UpeelechienWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        super().__init__(application=app)

        self.set_title("Upeelechien")
        self.set_default_size(900, 650)
        self.set_size_request(600, 500)

        self.build_ui()

    def build_ui(self):
        main = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0
        )

        self.set_child(main)

        # Barre supérieure
        header = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12
        )
        header.set_margin_top(12)
        header.set_margin_bottom(12)
        header.set_margin_start(18)
        header.set_margin_end(18)

        title = Gtk.Label()
        title.set_markup(
            '<span size="x-large" weight="bold">🐶 Upeelechien</span>'
        )

        subtitle = Gtk.Label(label="IA française locale")
        subtitle.add_css_class("dim-label")

        title_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2
        )
        title_box.append(title)
        title_box.append(subtitle)

        header.append(title_box)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        header.append(spacer)

        status = Gtk.Label(label="● Connecté")
        status.add_css_class("success")
        header.append(status)

        main.append(header)

        separator = Gtk.Separator()
        main.append(separator)

        # Zone de conversation
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_vexpand(True)
        self.scrolled.set_hexpand(True)

        self.messages = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12
        )

        self.messages.set_margin_top(20)
        self.messages.set_margin_bottom(20)
        self.messages.set_margin_start(20)
        self.messages.set_margin_end(20)

        self.scrolled.set_child(self.messages)
        main.append(self.scrolled)

        # Message d'accueil
        self.add_message(
            "Upeelechien",
            "Bonjour ! Je suis Upeelechien 5.6, "
            "une IA française locale. Comment puis-je vous aider ?",
            False
        )

        # Zone de saisie
        bottom = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10
        )

        bottom.set_margin_top(12)
        bottom.set_margin_bottom(16)
        bottom.set_margin_start(18)
        bottom.set_margin_end(18)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text(
            "Écrivez votre message..."
        )
        self.entry.set_hexpand(True)

        self.entry.connect("activate", self.send_message)

        send = Gtk.Button(label="Envoyer")
        send.add_css_class("suggested-action")
        send.connect("clicked", self.send_message)

        bottom.append(self.entry)
        bottom.append(send)

        main.append(bottom)

    def add_message(self, author, text, user):
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=5
        )

        label = Gtk.Label()
        label.set_halign(
            Gtk.Align.END if user else Gtk.Align.START
        )

        label.set_markup(
            f"<b>{GLib.markup_escape_text(author)}</b>"
        )

        message = Gtk.Label(
            label=GLib.markup_escape_text(text)
        )

        message.set_wrap(True)
        message.set_xalign(0)
        message.set_selectable(True)

        box.append(label)
        box.append(message)

        if user:
            box.add_css_class("user-message")
        else:
            box.add_css_class("assistant-message")

        self.messages.append(box)

        GLib.idle_add(self.scroll_bottom)

    def scroll_bottom(self):
        adjustment = self.scrolled.get_vadjustment()
        adjustment.set_value(adjustment.get_upper())
        return False

    def send_message(self, widget):
        prompt = self.entry.get_text().strip()

        if not prompt:
            return

        self.entry.set_text("")

        self.add_message(
            "Vous",
            prompt,
            True
        )

        self.add_message(
            "Upeelechien",
            "Réflexion en cours...",
            False
        )

        thread = threading.Thread(
            target=self.ask_ollama,
            args=(prompt,),
            daemon=True
        )

        thread.start()

    def ask_ollama(self, prompt):
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "think": False
        }

        try:
            request = urllib.request.Request(
                OLLAMA_URL,
                data=json.dumps(payload).encode(),
                headers={
                    "Content-Type": "application/json"
                }
            )

            with urllib.request.urlopen(
                request,
                timeout=300
            ) as response:

                data = json.load(response)
                answer = data.get(
                    "response",
                    "Aucune réponse."
                )

        except urllib.error.URLError:
            answer = (
                "❌ Impossible de contacter Ollama.\n\n"
                "Vérifiez que le service Ollama fonctionne."
            )

        except Exception as error:
            answer = f"❌ Erreur : {error}"

        GLib.idle_add(
            self.replace_last_message,
            answer
        )

    def replace_last_message(self, text):
        child = self.messages.get_last_child()

        if child:
            message = child.get_last_child()

            if message:
                message.set_text(text)

        return False


class UpeelechienApp(Gtk.Application):

    def __init__(self):
        super().__init__(
            application_id="io.github.mdp2014.Upeelechien"
        )

    def do_activate(self):
        window = UpeelechienWindow(self)
        window.present()


app = UpeelechienApp()
app.run()
