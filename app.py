import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

import tracker


KEYBOARD_LAYOUTS = [
    "ISO-ES 100%",
    "ANSI-US 100%"
]

SETTINGS_FILE = "data/settings.json"

DEFAULT_SETTINGS = {
    "keyboard_layout": "ISO-ES 100%",
    "view_mode": "total",
    "start_recording_on_launch": True
}


KEY_ALIASES = {
    "Key.esc": "esc",
    "Key.f1": "f1",
    "Key.f2": "f2",
    "Key.f3": "f3",
    "Key.f4": "f4",
    "Key.f5": "f5",
    "Key.f6": "f6",
    "Key.f7": "f7",
    "Key.f8": "f8",
    "Key.f9": "f9",
    "Key.f10": "f10",
    "Key.f11": "f11",
    "Key.f12": "f12",
    "Key.print_screen": "print_screen",
    "Key.scroll_lock": "scroll_lock",
    "Key.pause": "pause",
    "Key.backspace": "backspace",
    "Key.tab": "tab",
    "Key.caps_lock": "caps_lock",
    "Key.enter": "enter",
    "Key.shift": "shift",
    "Key.shift_l": "shift",
    "Key.shift_r": "shift",
    "Key.ctrl": "ctrl",
    "Key.ctrl_l": "ctrl",
    "Key.ctrl_r": "ctrl",
    "Key.alt": "alt",
    "Key.alt_l": "alt",
    "Key.alt_r": "alt",
    "Key.alt_gr": "alt",
    "Key.cmd": "win",
    "Key.cmd_l": "win",
    "Key.cmd_r": "win",
    "Key.space": "space",
    "Key.menu": "menu",
    "Key.up": "up",
    "Key.down": "down",
    "Key.left": "left",
    "Key.right": "right",
    "Key.insert": "insert",
    "Key.home": "home",
    "Key.page_up": "page_up",
    "Key.delete": "delete",
    "Key.end": "end",
    "Key.page_down": "page_down",
    "Key.num_lock": "num_lock",
}


NUMPAD_ALIASES = {
    "<96>": "num_0",
    "<97>": "num_1",
    "<98>": "num_2",
    "<99>": "num_3",
    "<100>": "num_4",
    "<101>": "num_5",
    "<102>": "num_6",
    "<103>": "num_7",
    "<104>": "num_8",
    "<105>": "num_9",
    "<106>": "num_multiply",
    "<107>": "num_add",
    "<109>": "num_subtract",
    "<110>": "num_decimal",
    "<111>": "num_divide",
}


MOUSE_ALIASES = {
    "Button.left": "left",
    "Button.right": "right",
    "Button.middle": "middle",
    "Button.x1": "side_1",
    "Button.x2": "side_2",
    "scroll_up": "scroll_up",
    "scroll_down": "scroll_down"
}


def ensure_data_folder():
    os.makedirs("data", exist_ok=True)


def load_settings():
    ensure_data_folder()

    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            loaded_settings = json.load(file)

        settings = DEFAULT_SETTINGS.copy()
        settings.update(loaded_settings)

        if settings["keyboard_layout"] not in KEYBOARD_LAYOUTS:
            settings["keyboard_layout"] = DEFAULT_SETTINGS["keyboard_layout"]

        if settings["view_mode"] not in ["total", "session"]:
            settings["view_mode"] = DEFAULT_SETTINGS["view_mode"]

        return settings
    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    ensure_data_folder()

    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4, ensure_ascii=False)


def normalize_key_name(raw_key):
    if not raw_key:
        return None

    if raw_key in KEY_ALIASES:
        return KEY_ALIASES[raw_key]

    if raw_key in NUMPAD_ALIASES:
        return NUMPAD_ALIASES[raw_key]

    if len(raw_key) == 1:
        return raw_key.lower()

    if raw_key.startswith("Key."):
        return raw_key.replace("Key.", "").lower()

    return raw_key.lower()


def get_keyboard_counts(source_stats):
    result = {}

    for raw_key, count in source_stats["keyboard"].items():
        key_name = normalize_key_name(raw_key)

        if not key_name:
            continue

        result[key_name] = result.get(key_name, 0) + count

    return result


def get_mouse_counts(source_stats):
    result = {}

    for raw_key, count in source_stats["mouse"].items():
        key_name = MOUSE_ALIASES.get(raw_key, raw_key)
        result[key_name] = result.get(key_name, 0) + count

    return result


def interpolate_color(count, max_count):
    if max_count <= 0 or count <= 0:
        return "#2b2b2b"

    ratio = count / max_count
    ratio = max(0, min(ratio, 1))

    start = (43, 43, 43)
    end = (0, 200, 255)

    r = int(start[0] + (end[0] - start[0]) * ratio)
    g = int(start[1] + (end[1] - start[1]) * ratio)
    b = int(start[2] + (end[2] - start[2]) * ratio)

    return f"#{r:02x}{g:02x}{b:02x}"


class KeyRecordApp:
    KEY_WIDTH = 42
    KEY_HEIGHT = 48
    KEY_GAP = 4

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KeyRecord")
        try:
            self.root.iconbitmap("assets/icon.ico")
        except Exception:
            pass
        self.root.geometry("1280x780")
        self.root.minsize(1050, 620)

        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        self.root.bind("<Unmap>", self.on_minimize)

        self.is_exiting = False
        self.settings = load_settings()

        self.view_mode = tk.StringVar(value=self.settings.get("view_mode", "total"))
        self.keyboard_layout_name = tk.StringVar(
            value=self.settings.get("keyboard_layout", "ISO-ES 100%")
        )

        tracker.tracking_enabled = self.settings.get("start_recording_on_launch", True)

        self.key_widgets = []
        self.mouse_widgets = {}

        self.build_ui()
        self.update_ui()

    def build_ui(self):
        self.main_canvas = tk.Canvas(self.root, borderwidth=0)

        self.scrollbar_y = ttk.Scrollbar(
            self.root,
            orient="vertical",
            command=self.main_canvas.yview
        )

        self.scrollable_frame = ttk.Frame(self.main_canvas)

        self.canvas_window = self.main_canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.main_canvas.configure(yscrollcommand=self.scrollbar_y.set)

        self.main_canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.scrollable_frame.bind("<Configure>", self.update_scroll_region)
        self.main_canvas.bind("<Configure>", self.update_scroll_region)
        self.main_canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        self.title_label = ttk.Label(
            self.scrollable_frame,
            text="KeyRecord",
            font=("Segoe UI", 22, "bold")
        )
        self.title_label.pack(pady=(18, 4))

        self.subtitle_label = ttk.Label(
            self.scrollable_frame,
            text="Keyboard & mouse usage heatmap"
        )
        self.subtitle_label.pack(pady=(0, 12))

        self.top_frame = ttk.Frame(self.scrollable_frame)
        self.top_frame.pack(pady=8)

        self.status_label = ttk.Label(
            self.top_frame,
            text="Status: Recording",
            font=("Segoe UI", 12)
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=4)

        self.toggle_button = ttk.Button(
            self.top_frame,
            text="Stop Recording",
            command=self.toggle_recording
        )
        self.toggle_button.grid(row=0, column=1, padx=10, pady=4)

        self.reset_session_button = ttk.Button(
            self.top_frame,
            text="Reset Session",
            command=self.reset_session
        )
        self.reset_session_button.grid(row=0, column=2, padx=10, pady=4)

        self.reset_total_button = ttk.Button(
            self.top_frame,
            text="Reset Total",
            command=self.reset_total
        )
        self.reset_total_button.grid(row=0, column=3, padx=10, pady=4)

        self.summary_label = ttk.Label(
            self.top_frame,
            text="Keyboard events: 0 | Mouse events: 0",
            font=("Segoe UI", 11)
        )
        self.summary_label.grid(row=0, column=4, padx=10, pady=4)

        self.controls_frame = ttk.Frame(self.scrollable_frame)
        self.controls_frame.pack(pady=8)

        self.total_radio = ttk.Radiobutton(
            self.controls_frame,
            text="Total",
            variable=self.view_mode,
            value="total",
            command=self.on_view_mode_changed
        )
        self.total_radio.grid(row=0, column=0, padx=8)

        self.session_radio = ttk.Radiobutton(
            self.controls_frame,
            text="Session",
            variable=self.view_mode,
            value="session",
            command=self.on_view_mode_changed
        )
        self.session_radio.grid(row=0, column=1, padx=8)

        self.layout_label = ttk.Label(
            self.controls_frame,
            text="Keyboard layout:"
        )
        self.layout_label.grid(row=0, column=2, padx=(28, 6))

        self.layout_select = ttk.Combobox(
            self.controls_frame,
            textvariable=self.keyboard_layout_name,
            values=KEYBOARD_LAYOUTS,
            state="readonly",
            width=16
        )
        self.layout_select.grid(row=0, column=3, padx=6)
        self.layout_select.bind("<<ComboboxSelected>>", self.change_keyboard_layout)

        self.legend_label = ttk.Label(
            self.scrollable_frame,
            text="Darker = less used | Brighter = more used"
        )
        self.legend_label.pack(pady=(0, 12))

        self.keyboard_frame = tk.LabelFrame(
            self.scrollable_frame,
            text="Keyboard heatmap",
            padx=12,
            pady=12,
            font=("Segoe UI", 10, "bold")
        )
        self.keyboard_frame.pack(padx=18, pady=(0, 18), anchor="center")

        self.build_keyboard_heatmap()

        self.mouse_frame = tk.LabelFrame(
            self.scrollable_frame,
            text="Mouse heatmap",
            padx=12,
            pady=12,
            font=("Segoe UI", 10, "bold")
        )
        self.mouse_frame.pack(padx=18, pady=(0, 18), anchor="center")

        self.build_mouse_heatmap()

        self.unmapped_frame = tk.LabelFrame(
            self.scrollable_frame,
            text="Unmapped inputs",
            padx=12,
            pady=12,
            font=("Segoe UI", 10, "bold")
        )
        self.unmapped_frame.pack(padx=18, pady=(0, 18), anchor="center")

        self.unmapped_container = tk.Frame(self.unmapped_frame)
        self.unmapped_container.pack(anchor="center")

        self.unmapped_keyboard_label = ttk.Label(
            self.unmapped_container,
            text="Keyboard inputs not shown in layout"
        )
        self.unmapped_keyboard_label.grid(row=0, column=0, padx=8, pady=(0, 4))

        self.unmapped_mouse_label = ttk.Label(
            self.unmapped_container,
            text="Mouse inputs not shown in layout"
        )
        self.unmapped_mouse_label.grid(row=0, column=1, padx=8, pady=(0, 4))

        self.unmapped_keyboard_list = tk.Listbox(
            self.unmapped_container,
            width=38,
            height=6
        )
        self.unmapped_keyboard_list.grid(row=1, column=0, padx=8)

        self.unmapped_mouse_list = tk.Listbox(
            self.unmapped_container,
            width=38,
            height=6
        )
        self.unmapped_mouse_list.grid(row=1, column=1, padx=8)

        self.info_label = ttk.Label(
            self.scrollable_frame,
            text="Minimize to tray. Close to exit KeyRecord."
        )
        self.info_label.pack(pady=(0, 18))

    def update_scroll_region(self, event=None):
        canvas_width = self.main_canvas.winfo_width()

        self.main_canvas.itemconfig(
            self.canvas_window,
            width=canvas_width
        )

        self.main_canvas.coords(self.canvas_window, 0, 0)
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_minimize(self, event=None):
        if self.is_exiting:
            return

        if self.root.state() == "iconic":
            self.root.after(100, self.hide_window)

    def confirm_exit(self):
        confirm = messagebox.askyesno(
            "Exit KeyRecord",
            "Do you want to close KeyRecord completely?\n\nIf you only want to keep it running in the tray, minimize the window instead."
        )

        if confirm:
            self.exit_app()

    def exit_app(self):
        self.save_current_settings()
        self.is_exiting = True

        try:
            tracker.save_now()
            tracker.stop_tracking()
        except Exception:
            pass

        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass

        os._exit(0)

    def save_current_settings(self):
        self.settings["keyboard_layout"] = self.keyboard_layout_name.get()
        self.settings["view_mode"] = self.view_mode.get()
        self.settings["start_recording_on_launch"] = tracker.tracking_enabled
        save_settings(self.settings)

    def on_view_mode_changed(self):
        self.save_current_settings()
        self.update_ui()

    def get_current_stats(self):
        if self.view_mode.get() == "session":
            return tracker.session_stats

        return tracker.stats

    def change_keyboard_layout(self, event=None):
        self.save_current_settings()

        for widget in self.keyboard_frame.winfo_children():
            widget.destroy()

        self.key_widgets = []
        self.build_keyboard_heatmap()
        self.update_ui()

    def build_keyboard_heatmap(self):
        keyboard_outer = tk.Frame(self.keyboard_frame)
        keyboard_outer.pack(anchor="center")

        function_row = tk.Frame(keyboard_outer)
        function_row.pack(anchor="center", pady=(0, 10))

        self.configure_keyboard_grid(function_row, columns=20, rows=1)

        is_iso = self.keyboard_layout_name.get() == "ISO-ES 100%"
        print_label = "Impr" if is_iso else "PrtSc"
        scroll_label = "Bloq" if is_iso else "ScrLk"
        pause_label = "Pausa" if is_iso else "Pause"

        self.create_key(function_row, "esc", "Esc", 0, 0)
        self.create_empty_key_space(function_row, 0, 1)

        self.create_key(function_row, "f1", "F1", 0, 2)
        self.create_key(function_row, "f2", "F2", 0, 3)
        self.create_key(function_row, "f3", "F3", 0, 4)
        self.create_key(function_row, "f4", "F4", 0, 5)

        self.create_empty_key_space(function_row, 0, 6)

        self.create_key(function_row, "f5", "F5", 0, 7)
        self.create_key(function_row, "f6", "F6", 0, 8)
        self.create_key(function_row, "f7", "F7", 0, 9)
        self.create_key(function_row, "f8", "F8", 0, 10)

        self.create_empty_key_space(function_row, 0, 11)

        self.create_key(function_row, "f9", "F9", 0, 12)
        self.create_key(function_row, "f10", "F10", 0, 13)
        self.create_key(function_row, "f11", "F11", 0, 14)
        self.create_key(function_row, "f12", "F12", 0, 15)

        self.create_empty_key_space(function_row, 0, 16)

        self.create_key(function_row, "print_screen", print_label, 0, 17)
        self.create_key(function_row, "scroll_lock", scroll_label, 0, 18)
        self.create_key(function_row, "pause", pause_label, 0, 19)

        keyboard_wrapper = tk.Frame(keyboard_outer)
        keyboard_wrapper.pack(anchor="center")

        main_block = tk.Frame(keyboard_wrapper)
        nav_block = tk.Frame(keyboard_wrapper)
        numpad_block = tk.Frame(keyboard_wrapper)

        main_block.grid(row=0, column=0, padx=(0, 18), sticky="n")
        nav_block.grid(row=0, column=1, padx=(0, 18), sticky="n")
        numpad_block.grid(row=0, column=2, sticky="n")

        self.build_main_keyboard_block(main_block)
        self.build_navigation_block(nav_block)
        self.build_numpad_block(numpad_block)

    def create_key(self, parent, key_id, display, row, column, colspan=1, rowspan=1):
        label = tk.Label(
            parent,
            text=f"{display}\n0",
            width=1,
            height=1,
            bg="#2b2b2b",
            fg="white",
            relief="solid",
            bd=1,
            justify="center",
            font=("Segoe UI", 8)
        )

        label.grid(
            row=row,
            column=column,
            columnspan=colspan,
            rowspan=rowspan,
            padx=self.KEY_GAP // 2,
            pady=self.KEY_GAP // 2,
            sticky="nsew"
        )

        self.key_widgets.append((label, key_id, display))
        return label

    def create_empty_key_space(self, parent, row, column, colspan=1, rowspan=1):
        spacer = tk.Frame(parent)
        spacer.grid(
            row=row,
            column=column,
            columnspan=colspan,
            rowspan=rowspan,
            padx=self.KEY_GAP // 2,
            pady=self.KEY_GAP // 2,
            sticky="nsew"
        )

    def configure_keyboard_grid(self, parent, columns, rows):
        for column in range(columns):
            parent.grid_columnconfigure(column, minsize=self.KEY_WIDTH, weight=0)

        for row in range(rows):
            parent.grid_rowconfigure(row, minsize=self.KEY_HEIGHT, weight=0)

    def build_main_keyboard_block(self, parent):
        self.configure_keyboard_grid(parent, columns=15, rows=5)

        is_iso = self.keyboard_layout_name.get() == "ISO-ES 100%"

        if is_iso:
            number_row = [
                ("º", "º"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"),
                ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"), ("0", "0"), ("'", "'"), ("¡", "¡")
            ]
            top_letter_row = [
                ("q", "Q"), ("w", "W"), ("e", "E"), ("r", "R"), ("t", "T"), ("y", "Y"),
                ("u", "U"), ("i", "I"), ("o", "O"), ("p", "P"), ("`", "`"), ("+", "+"), ("ç", "Ç")
            ]
            home_row = [
                ("a", "A"), ("s", "S"), ("d", "D"), ("f", "F"), ("g", "G"), ("h", "H"),
                ("j", "J"), ("k", "K"), ("l", "L"), ("ñ", "Ñ"), ("´", "´")
            ]
            bottom_row = [
                ("<", "<"), ("z", "Z"), ("x", "X"), ("c", "C"), ("v", "V"), ("b", "B"),
                ("n", "N"), ("m", "M"), (",", ","), (".", "."), ("-", "-")
            ]
            right_alt_label = "AltGr"
        else:
            number_row = [
                ("`", "`"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"),
                ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"), ("0", "0"), ("-", "-"), ("=", "=")
            ]
            top_letter_row = [
                ("q", "Q"), ("w", "W"), ("e", "E"), ("r", "R"), ("t", "T"), ("y", "Y"),
                ("u", "U"), ("i", "I"), ("o", "O"), ("p", "P"), ("[", "["), ("]", "]"), ("\\", "\\")
            ]
            home_row = [
                ("a", "A"), ("s", "S"), ("d", "D"), ("f", "F"), ("g", "G"), ("h", "H"),
                ("j", "J"), ("k", "K"), ("l", "L"), (";", ";"), ("'", "'")
            ]
            bottom_row = [
                ("z", "Z"), ("x", "X"), ("c", "C"), ("v", "V"), ("b", "B"),
                ("n", "N"), ("m", "M"), (",", ","), (".", "."), ("/", "/")
            ]
            right_alt_label = "Alt"

        for index, (key_id, label) in enumerate(number_row):
            self.create_key(parent, key_id, label, 0, index)

        self.create_key(parent, "backspace", "Backspace", 0, 13, colspan=2)

        self.create_key(parent, "tab", "Tab", 1, 0, colspan=2)

        for index, (key_id, label) in enumerate(top_letter_row):
            self.create_key(parent, key_id, label, 1, index + 2)

        self.create_key(parent, "caps_lock", "Caps", 2, 0, colspan=2)

        for index, (key_id, label) in enumerate(home_row):
            self.create_key(parent, key_id, label, 2, index + 2)

        self.create_key(parent, "enter", "Enter", 2, 13, colspan=2)

        self.create_key(parent, "shift", "Shift", 3, 0, colspan=2)

        for index, (key_id, label) in enumerate(bottom_row):
            self.create_key(parent, key_id, label, 3, index + 2)

        if is_iso:
            self.create_key(parent, "shift", "Shift", 3, 13, colspan=2)
        else:
            self.create_key(parent, "shift", "Shift", 3, 12, colspan=3)

        self.create_key(parent, "ctrl", "Ctrl", 4, 0)
        self.create_key(parent, "win", "Win", 4, 1)
        self.create_key(parent, "alt", "Alt", 4, 2)
        self.create_key(parent, "space", "Space", 4, 3, colspan=6)
        self.create_key(parent, "alt", right_alt_label, 4, 9)
        self.create_key(parent, "win", "Win", 4, 10)
        self.create_key(parent, "menu", "Menu", 4, 11)
        self.create_key(parent, "ctrl", "Ctrl", 4, 12)

    def build_navigation_block(self, parent):
        self.configure_keyboard_grid(parent, columns=3, rows=5)

        is_iso = self.keyboard_layout_name.get() == "ISO-ES 100%"
        home_label = "Inicio" if is_iso else "Home"
        page_up_label = "RePág" if is_iso else "PgUp"
        delete_label = "Supr" if is_iso else "Del"
        end_label = "Fin" if is_iso else "End"
        page_down_label = "AvPág" if is_iso else "PgDn"

        self.create_key(parent, "insert", "Ins", 0, 0)
        self.create_key(parent, "home", home_label, 0, 1)
        self.create_key(parent, "page_up", page_up_label, 0, 2)

        self.create_key(parent, "delete", delete_label, 1, 0)
        self.create_key(parent, "end", end_label, 1, 1)
        self.create_key(parent, "page_down", page_down_label, 1, 2)

        self.create_empty_key_space(parent, 2, 0)
        self.create_empty_key_space(parent, 2, 1)
        self.create_empty_key_space(parent, 2, 2)

        self.create_empty_key_space(parent, 3, 0)
        self.create_key(parent, "up", "↑", 3, 1)
        self.create_empty_key_space(parent, 3, 2)

        self.create_key(parent, "left", "←", 4, 0)
        self.create_key(parent, "down", "↓", 4, 1)
        self.create_key(parent, "right", "→", 4, 2)

    def build_numpad_block(self, parent):
        self.configure_keyboard_grid(parent, columns=4, rows=5)

        decimal_label = "," if self.keyboard_layout_name.get() == "ISO-ES 100%" else "."

        self.create_key(parent, "num_lock", "Num", 0, 0)
        self.create_key(parent, "num_divide", "/", 0, 1)
        self.create_key(parent, "num_multiply", "*", 0, 2)
        self.create_key(parent, "num_subtract", "-", 0, 3)

        self.create_key(parent, "num_7", "7", 1, 0)
        self.create_key(parent, "num_8", "8", 1, 1)
        self.create_key(parent, "num_9", "9", 1, 2)
        self.create_key(parent, "num_add", "+", 1, 3, rowspan=2)

        self.create_key(parent, "num_4", "4", 2, 0)
        self.create_key(parent, "num_5", "5", 2, 1)
        self.create_key(parent, "num_6", "6", 2, 2)

        self.create_key(parent, "num_1", "1", 3, 0)
        self.create_key(parent, "num_2", "2", 3, 1)
        self.create_key(parent, "num_3", "3", 3, 2)
        self.create_key(parent, "num_enter", "Enter", 3, 3, rowspan=2)

        self.create_key(parent, "num_0", "0", 4, 0, colspan=2)
        self.create_key(parent, "num_decimal", decimal_label, 4, 2)

    def build_mouse_heatmap(self):
        mouse_container = tk.Frame(self.mouse_frame)
        mouse_container.pack(anchor="center")

        self.mouse_widgets["left"] = self.create_mouse_box(mouse_container, "Left Click", 0, 0)
        self.mouse_widgets["middle"] = self.create_mouse_box(mouse_container, "Middle Click", 0, 1)
        self.mouse_widgets["right"] = self.create_mouse_box(mouse_container, "Right Click", 0, 2)
        self.mouse_widgets["side_1"] = self.create_mouse_box(mouse_container, "Side 1", 0, 3)
        self.mouse_widgets["side_2"] = self.create_mouse_box(mouse_container, "Side 2", 0, 4)

        self.mouse_widgets["scroll_up"] = self.create_mouse_box(mouse_container, "Scroll Up", 1, 1)
        self.mouse_widgets["scroll_down"] = self.create_mouse_box(mouse_container, "Scroll Down", 1, 2)

    def create_mouse_box(self, parent, text, row, column, colspan=1, rowspan=1):
        label = tk.Label(
            parent,
            text=f"{text}\n0",
            width=18,
            height=3,
            bg="#2b2b2b",
            fg="white",
            relief="solid",
            bd=1,
            justify="center",
            font=("Segoe UI", 10)
        )

        label.grid(
            row=row,
            column=column,
            columnspan=colspan,
            rowspan=rowspan,
            padx=5,
            pady=5,
            sticky="nsew"
        )

        return label

    def toggle_recording(self):
        tracker.tracking_enabled = not tracker.tracking_enabled
        self.save_current_settings()
        self.refresh_recording_ui()

    def reset_session(self):
        confirm = messagebox.askyesno(
            "Reset session stats",
            "Reset only the current session stats?"
        )

        if confirm:
            tracker.reset_session_stats()
            self.update_ui()

    def reset_total(self):
        confirm = messagebox.askyesno(
            "Reset total stats",
            "This will delete all saved stats and reset the current session.\n\nAre you sure?"
        )

        if confirm:
            tracker.reset_total_stats()
            self.update_ui()

    def refresh_recording_ui(self):
        if tracker.tracking_enabled:
            self.status_label.config(text="Status: Recording")
            self.toggle_button.config(text="Stop Recording")
        else:
            self.status_label.config(text="Status: Paused")
            self.toggle_button.config(text="Start Recording")

    def update_keyboard_heatmap(self):
        current_stats = self.get_current_stats()
        keyboard_counts = get_keyboard_counts(current_stats)

        max_count = 0

        for _, key_id, _ in self.key_widgets:
            value = keyboard_counts.get(key_id, 0)

            if value > max_count:
                max_count = value

        for widget, key_id, display in self.key_widgets:
            count = keyboard_counts.get(key_id, 0)
            color = interpolate_color(count, max_count)

            widget.config(
                text=f"{display}\n{count}",
                bg=color
            )

    def update_mouse_heatmap(self):
        current_stats = self.get_current_stats()
        mouse_counts = get_mouse_counts(current_stats)

        max_count = max(mouse_counts.values(), default=0)

        for key_id, widget in self.mouse_widgets.items():
            count = mouse_counts.get(key_id, 0)
            color = interpolate_color(count, max_count)

            current_title = widget.cget("text").split("\n")[0]

            widget.config(
                text=f"{current_title}\n{count}",
                bg=color
            )

    def update_unmapped_inputs(self):
        current_stats = self.get_current_stats()

        keyboard_counts = get_keyboard_counts(current_stats)
        mouse_counts = get_mouse_counts(current_stats)

        visible_keyboard_keys = {key_id for _, key_id, _ in self.key_widgets}
        visible_mouse_keys = set(self.mouse_widgets.keys())

        unmapped_keyboard = sorted(
            [
                (key, count)
                for key, count in keyboard_counts.items()
                if key not in visible_keyboard_keys
            ],
            key=lambda item: item[1],
            reverse=True
        )

        unmapped_mouse = sorted(
            [
                (key, count)
                for key, count in mouse_counts.items()
                if key not in visible_mouse_keys
            ],
            key=lambda item: item[1],
            reverse=True
        )

        self.unmapped_keyboard_list.delete(0, tk.END)
        self.unmapped_mouse_list.delete(0, tk.END)

        if unmapped_keyboard:
            for key, count in unmapped_keyboard[:12]:
                self.unmapped_keyboard_list.insert(tk.END, f"{key}: {count}")
        else:
            self.unmapped_keyboard_list.insert(tk.END, "No unmapped keyboard inputs")

        if unmapped_mouse:
            for key, count in unmapped_mouse[:12]:
                self.unmapped_mouse_list.insert(tk.END, f"{key}: {count}")
        else:
            self.unmapped_mouse_list.insert(tk.END, "No unmapped mouse inputs")

    def update_summary(self):
        current_stats = self.get_current_stats()

        keyboard_total = sum(current_stats["keyboard"].values())
        mouse_total = sum(current_stats["mouse"].values())

        mode_label = "Session" if self.view_mode.get() == "session" else "Total"

        self.summary_label.config(
            text=f"{mode_label} | Keyboard events: {keyboard_total} | Mouse events: {mouse_total}"
        )

    def update_ui(self):
        self.refresh_recording_ui()
        self.update_summary()
        self.update_keyboard_heatmap()
        self.update_mouse_heatmap()
        self.update_unmapped_inputs()

        self.root.after(1000, self.update_ui)

    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_window(self):
        self.root.withdraw()

    def run(self):
        self.root.mainloop()
