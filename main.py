"""
Punto de entrada principal para la aplicación.
"""
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from simulation_naive import SimulationNaive
from simulation_corrected import SimulationCorrected
from ui import DiningPhilosophersUI
import random


class SimulationSelector:
    """Selector de modo de simulación"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Filósofos Comensales - Selector de Simulación")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.selected_mode = None
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del selector"""
        # Título
        title = ttk.Label(
            self.root,
            text="PROBLEMA DE LOS FILÓSOFOS COMENSALES",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=20)
        
        subtitle = ttk.Label(
            self.root,
            text="Simulación Concurrente de Sistemas Operacionales",
            font=("Arial", 11)
        )
        subtitle.pack()
        
        # Separador
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Frame para opciones
        options_frame = ttk.Frame(self.root)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Opción 1: Modo Ingenuo
        mode1_frame = ttk.LabelFrame(
            options_frame,
            text="Modo 1: INGENUO (Propenso a Deadlock)",
            padding=15
        )
        mode1_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(
            mode1_frame,
            text="Cada filósofo toma:\n"
                 "1. Tenedor izquierdo\n"
                 "2. Tenedor derecho\n\n"
                 "Si todos tocan izquierdo al mismo tiempo → DEADLOCK",
            justify=tk.LEFT,
            font=("Arial", 10)
        ).pack(anchor=tk.W)
        
        ttk.Button(
            mode1_frame,
            text="Ejecutar Modo Ingenuo",
            command=lambda: self._select_mode("naive")
        ).pack(side=tk.RIGHT, padx=5)
        
        # Opción 2: Modo Corregido
        mode2_frame = ttk.LabelFrame(
            options_frame,
            text="Modo 2: CORREGIDO (Sin Deadlock ni Starvation)",
            padding=15
        )
        mode2_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(
            mode2_frame,
            text="Usa un Monitor FIFO que garantiza:\n"
                 "• Sin deadlock: ambos tenedores atómicamente\n"
                 "• Sin starvation: cola justa FIFO\n"
                 "• Concurrencia real preservada",
            justify=tk.LEFT,
            font=("Arial", 10)
        ).pack(anchor=tk.W)
        
        ttk.Button(
            mode2_frame,
            text="Ejecutar Modo Corregido",
            command=lambda: self._select_mode("corrected")
        ).pack(side=tk.RIGHT, padx=5)
        
        # Frame inferior con botones
        button_frame = ttk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
        
        ttk.Button(
            button_frame,
            text="Salir",
            command=self.root.quit
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Información",
            command=self._show_info
        ).pack(side=tk.RIGHT, padx=5)
    
    def _select_mode(self, mode):
        """Selecciona el modo de simulación"""
        self.selected_mode = mode
        self.root.destroy()
    
    def _show_info(self):
        """Muestra información sobre el problema"""
        info_text = """PROBLEMA DE LOS FILÓSOFOS COMENSALES

Problema clásico de concurrencia en Sistemas Operacionales.

CONTEXTO:
- 5 filósofos alrededor de una mesa circular
- Cada filósofo entre dos tenedores
- Para comer necesitan AMBOS tenedores
- Alternan entre pensar y comer

CONDICIÓN DE DEADLOCK:
- Todos toman tenedor izquierdo simultáneamente
- Todos esperan tenedor derecho (que tiene el vecino)
- Nadie puede liberar tenedores
- Sistema se bloquea indefinidamente

SOLUCIÓN:
- Monitor con Condition Variables
- Cola FIFO para fairness
- Adquisición atómica de ambos tenedores
- Garantiza: Sin deadlock, sin starvation
"""
        messagebox.showinfo("Información", info_text)
    
    def run(self):
        """Ejecuta el selector"""
        self.root.mainloop()
        return self.selected_mode


def main():
    """Función principal"""
    # Selector de modo
    selector = SimulationSelector()
    mode = selector.run()
    
    if mode is None:
        return
    
    # Crear simulación según modo seleccionado
    if mode == "naive":
        simulation = SimulationNaive()
    else:
        simulation = SimulationCorrected()
    
    # Crear ventana principal y UI
    root = tk.Tk()
    ui = DiningPhilosophersUI(root, simulation)
    
    root.protocol("WM_DELETE_WINDOW", ui.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
