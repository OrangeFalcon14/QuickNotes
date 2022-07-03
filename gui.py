import db
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Pango, Gdk, GLib


class Note:
    def __init__(self, note, index, new_note):
        self.index = index
        self.new_note = new_note
        title = note[2]
        if len(title) > 25:
            title = title[:20] + "..."
        label_text = "<span size='20000'>" + str(
            title) + "</span>" + "\n\n\t" + " " + "<span size='12000'>" + str(note[1]) + " " + str(
            note[0]) + "</span>"
        self.note_label = Gtk.Label(label=label_text, use_markup=True, hexpand=False)
        self.note_label.props.halign = 1

        self.note_btn = Gtk.Button()

        self.notes = db.get_notes()
        self.note = note

    def get_note_btn(self):
        self.note_btn.add(self.note_label)
        self.note_btn.connect("clicked", lambda dummy: self.new_note("", self.index))
        self.note_btn.set_hexpand(True)
        return self.note_btn


class Window(Gtk.Window):
    def __init__(self, title, width, height):
        Gtk.Window.__init__(self, title=title)
        GLib.set_application_name("QuickNotes")
        self.set_default_size(width, height)
        self.set_border_width(10)
        window_icon = self.render_icon("quicknotes_icon.png", Gtk.IconSize.MENU)
        self.set_icon(window_icon)
        self.connect("key-press-event", self.key_press)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.add(self.scrolled_window)

        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.props.title = "QuickNotes"
        self.set_titlebar(headerbar)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.scrolled_window.add(self.vbox)
        self.notes = db.get_notes()

        new_btn = Gtk.Button()
        icon = Gio.ThemedIcon(name="list-add")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        new_btn.add(image)
        new_btn.connect("clicked", self.new_note)
        headerbar.add(new_btn)

        db.write_new_note_numbers()
        print(self.notes)
        self.set_up_notes_widgets(True)
        self.show_all()

    def key_press(self, window, event):
        key_name = Gdk.keyval_name(event.keyval)
        if not Gdk.ModifierType.CONTROL_MASK:
            return
        if (Gdk.ModifierType.CONTROL_MASK and event.state) and key_name == "n":
            self.new_note("")

    def set_up_notes_widgets(self, first_run: bool):
        self.notes = db.get_notes()
        if not first_run:
            for widget in self.vbox.get_children():
                self.vbox.remove(widget)

        if len(self.notes) == 0:
            label_text = "\n\n\n\n<span size='15000'>" + "You have no notes" + "</span>"
            label = Gtk.Label(label=label_text, valign=0, use_markup=True)
            label.set_vexpand = True
            label.set_hexpand = True
            label.props.halign = 0
            label.props.valign = 2
            self.vbox.add(label)
            label2 = Gtk.Label(label="\nClick the button on the top left or", valign=0)
            label2.set_vexpand = True
            label2.set_hexpand = True
            label2.props.halign = 0
            label2.props.valign = 2
            self.vbox.add(label2)
            label3 = Gtk.Label(label="press CTRL + N to add one (does not work yet)", valign=0)
            label3.set_vexpand = True
            label3.set_hexpand = True
            label3.props.halign = 0
            label2.props.valign = 2
            self.vbox.add(label3)
            self.show_all()

        for x in enumerate(self.notes):
            note = x[1]
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            hbox.set_hexpand(False)

            note_btn_obj = Note(note, x[0], self.new_note)
            note_btn = note_btn_obj.get_note_btn()
            hbox.add(note_btn)

            delete_btn = Gtk.Button()
            delete_btn.props.halign = 0
            icon = Gio.ThemedIcon(name="user-trash-symbolic")
            image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
            delete_btn.add(image)
            delete_btn.connect("clicked", self.delete_note, note_btn_obj.index)
            hbox.add(delete_btn)

            self.vbox.add(hbox)
            self.show_all()

    def delete_note(self, dummy, index):
        self.notes = db.get_notes()
        db.delete_record(index + 1)
        db.write_new_note_numbers()
        self.set_up_notes_widgets(False)

    def new_note(self, dummy, i=None):
        def note_exit(dummy, edit: bool, window):
            # save the note:
            if not edit:
                buffer = title_entry.get_buffer()
                title = buffer.get_text()
                buffer = note_text_entry.get_buffer()
                note_text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
                try:
                    db.write_new_note(title, note_text)
                    db.write_new_note_numbers()
                except Exception as e:
                    dialog = Gtk.MessageDialog(text=str(e), buttons=Gtk.ButtonsType.OK,
                                               message_type=Gtk.MessageType.ERROR)
                    dialog.run()
                    dialog.set_transient_for(window)
                    dialog.destroy()
                    dialog.set_destroy_with_parent(True)
            else:
                buffer = title_entry.get_buffer()
                title = buffer.get_text()
                buffer = note_text_entry.get_buffer()
                note_text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
                try:
                    db.update_db(self.notes[i], title, note_text)
                    db.write_new_note_numbers()
                except Exception as e:
                    dialog = Gtk.MessageDialog(text=str(e), buttons=Gtk.ButtonsType.OK,
                                               message_type=Gtk.MessageType.ERROR)
                    dialog.run()
                    dialog.set_transient_for(window)
                    dialog.destroy()
                    dialog.set_destroy_with_parent(True)
            window.destroy()
            self.set_up_notes_widgets(False)

        def on_button_clicked(widget, tag, buffer):
            bounds = buffer.get_selection_bounds()
            if len(bounds) != 0:
                start, end = bounds
                buffer.apply_tag(tag, start, end)

        if i is None:
            window = Gtk.Window(title="QuickNotes - New Note")
            window.connect("key-press-event", self.key_press)
            window.set_border_width(5)
            window.set_default_size(500, 300)

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            window.add(vbox)

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_hexpand(True)
            scrolled_window.set_vexpand(False)
            vbox.add(scrolled_window)

            title_entry = Gtk.Entry(placeholder_text="Title")
            title_entry.modify_font(Pango.FontDescription('Ubuntu 17'))
            title_entry.set_margin_bottom(10)
            scrolled_window.add(title_entry)

            toolbar = Gtk.Toolbar()
            vbox.add(toolbar)

            scrolled_window_2 = Gtk.ScrolledWindow()
            scrolled_window_2.set_hexpand(True)
            scrolled_window_2.set_vexpand(True)
            vbox.add(scrolled_window_2)

            note_text_entry = Gtk.TextView()

            note_text_entry.set_left_margin(5)
            note_text_entry.set_right_margin(5)
            note_text_entry.set_top_margin(5)
            note_text_entry.set_bottom_margin(5)
            note_text_entry.set_vexpand(True)
            note_text_entry.modify_font(Pango.FontDescription('Ubuntu 14'))
            scrolled_window_2.add(note_text_entry)

            note_text_entry_buffer = note_text_entry.get_buffer()

            tag_bold = note_text_entry_buffer.create_tag("bold", weight=Pango.Weight.BOLD)
            tag_italic = note_text_entry_buffer.create_tag("italic", style=Pango.Style.ITALIC)
            tag_underline = note_text_entry_buffer.create_tag(
                "underline", underline=Pango.Underline.SINGLE
            )

            button_bold = Gtk.ToolButton()
            button_bold.set_icon_name("format-text-bold-symbolic")
            toolbar.insert(button_bold, 0)

            button_italic = Gtk.ToolButton()
            button_italic.set_icon_name("format-text-italic-symbolic")
            toolbar.insert(button_italic, 1)

            button_underline = Gtk.ToolButton()
            button_underline.set_icon_name("format-text-underline-symbolic")
            toolbar.insert(button_underline, 2)

            button_save = Gtk.ToolButton(label="Save")
            toolbar.insert(button_save, -1)

            button_bold.connect("clicked", on_button_clicked, tag_bold, note_text_entry_buffer)
            button_italic.connect("clicked", on_button_clicked, tag_italic, note_text_entry_buffer)
            button_underline.connect("clicked", on_button_clicked, tag_underline, note_text_entry_buffer)
            button_save.connect("clicked", note_exit, False, window)

            window.connect("destroy", Gtk.main_quit)
            window.show_all()
            Gtk.main()
        elif i is not None:
            # print(i)
            note = db.get_notes()[i]

            window = Gtk.Window(title=str("QuickNotes - " + note[2]))
            window.connect("key-press-event", self.key_press)
            window.set_border_width(5)
            window.set_default_size(500, 300)

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            window.add(vbox)

            title_entry = Gtk.Entry(placeholder_text="Title")
            title_entry.modify_font(Pango.FontDescription('Ubuntu 20'))
            title_buffer = title_entry.get_buffer()
            title_buffer.set_text(note[2], len(note[2]))
            title_entry.set_margin_bottom(10)
            vbox.add(title_entry)

            toolbar = Gtk.Toolbar()
            vbox.add(toolbar)

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_hexpand(True)
            scrolled_window.set_vexpand(True)
            vbox.add(scrolled_window)

            note_text_entry = Gtk.TextView()
            note_text_entry.set_left_margin(5)
            note_text_entry.set_right_margin(5)
            note_text_entry.set_top_margin(5)
            note_text_entry.set_bottom_margin(5)
            note_text_entry.modify_font(Pango.FontDescription('Ubuntu 14'))
            note_text_entry_buffer = note_text_entry.get_buffer()
            note_text_entry_buffer.set_text(note[3], len(note[3]))
            note_text_entry.set_vexpand(True)
            scrolled_window.add(note_text_entry)

            note_text_entry_buffer = note_text_entry.get_buffer()

            tag_bold = note_text_entry_buffer.create_tag("bold", weight=Pango.Weight.BOLD)
            tag_italic = note_text_entry_buffer.create_tag("italic", style=Pango.Style.ITALIC)
            tag_underline = note_text_entry_buffer.create_tag(
                "underline", underline=Pango.Underline.SINGLE
            )

            button_bold = Gtk.ToolButton()
            button_bold.set_icon_name("format-text-bold-symbolic")
            toolbar.insert(button_bold, 0)

            button_italic = Gtk.ToolButton()
            button_italic.set_icon_name("format-text-italic-symbolic")
            toolbar.insert(button_italic, 1)

            button_underline = Gtk.ToolButton()
            button_underline.set_icon_name("format-text-underline-symbolic")
            toolbar.insert(button_underline, 2)

            button_save = Gtk.ToolButton(label="Save")
            toolbar.insert(button_save, -1)

            button_bold.connect("clicked", on_button_clicked, tag_bold, note_text_entry_buffer)
            button_italic.connect("clicked", on_button_clicked, tag_italic, note_text_entry_buffer)
            button_underline.connect("clicked", on_button_clicked, tag_underline, note_text_entry_buffer)
            button_save.connect("clicked", note_exit, True, window)

            window.connect("destroy", Gtk.main_quit)
            window.show_all()
            Gtk.main()
