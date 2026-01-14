import threading
from db import initialize_db, retry_unsent
from file_watcher import monitor_folder
import pystray
from pystray import MenuItem as item
from PIL import Image
from safe_path import resource_path
from autostartup import add_to_startup
import sys 
from settings_gui import open_settings
from db_manager_gui import open_db_manager
from send_mail import send_diagnosis_via_gmail
from debug_gui import open_debug_gui

if '--autorun' in sys.argv:
    add_to_startup()

def create_image():
    return Image.open(resource_path("app.ico"))


def on_quit(icon, item):
    icon.stop()
    sys.exit()


def setup():
    initialize_db()
    threading.Thread(target=retry_unsent, daemon=True).start()
    threading.Thread(target=monitor_folder, daemon=True).start()


def run_tray():
    icon = pystray.Icon("FileMonitor")
    icon.icon = create_image()
    icon.menu = pystray.Menu(
        item('View Database', lambda icon, item: open_db_manager()),
        item('Settings', lambda icon, item: open_settings()),
        item('Debug', lambda icon, item: open_debug_gui()),
        item('Send DB', lambda icon, item: threading.Thread(target=send_diagnosis_via_gmail, daemon=True).start()),
        item('Quit', on_quit)
    )
    setup()
    icon.run()


if __name__ == "__main__":
    run_tray()
