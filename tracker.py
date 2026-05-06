from pynput import keyboard, mouse
from storage import load_stats, save_stats, get_empty_stats

stats = load_stats()

session_stats = {
    "keyboard": {},
    "mouse": {}
}

tracking_enabled = True
dirty = False

pressed_keys = set()


VK_TO_KEY = {
    8: "backspace",
    9: "tab",
    13: "enter",
    16: "shift",
    17: "ctrl",
    18: "alt",
    19: "pause",
    20: "caps_lock",
    27: "esc",
    32: "space",
    33: "page_up",
    34: "page_down",
    35: "end",
    36: "home",
    37: "left",
    38: "up",
    39: "right",
    40: "down",
    44: "print_screen",
    45: "insert",
    46: "delete",
    91: "win",
    92: "win",
    93: "menu",
    144: "num_lock",
    145: "scroll_lock",

    96: "num_0",
    97: "num_1",
    98: "num_2",
    99: "num_3",
    100: "num_4",
    101: "num_5",
    102: "num_6",
    103: "num_7",
    104: "num_8",
    105: "num_9",
    106: "num_multiply",
    107: "num_add",
    109: "num_subtract",
    110: "num_decimal",
    111: "num_divide",
}


SPECIAL_KEY_NAMES = {
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


def add_count_to_dict(target, category, name):
    if name not in target[category]:
        target[category][name] = 0

    target[category][name] += 1


def add_count(category, name):
    global dirty

    add_count_to_dict(stats, category, name)
    add_count_to_dict(session_stats, category, name)

    dirty = True


def get_clean_key_name(key):
    raw_name = str(key)

    if raw_name in SPECIAL_KEY_NAMES:
        return SPECIAL_KEY_NAMES[raw_name]

    vk = getattr(key, "vk", None)

    if vk in VK_TO_KEY:
        return VK_TO_KEY[vk]

    if vk is not None:
        if 65 <= vk <= 90:
            return chr(vk).lower()

        if 48 <= vk <= 57:
            return chr(vk)

    char = getattr(key, "char", None)

    if char:
        char_code = ord(char)

        if 1 <= char_code <= 26:
            return chr(char_code + 96)

        if char_code >= 32:
            return char.lower()

    if raw_name.startswith("'") and raw_name.endswith("'"):
        return raw_name[1:-1].lower()

    return raw_name.replace("Key.", "").lower()


def save_if_needed():
    global dirty

    if dirty:
        save_stats(stats)
        dirty = False
        print("Stats saved")


def save_now():
    save_stats(stats)
    print("Stats saved")


def reset_session_stats():
    session_stats["keyboard"].clear()
    session_stats["mouse"].clear()
    print("Session stats reset")


def reset_total_stats():
    global stats, dirty

    stats = get_empty_stats()
    reset_session_stats()
    save_stats(stats)

    dirty = False

    print("Total stats reset")


def on_press(key):
    if not tracking_enabled:
        return

    key_name = get_clean_key_name(key)

    if not key_name:
        return

    if key_name in pressed_keys:
        return

    pressed_keys.add(key_name)

    add_count("keyboard", key_name)

    print(f"KEY: {key_name} -> {stats['keyboard'][key_name]}")


def on_release(key):
    key_name = get_clean_key_name(key)

    if key_name in pressed_keys:
        pressed_keys.remove(key_name)


def on_click(x, y, button, pressed):
    if not tracking_enabled:
        return

    if pressed:
        button_name = str(button)
        add_count("mouse", button_name)

        print(f"MOUSE: {button_name} -> {stats['mouse'][button_name]}")


def on_scroll(x, y, dx, dy):
    if not tracking_enabled:
        return

    direction = "scroll_up" if dy > 0 else "scroll_down"

    add_count("mouse", direction)

    print(f"{direction} -> {stats['mouse'][direction]}")


keyboard_listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release
)

mouse_listener = mouse.Listener(
    on_click=on_click,
    on_scroll=on_scroll
)


def start_tracking():
    keyboard_listener.start()
    mouse_listener.start()


def stop_tracking():
    keyboard_listener.stop()
    mouse_listener.stop()
    save_now()