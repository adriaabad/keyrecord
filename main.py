from tracker import start_tracking, save_if_needed
from app import KeyRecordApp
from tray import run_tray, set_app

import threading
import time


def autosave_loop():
    while True:
        time.sleep(5)
        save_if_needed()


print("KeyRecord iniciado")

start_tracking()

app = KeyRecordApp()
set_app(app)

autosave_thread = threading.Thread(
    target=autosave_loop,
    daemon=True
)
autosave_thread.start()

tray_thread = threading.Thread(
    target=run_tray,
    daemon=True
)
tray_thread.start()

app.run()