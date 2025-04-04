from db import initialize_db
from file_watcher import monitor_folder

if __name__ == "__main__":
    initialize_db()
    monitor_folder()
