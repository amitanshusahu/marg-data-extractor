# install dependency
pip install pymupdf pillow watchdog pywin32 requests


# build
pyinstaller --clean --onefile --windowed --icon=app.ico --name=NexInsights --add-data "logo.png;." main.py
