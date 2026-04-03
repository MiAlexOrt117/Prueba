"""
Interfaz gráfica en Tkinter para la simulación de los filósofos comensales.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import math
import threading
import time
from utils import PhilosopherState, COLORS


class DiningPhilosophersUI:
    """Interfaz gráfica para la simulación"""
    
    def __init__(self, root, simulation):
        """
        Inicializa la interfaz.
        
        Args:
            root: Ventana raíz de Tkinter
            simulation: Objeto de simulación (Naive o Corrected)
        """
        self.root = root
        self.simulation = simulation
        self.root.title("Problema de los Filósofos Comensales - Simulación Concurrente")
        self.root.geometry("1400x900")
        
        # Callback para que la simulación actualice la UI
        self.simulation.ui_callback = self._on_simulation_update
        
        # Variables de control
        self.simulation_mode = tk.StringVar(value="naive")
        self.speed_factor = tk.DoubleVar(value=1.0)
        self.seed_value = tk.StringVar(value="")
        self.detailed_logs = tk.BooleanVar(value=False)
        self.synchronize_start = tk.BooleanVar(value=False)
        
        self.animation_id = None
        self.last_update_time = time.time()
        
        # Crear UI
        self._create_widgets()
        
        # Iniciar loop de actualización
        self._update_loop()
    
    def _create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Panel superior con controles
        top_panel = ttk.Frame(self.root)
        top_panel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Sección de modo de simulación
        mode_frame = ttk.LabelFrame(top_panel, text="Modo de Simulación", padding=5)
        mode_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(mode_frame, text="Ingenuo (con Deadlock)", 
                       variable=self.simulation_mode, value="naive",
                       state=tk.DISABLED).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Corregido (sin Deadlock)", 
                       variable=self.simulation_mode, value="corrected",
                       state=tk.DISABLED).pack(anchor=tk.W)
        
        # Sección de controles
        control_frame = ttk.LabelFrame(top_panel, text="Controles", padding=5)
        control_frame.pack(side=tk.LEFT, padx=5)
        
        self.btn_start = ttk.Button(control_frame, text="Iniciar", command=self._on_start)
        self.btn_start.pack(side=tk.LEFT, padx=2)
        
        self.btn_pause = ttk.Button(control_frame, text="Pausar", command=self._on_pause, 
                                    state=tk.DISABLED)
        self.btn_pause.pack(side=tk.LEFT, padx=2)
        
        self.btn_resume = ttk.Button(control_frame, text="Reanudar", command=self._on_resume, 
                                     state=tk.DISABLED)
        self.btn_resume.pack(side=tk.LEFT, padx=2)
        
        self.btn_reset = ttk.Button(control_frame, text="Reiniciar", command=self._on_reset)
        self.btn_reset.pack(side=tk.LEFT, padx=2)
        
        self.btn_stop = ttk.Button(control_frame, text="Detener", command=self._on_stop,
                                   state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=2)
        
        # Sección de configuración
        config_frame = ttk.LabelFrame(top_panel, text="Configuración", padding=5)
        config_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(config_frame, text="Velocidad:").pack(side=tk.LEFT, padx=2)
        speed_scale = ttk.Scale(config_frame, from_=0.1, to=3.0, 
                               variable=self.speed_factor, orient=tk.HORIZONTAL,
                               length=100)
        speed_scale.pack(side=tk.LEFT, padx=2)
        self.speed_label = ttk.Label(config_frame, text="1.0x", width=5)
        self.speed_label.pack(side=tk.LEFT, padx=2)
        
        ttk.Checkbutton(config_frame, text="Inicio sincronizado", 
                       variable=self.synchronize_start).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(config_frame, text="Logs detallados", 
                       variable=self.detailed_logs).pack(side=tk.LEFT, padx=5)
        
        # Panel principal con canvas y panel lateral
        main_panel = ttk.Frame(self.root)
        main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas para visualización
        canvas_frame = ttk.Frame(main_panel)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(canvas_frame, text="Mesa Circular", font=("Arial", 12, "bold")).pack()
        
        self.canvas = tk.Canvas(canvas_frame, bg=COLORS["background"], 
                               width=600, height=600, highlightthickness=1)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Panel lateral con estadísticas y eventos
        right_panel = ttk.Frame(main_panel, width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)
        right_panel.pack_propagate(False)
        
        # Estadísticas
        stats_frame = ttk.LabelFrame(right_panel, text="Estadísticas", padding=5)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=10, width=40, state=tk.DISABLED,
                                 font=("Courier", 9))
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Eventos recientes
        events_frame = ttk.LabelFrame(right_panel, text="Eventos Recientes", padding=5)
        events_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(events_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.events_text = tk.Text(events_frame, height=15, width=40, 
                                  yscrollcommand=scrollbar.set,
                                  font=("Courier", 8), state=tk.DISABLED)
        self.events_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.events_text.yview)
        
        # Barra de estado
        self.status_var = tk.StringVar(value="Listo")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _on_start(self):
        """Inicia la simulación"""
        self.simulation.set_simulation_speeds(
            0.5 / self.speed_factor,
            2.0 / self.speed_factor,
            0.5 / self.speed_factor,
            1.5 / self.speed_factor
        )
        self.simulation.start(synchronize_start=self.synchronize_start.get())
        
        self.btn_start.config(state=tk.DISABLED)
        self.btn_pause.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_resume.config(state=tk.DISABLED)
        
        self.status_var.set("Simulación en ejecución...")
    
    def _on_pause(self):
        """Pausa la simulación"""
        self.simulation.pause()
        
        self.btn_pause.config(state=tk.DISABLED)
        self.btn_resume.config(state=tk.NORMAL)
        
        self.status_var.set("Simulación pausada")
    
    def _on_resume(self):
        """Reanuda la simulación"""
        self.simulation.resume()
        
        self.btn_pause.config(state=tk.NORMAL)
        self.btn_resume.config(state=tk.DISABLED)
        
        self.status_var.set("Simulación en ejecución...")
    
    def _on_reset(self):
        """Reinicia la simulación"""
        self.simulation.reset()
        
        self.btn_start.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED)
        self.btn_resume.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.DISABLED)
        
        self._clear_ui()
        self.status_var.set("Simulación reiniciada")
    
    def _on_stop(self):
        """Detiene la simulación"""
        self.simulation.stop()
        
        self.btn_start.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED)
        self.btn_resume.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.DISABLED)
        
        self.status_var.set("Simulación detenida")
    
    def _on_simulation_update(self, event_type):
        """Callback desde la simulación para actualizar la UI"""
        # La actualización será hecha por el loop de animación
        pass
    
    def _update_loop(self):
        """Loop principal de actualización de la UI"""
        try:
            # Actualizar velocidad
            self.speed_label.config(text=f"{self.speed_factor.get():.1f}x")
            
            # Actualizar visualización
            self._draw_philosophers_and_forks()
            self._update_statistics()
            self._update_events()
            
        except Exception as e:
            print(f"Error en update loop: {e}")
        
        # Programar siguiente actualización
        self.animation_id = self.root.after(100, self._update_loop)
    
    def _draw_philosophers_and_forks(self):
        """Dibuja los filósofos y tenedores en el canvas"""
        self.canvas.delete("all")
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            width = 600
            height = 600
        
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 60
        
        # Dibujar mesa
        self.canvas.create_oval(
            center_x - radius - 20, center_y - radius - 20,
            center_x + radius + 20, center_y + radius + 20,
            outline="#888888", width=2, fill="#F5F5F5"
        )
        
        # Dibujar filósofos y tenedores
        for i in range(5):
            angle = (i * 2 * math.pi) / 5 - math.pi / 2
            
            # Posición del filósofo
            phil_x = center_x + radius * math.cos(angle)
            phil_y = center_y + radius * math.sin(angle)
            
            # Obtener estado del filósofo
            philosopher_state = self.simulation.get_philosopher_state(i)
            
            # Color según estado
            if philosopher_state == PhilosopherState.THINKING:
                color = COLORS["thinking"]
            elif philosopher_state == PhilosopherState.HUNGRY:
                color = COLORS["hungry"]
            elif philosopher_state == PhilosopherState.EATING:
                color = COLORS["eating"]
            elif philosopher_state == PhilosopherState.WAITING:
                color = COLORS["waiting"]
            elif philosopher_state == PhilosopherState.DEADLOCK:
                color = COLORS["deadlock"]
            else:
                color = "#CCCCCC"
            
            # Dibujar filósofo (círculo)
            phil_size = 30
            self.canvas.create_oval(
                phil_x - phil_size, phil_y - phil_size,
                phil_x + phil_size, phil_y + phil_size,
                fill=color, outline="black", width=2
            )
            
            # Etiqueta del filósofo
            self.canvas.create_text(
                phil_x, phil_y,
                text=f"F{i}\n{philosopher_state.value[:4]}",
                font=("Arial", 9, "bold"), fill="white"
            )
            
            # Estadísticas del filósofo debajo
            stats = self.simulation.get_statistics()[i]
            self.canvas.create_text(
                phil_x, phil_y + 50,
                text=f"Comidas: {stats.meals_eaten}",
                font=("Arial", 8), fill="black"
            )
            
            # Posición del tenedor entre este filósofo y el siguiente
            next_angle = ((i + 0.5) * 2 * math.pi) / 5 - math.pi / 2
            fork_x = center_x + (radius - 40) * math.cos(next_angle)
            fork_y = center_y + (radius - 40) * math.sin(next_angle)
            
            # Obtener estado del tenedor
            fork_state = self.simulation.get_fork_state(i)
            
            if fork_state["is_free"]:
                fork_color = COLORS["free_fork"]
                fork_label = "Libre"
            else:
                fork_color = COLORS["taken_fork"]
                fork_label = f"F{fork_state['owner_id']}"
            
            # Dibujar tenedor (rectángulo)
            fork_size = 12
            self.canvas.create_rectangle(
                fork_x - fork_size, fork_y - fork_size,
                fork_x + fork_size, fork_y + fork_size,
                fill=fork_color, outline="black", width=2
            )
            
            self.canvas.create_text(
                fork_x, fork_y,
                text="T",
                font=("Arial", 8, "bold"), fill="white"
            )
        
        # Indicador de deadlock
        if self.simulation.is_in_deadlock():
            self.canvas.create_text(
                center_x, 30,
                text="⚠️ DEADLOCK DETECTADO ⚠️",
                font=("Arial", 14, "bold"), fill=COLORS["deadlock"]
            )
    
    def _update_statistics(self):
        """Actualiza el panel de estadísticas"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        stats_all = self.simulation.get_statistics()
        
        # Mostrar estadísticas
        text = "ESTADÍSTICAS POR FILÓSOFO\n"
        text += "=" * 38 + "\n\n"
        
        total_meals = 0
        max_wait = 0.0
        total_wait = 0.0
        
        for i, stats in enumerate(stats_all):
            total_meals += stats.meals_eaten
            total_wait += stats.total_wait_time
            max_wait = max(max_wait, stats.max_wait_time)
            
            text += f"Filósofo {i}:\n"
            text += f"  Comidas: {stats.meals_eaten}\n"
            text += f"  Espera max: {stats.max_wait_time:.2f}s\n"
            text += f"  Espera total: {stats.total_wait_time:.2f}s\n"
            text += "\n"
        
        text += "=" * 38 + "\n"
        text += f"Total comidas: {total_meals}\n"
        text += f"Espera máxima: {max_wait:.2f}s\n"
        text += f"Espera total: {total_wait:.2f}s\n"
        
        if self.simulation.is_in_deadlock():
            text += "\n⚠️ DEADLOCK ACTIVO\n"
        
        self.stats_text.insert(tk.END, text)
        self.stats_text.config(state=tk.DISABLED)
    
    def _update_events(self):
        """Actualiza el panel de eventos"""
        self.events_text.config(state=tk.NORMAL)
        self.events_text.delete(1.0, tk.END)
        
        events = self.simulation.get_recent_events(20)
        
        for event in events:
            if self.detailed_logs or event.event_type in ["DEADLOCK", "EATING", "HUNGRY"]:
                self.events_text.insert(tk.END, str(event) + "\n")
        
        self.events_text.see(tk.END)
        self.events_text.config(state=tk.DISABLED)
    
    def _clear_ui(self):
        """Limpia la interfaz"""
        self.canvas.delete("all")
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.config(state=tk.DISABLED)
        self.events_text.config(state=tk.NORMAL)
        self.events_text.delete(1.0, tk.END)
        self.events_text.config(state=tk.DISABLED)
    
    def on_closing(self):
        """Se llama al cerrar la aplicación"""
        self.simulation.stop()
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
        self.root.destroy()
