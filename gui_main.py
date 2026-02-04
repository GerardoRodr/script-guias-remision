import sys
from src.gui.main_window import MainWindow

def main():
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        print(f"Error iniciando la aplicación: {e}")
        input("Presione enter para salir...")

if __name__ == "__main__":
    main()
