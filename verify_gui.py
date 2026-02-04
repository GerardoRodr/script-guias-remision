try:
    import tkinter
    from src.gui.main_window import MainWindow
    from src.config.settings import settings
    from src.parsers.pdf_parser import PDFParser
    print("Imports successful")
except Exception as e:
    print(f"Import failed: {e}")
    exit(1)
