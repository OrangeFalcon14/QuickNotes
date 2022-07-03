import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import gui

TITLE = "QuickNotes"
WIDTH = 400
HEIGHT = 400


def main():
    window = gui.Window(TITLE, WIDTH, HEIGHT)
    window.connect("destroy", Gtk.main_quit)

    Gtk.main()


main()
