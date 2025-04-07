import os
import sys
import win32com.client

def add_to_startup():
    startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    exe_path = sys.executable

    shortcut_path = os.path.join(startup_dir, "NexInsights.lnk")
    if not os.path.exists(shortcut_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.IconLocation = exe_path
        shortcut.save()
