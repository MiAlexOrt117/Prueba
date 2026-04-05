"""
Interfaz gráfica en Tkinter para la simulación de los filósofos comensales.
"""
import math
import tkinter as tk
from tkinter import messagebox, ttk

from simulation_corrected import SimulationCorrected
from simulation_naive import SimulationNaive
from utils import COLORS, PhilosopherState


STATE_COLORS = {
    PhilosopherState.THINKING: COLORS["thinking"],
    PhilosopherState.HUNGRY: COLORS["hungry"],
    PhilosopherState.WAITING: COLORS["waiting"],
    PhilosopherState.TOOK_LEFT: COLORS["took_left"],
    PhilosopherState.TOOK_RIGHT: COLORS["took_right"],
    PhilosopherState.HAS_BOTH: COLORS["has_both"],
    PhilosopherState.EATING: COLORS["eating"],
    PhilosopherState.DEADLOCK: COLORS["deadlock"],
}


class DiningPhilosophersUI:
    """Interfaz gráfica principal."""

    def __init__(self, root):
        self.root = root
        self.root.title("Problema de los Filósofos Comensales")
        self.root.geometry("1500x950")

        self.current_mode = tk.StringVar(value="Sin iniciar")
        self.system_state = tk.StringVar(value="Listo")
        self.deadlock_state = tk.StringVar(value="No")
        self.speed_factor = tk.DoubleVar(value=1.0)
        self.seed_value = tk.StringVar(value="123")
        self.detailed_logs = tk.BooleanVar(value=True)
        self.synchronize_start = tk.BooleanVar(value=True)
        self.high_contention = tk.BooleanVar(value=True)

        self.simulation = None
        self.animation_id = None
        self._create_widgets()
        self._load_simulation("naive")
        self._update_loop()

    def _create_widgets(self):
        top_panel = ttk.Frame(self.root)
        top_panel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        mode_frame = ttk.LabelFrame(top_panel, text="Inicio de Simulación", padding=8)
        mode_frame.pack(side=tk.LEFT, padx=5)

        self.btn_start_naive = ttk.Button(
            mode_frame,
            text="Iniciar Modo Ingenuo",
            command=lambda: self._start_mode("naive"),
        )
        self.btn_start_naive.pack(side=tk.LEFT, padx=3)

        self.btn_start_corrected = ttk.Button(
            mode_frame,
            text="Iniciar Modo Corregido",
            command=lambda: self._start_mode("corrected"),
        )
        self.btn_start_corrected.pack(side=tk.LEFT, padx=3)

        control_frame = ttk.LabelFrame(top_panel, text="Controles", padding=8)
        control_frame.pack(side=tk.LEFT, padx=5)

        self.btn_pause = ttk.Button(control_frame, text="Pausar", command=self._on_pause, state=tk.DISABLED)
        self.btn_pause.pack(side=tk.LEFT, padx=2)
        self.btn_resume = ttk.Button(control_frame, text="Reanudar", command=self._on_resume, state=tk.DISABLED)
        self.btn_resume.pack(side=tk.LEFT, padx=2)
        self.btn_reset = ttk.Button(control_frame, text="Reiniciar", command=self._on_reset)
        self.btn_reset.pack(side=tk.LEFT, padx=2)
        self.btn_stop = ttk.Button(control_frame, text="Detener", command=self._on_stop, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=2)

        config_frame = ttk.LabelFrame(top_panel, text="Configuración", padding=8)
        config_frame.pack(side=tk.LEFT, padx=5)

        ttk.Label(config_frame, text="Velocidad").grid(row=0, column=0, sticky="w")
        ttk.Scale(
            config_frame,
            from_=0.1,
            to=3.0,
            variable=self.speed_factor,
            orient=tk.HORIZONTAL,
            length=100,
        ).grid(row=0, column=1, padx=4)
        self.speed_label = ttk.Label(config_frame, text="1.0x", width=6)
        self.speed_label.grid(row=0, column=2, padx=4)

        ttk.Label(config_frame, text="Semilla").grid(row=1, column=0, sticky="w")
        ttk.Entry(config_frame, textvariable=self.seed_value, width=10).grid(row=1, column=1, sticky="w", padx=4)

        ttk.Checkbutton(
            config_frame,
            text="Inicio sincronizado",
            variable=self.synchronize_start,
        ).grid(row=0, column=3, padx=6, sticky="w")
        ttk.Checkbutton(
            config_frame,
            text="Alta contención",
            variable=self.high_contention,
        ).grid(row=1, column=3, padx=6, sticky="w")
        ttk.Checkbutton(
            config_frame,
            text="Logs detallados",
            variable=self.detailed_logs,
        ).grid(row=0, column=4, padx=6, sticky="w")

        summary_frame = ttk.LabelFrame(top_panel, text="Estado Global", padding=8)
        summary_frame.pack(side=tk.LEFT, padx=5)

        ttk.Label(summary_frame, text="Modo actual:").grid(row=0, column=0, sticky="w")
        ttk.Label(summary_frame, textvariable=self.current_mode).grid(row=0, column=1, sticky="w")
        ttk.Label(summary_frame, text="Sistema:").grid(row=1, column=0, sticky="w")
        ttk.Label(summary_frame, textvariable=self.system_state).grid(row=1, column=1, sticky="w")
        ttk.Label(summary_frame, text="Deadlock:").grid(row=2, column=0, sticky="w")
        ttk.Label(summary_frame, textvariable=self.deadlock_state).grid(row=2, column=1, sticky="w")

        main_panel = ttk.Frame(self.root)
        main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas_frame = ttk.Frame(main_panel)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(canvas_frame, text="Mesa Circular", font=("Arial", 12, "bold")).pack()

        self.canvas = tk.Canvas(
            canvas_frame,
            bg=COLORS["background"],
            width=850,
            height=700,
            highlightthickness=1,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        right_panel = ttk.Frame(main_panel, width=420)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)
        right_panel.pack_propagate(False)

        legend_frame = ttk.LabelFrame(right_panel, text="Leyenda", padding=5)
        legend_frame.pack(fill=tk.X, pady=5)
        legend_text = (
            "Pensando=azul | Hambriento=naranja | Esperando=amarillo\n"
            "Tomó izq.=ocre | Tiene ambos=turquesa | Comiendo=verde | Deadlock=rojo"
        )
        ttk.Label(legend_frame, text=legend_text, justify=tk.LEFT).pack(anchor=tk.W)

        stats_frame = ttk.LabelFrame(right_panel, text="Estadísticas", padding=5)
        stats_frame.pack(fill=tk.X, pady=5)
        self.stats_text = tk.Text(stats_frame, height=16, width=46, state=tk.DISABLED, font=("Courier New", 9))
        self.stats_text.pack(fill=tk.BOTH, expand=True)

        events_frame = ttk.LabelFrame(right_panel, text="Eventos Recientes", padding=5)
        events_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        scrollbar = ttk.Scrollbar(events_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.events_text = tk.Text(
            events_frame,
            height=20,
            width=46,
            yscrollcommand=scrollbar.set,
            font=("Courier New", 8),
            state=tk.DISABLED,
        )
        self.events_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.events_text.yview)

        self.status_var = tk.StringVar(value="Listo para iniciar una demostración.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _load_simulation(self, mode):
        if self.simulation is not None:
            self.simulation.stop()

        if mode == "naive":
            self.simulation = SimulationNaive(ui_callback=self._on_simulation_update)
        else:
            self.simulation = SimulationCorrected(ui_callback=self._on_simulation_update)

        self.current_mode.set(self.simulation.get_mode_name())
        self.deadlock_state.set("No")
        self.system_state.set(self.simulation.get_system_status())

    def _parse_seed(self):
        value = self.seed_value.get().strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            messagebox.showerror("Semilla inválida", "La semilla debe ser un entero.")
            return None

    def _apply_speed(self):
        factor = self.speed_factor.get()
        self.simulation.set_simulation_speeds(
            0.5 / factor,
            2.0 / factor,
            0.5 / factor,
            1.5 / factor,
        )

    def _start_mode(self, mode):
        seed = self._parse_seed()
        if self.seed_value.get().strip() and seed is None:
            return

        self._load_simulation(mode)
        self.simulation.set_run_options(
            random_seed=seed,
            high_contention=self.high_contention.get(),
        )
        self._apply_speed()
        self.simulation.start(synchronize_start=self.synchronize_start.get())

        self.btn_pause.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_resume.config(state=tk.DISABLED)
        self.status_var.set(f"Simulación {self.simulation.get_mode_name()} en ejecución.")

    def _on_pause(self):
        if self.simulation is None:
            return
        self.simulation.pause()
        self.btn_pause.config(state=tk.DISABLED)
        self.btn_resume.config(state=tk.NORMAL)
        self.status_var.set("Simulación pausada.")

    def _on_resume(self):
        if self.simulation is None:
            return
        self._apply_speed()
        self.simulation.resume()
        self.btn_pause.config(state=tk.NORMAL)
        self.btn_resume.config(state=tk.DISABLED)
        self.status_var.set("Simulación reanudada.")

    def _on_reset(self):
        if self.simulation is None:
            return
        current_mode = "naive" if self.simulation.get_mode_name() == "Ingenuo" else "corrected"
        self._load_simulation(current_mode)
        self.btn_pause.config(state=tk.DISABLED)
        self.btn_resume.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.DISABLED)
        self._clear_ui()
        self.status_var.set("Simulación reiniciada.")

    def _on_stop(self):
        if self.simulation is None:
            return
        self.simulation.stop()
        self.btn_pause.config(state=tk.DISABLED)
        self.btn_resume.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.DISABLED)
        self.system_state.set(self.simulation.get_system_status())
        self.deadlock_state.set("No")
        self.status_var.set("Simulación detenida.")

    def _on_simulation_update(self, event_type):
        pass

    def _update_loop(self):
        try:
            self.speed_label.config(text=f"{self.speed_factor.get():.1f}x")
            if self.simulation is not None:
                self.system_state.set(self.simulation.get_system_status())
                self.deadlock_state.set("Sí" if self.simulation.is_in_deadlock() else "No")
                self._draw_philosophers_and_forks()
                self._update_statistics()
                self._update_events()
        except Exception as exc:
            print(f"Error en update loop: {exc}")

        self.animation_id = self.root.after(100, self._update_loop)

    def _draw_philosophers_and_forks(self):
        self.canvas.delete("all")

        width = max(self.canvas.winfo_width(), 850)
        height = max(self.canvas.winfo_height(), 700)
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 110

        self.canvas.create_oval(
            center_x - radius - 40,
            center_y - radius - 40,
            center_x + radius + 40,
            center_y + radius + 40,
            outline="#888888",
            width=2,
            fill="#F7F7F7",
        )
        self.canvas.create_text(center_x, center_y, text="Mesa", font=("Arial", 18, "bold"))

        for i in range(5):
            angle = (i * 2 * math.pi) / 5 - math.pi / 2
            phil_x = center_x + radius * math.cos(angle)
            phil_y = center_y + radius * math.sin(angle)

            philosopher_state = self.simulation.get_philosopher_state(i)
            color = STATE_COLORS.get(philosopher_state, "#CCCCCC")

            self.canvas.create_oval(
                phil_x - 42,
                phil_y - 42,
                phil_x + 42,
                phil_y + 42,
                fill=color,
                outline="black",
                width=2,
            )
            self.canvas.create_text(
                phil_x,
                phil_y - 10,
                text=f"Filósofo {i}",
                font=("Arial", 10, "bold"),
                fill="white",
            )
            self.canvas.create_text(
                phil_x,
                phil_y + 12,
                text=philosopher_state.value,
                font=("Arial", 9, "bold"),
                fill="white",
            )

            stats = self.simulation.get_statistics()[i]
            self.canvas.create_text(
                phil_x,
                phil_y + 64,
                text=f"Comidas: {stats.meals_eaten} | Espera actual: {stats.get_current_wait_time():.1f}s",
                font=("Arial", 8),
                fill="black",
            )

            fork_angle = ((i + 0.5) * 2 * math.pi) / 5 - math.pi / 2
            fork_x = center_x + (radius - 55) * math.cos(fork_angle)
            fork_y = center_y + (radius - 55) * math.sin(fork_angle)
            fork_state = self.simulation.get_fork_state(i)
            fork_color = COLORS["free_fork"] if fork_state["is_free"] else COLORS["taken_fork"]

            self.canvas.create_rectangle(
                fork_x - 16,
                fork_y - 22,
                fork_x + 16,
                fork_y + 22,
                fill=fork_color,
                outline=COLORS["highlight_fork"],
                width=2,
            )
            self.canvas.create_text(
                fork_x,
                fork_y - 6,
                text=f"T{i}",
                font=("Arial", 8, "bold"),
                fill="white",
            )
            self.canvas.create_text(
                fork_x,
                fork_y + 8,
                text=fork_state["label"],
                font=("Arial", 8, "bold"),
                fill="white",
            )

        mode_text = f"Modo actual: {self.simulation.get_mode_name()} | Estado: {self.simulation.get_system_status()}"
        self.canvas.create_text(center_x, 28, text=mode_text, font=("Arial", 13, "bold"), fill="black")

        if self.simulation.is_in_deadlock():
            timestamp = self.simulation.get_deadlock_timestamp()
            deadlock_text = "DEADLOCK DETECTADO"
            if timestamp is not None:
                deadlock_text += f" en t={timestamp:.2f}s"
            self.canvas.create_text(
                center_x,
                55,
                text=deadlock_text,
                font=("Arial", 15, "bold"),
                fill=COLORS["deadlock"],
            )

    def _update_statistics(self):
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)

        stats_all = self.simulation.get_statistics()
        total_meals = sum(stats.meals_eaten for stats in stats_all)
        max_wait = max((stats.max_wait_time for stats in stats_all), default=0.0)
        lines = [
            "ESTADÍSTICAS POR FILÓSOFO",
            "=" * 40,
        ]

        for i, stats in enumerate(stats_all):
            queue_info = ""
            if hasattr(self.simulation, "get_queue_position"):
                position = self.simulation.get_queue_position(i)
                queue_info = f" | Cola: {position}" if position else ""

            lines.append(
                f"F{i}: comidas={stats.meals_eaten:3d} | espera actual={stats.get_current_wait_time():5.2f}s{queue_info}"
            )
            lines.append(
                f"    espera total={stats.total_wait_time:5.2f}s | espera max={stats.max_wait_time:5.2f}s"
            )

        lines.extend(
            [
                "=" * 40,
                f"Total de comidas: {total_meals}",
                f"Espera máxima observada: {max_wait:.2f}s",
                f"Modo: {self.simulation.get_mode_name()}",
                f"Estado global: {self.simulation.get_system_status()}",
                f"Deadlock: {'Sí' if self.simulation.is_in_deadlock() else 'No'}",
            ]
        )

        self.stats_text.insert(tk.END, "\n".join(lines))
        self.stats_text.config(state=tk.DISABLED)

    def _update_events(self):
        self.events_text.config(state=tk.NORMAL)
        self.events_text.delete(1.0, tk.END)

        important = {"SYSTEM", "DEADLOCK", "EATING", "HUNGRY", "GRAB_LEFT", "GRAB_RIGHT", "GRABBED_BOTH", "RELEASED"}
        for event in self.simulation.get_recent_events(30):
            if self.detailed_logs.get() or event.event_type in important:
                self.events_text.insert(tk.END, f"{event}\n")

        self.events_text.see(tk.END)
        self.events_text.config(state=tk.DISABLED)

    def _clear_ui(self):
        self.canvas.delete("all")
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.config(state=tk.DISABLED)
        self.events_text.config(state=tk.NORMAL)
        self.events_text.delete(1.0, tk.END)
        self.events_text.config(state=tk.DISABLED)

    def on_closing(self):
        if self.simulation is not None:
            self.simulation.stop()
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
        self.root.destroy()
