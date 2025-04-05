import threading
from db import initialize_db, retry_unsent
from file_watcher import monitor_folder

if __name__ == "__main__":
    initialize_db()
    threading.Thread(target=retry_unsent, daemon=True).start()
    monitor_folder()
