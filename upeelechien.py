#!/usr/bin/env python3

import json
import threading
import urllib.request
import urllib.error

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib


OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "upeelechien-2"


class UpeelechienWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        super().__init__(application=app)

        self.set_title("Upeelechien")
        self.set_default_size(900, 650)

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(main)

        # Barre supérieure
        header = Gtk.HeaderBar()

        title = Gtk.Label(label="🐶 Upeelechien")
        title.add_css_class("title")
        header.set_title_widget(title)

        clear_button = Gtk.Button(label="Effacer")
        clear_button.connect("clicked", self.clear_chat)
        header.pack_end(clear_button)

        main.append(header)

        # Zone de conversation
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)

        self.chat = Gtk.TextView()
        self.chat.set_editable(False)
        self.chat.set_cursor_visible(False)
        self.chat.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.chat.set_margin_top(20)
        self.chat.set_margin_bottom(20)
        self.chat.set_margin_start(20)
        self.chat.set_margin_end(20)

        scrolled.set_child(self.chat)
        main.append(scrolled)

        # Zone de saisie
        bottom = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8
        )
        bottom.set_margin_top(10)
        bottom.set_margin_bottom(10)
        bottom.set_margin_start(10)
        bottom.set_margin_end(10)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Écrivez votre message…")
        self.entry.set_hexpand(True)
        self.entry.connect("activate", self.send_message)

        send_button = Gtk.Button(label="Envoyer")
        send_button.add_css_class("suggested-action")
        send_button.connect("clicked", self.send_message)

        bottom.append(self.entry)
        bottom.append(send_button)

        main.append(bottom)

        self.status = Gtk.Label(label="Prêt")
        self.status.set_margin_bottom(8)
        main.append(self.status)

        self.append_message(
            "Upeelechien",
            "Bonjour ! Je suis Upeelechien 5.6. Comment puis-je vous aider ?"
        )

    def append_message(self, author, message):
        buffer = self.chat.get_buffer()

        end = buffer.get_end_iter()

        if buffer.get_char_count() > 0:
            buffer.insert(end, "\n\n", -1)

        buffer.insert(end, f"{author} :\n", -1)
        buffer.insert(end, message, -1)

        GLib.idle_add(self.scroll_to_bottom)

    def scroll_to_bottom(self):
        adjustment = self.chat.get_parent().get_vadjustment()
        adjustment.set_value(adjustment.get_upper())
        return False

    def clear_chat(self, button):
        self.chat.get_buffer().set_text("")
        self.append_message(
            "Upeelechien",
            "Conversation effacée. Comment puis-je vous aider ?"
        )

    def send_message(self, widget):
        prompt = self.entry.get_text().strip()

        if not prompt:
            return

        self.entry.set_text("")
        self.append_message("Vous", prompt)

        self.status.set_text("Upeelechien réfléchit…")

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
                f"{OLLAMA_URL}/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(request, timeout=300) as response:
                data = json.loads(response.read().decode("utf-8"))

            answer = data.get("response", "").strip()

            if not answer:
                answer = "Je n'ai reçu aucune réponse d'Ollama."

            GLib.idle_add(self.show_answer, answer)

        except urllib.error.URLError:
            GLib.idle_add(
                self.show_error,
                "Impossible de contacter Ollama."
            )

        except Exception as error:
            GLib.idle_add(
                self.show_error,
                f"Erreur : {error}"
            )

    def show_answer(self, answer):
        self.append_message("Upeelechien", answer)
        self.status.set_text("Prêt")
        return False

    def show_error(self, error):
        self.append_message("Erreur", error)
        self.status.set_text("Erreur")
        return False


class UpeelechienApp(Gtk.Application):

    def __init__(self):
        super().__init__(
            application_id="io.github.mdp2014.Upeelechien"
        )

    def do_activate(self):
        window = self.props.active_window

        if not window:
            window = UpeelechienWindow(self)

        window.present()


app = UpeelechienApp()
app.run()
