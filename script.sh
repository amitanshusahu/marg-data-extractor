# install dependency
pip install pymupdf pillow watchdog requests pystray pywin32 plyer


# build
pyinstaller --clean --onefile --windowed --icon=app.ico --name=NexInsights --add-data "logo.png;." main.py
python -m pyinstaller --clean --onefile --windowed --icon=app.ico --name=NexInsights --add-data "logo.png;." main.py
pyinstaller NexInsights.spec