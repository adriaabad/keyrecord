import os
import sys

from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

import tracker


icon = None
app_instance = None


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def set_app(app):
    global app_instance
    app_instance = app


def create_fallback_image():
    width = 64
    height = 64

    image = Image.new("RGB", (width, height), (30, 30, 30))
    draw = ImageDraw.Draw(image)

    draw.rectangle((14, 18, 50, 46), fill=(220, 220, 200))
    draw.ellipse((24, 20, 40, 36), fill=(220, 0, 0))
    draw.rectangle((22, 42, 42, 48), fill=(40, 40, 40))

    return image


def create_image():
    icon_path = resource_path("assets/icon.png")

    try:
        return Image.open(icon_path)
    except Exception:
        return create_fallback_image()


def open_app(icon, item):
    if app_instance:
        app_instance.show_window()


def toggle_tracking(icon, item):
    tracker.tracking_enabled = not tracker.tracking_enabled

    state = "ON" if tracker.tracking_enabled else "OFF"
    print(f"Tracking: {state}")


def quit_app(icon, item):
    tracker.save_now()

    try:
        tracker.stop_tracking()
    except Exception:
        pass

    if app_instance:
        try:
            app_instance.root.quit()
            app_instance.root.destroy()
        except Exception:
            pass

    icon.stop()
    os._exit(0)


def run_tray():
    global icon

    icon = Icon(
        "KeyRecord",
        create_image(),
        menu=Menu(
            MenuItem("Open KeyRecord", open_app),
            MenuItem("Pause / Resume", toggle_tracking),
            MenuItem("Exit", quit_app)
        )
    )

    icon.run()