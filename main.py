"""
Punto de entrada principal para la aplicación.
"""
import tkinter as tk

from ui import DiningPhilosophersUI


def main():
    """Lanza la interfaz principal."""
    root = tk.Tk()
    ui = DiningPhilosophersUI(root)
    root.protocol("WM_DELETE_WINDOW", ui.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
