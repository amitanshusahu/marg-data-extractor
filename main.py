import threading
from db import initialize_db, retry_unsent
from file_watcher import monitor_folder
import pystray
from pystray import MenuItem as item
from PIL import Image
from safe_path import resource_path
from autostartup import add_to_startup
import sys

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
        item('Quit', on_quit)
    )
    setup()
    icon.run()


if __name__ == "__main__":
    run_tray()
