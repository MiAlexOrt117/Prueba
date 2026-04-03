"""
Utilidades, constantes y enumeraciones para la simulación.
"""
from enum import Enum
import time

# ============================================================================
# Enumeraciones para estados
# ============================================================================

class PhilosopherState(Enum):
    """Estados posibles de un filósofo"""
    THINKING = "Pensando"
    HUNGRY = "Hambriento"
    EATING = "Comiendo"
    WAITING = "Esperando"
    DEADLOCK = "Deadlock"


class ForkState(Enum):
    """Estados posibles de un tenedor"""
    FREE = "Libre"
    TAKEN = "Tomado"


# ============================================================================
# Constantes de simulación
# ============================================================================

NUM_PHILOSOPHERS = 5
NUM_FORKS = 5

# Tiempos por defecto (en segundos)
DEFAULT_THINKING_TIME_MIN = 0.5
DEFAULT_THINKING_TIME_MAX = 2.0

DEFAULT_EATING_TIME_MIN = 0.5
DEFAULT_EATING_TIME_MAX = 1.5

DEFAULT_FORK_GRAB_TIME = 0.05  # Tiempo para tomar un tenedor

# Umbral para detectar deadlock (segundos sin progreso)
DEADLOCK_DETECTION_THRESHOLD = 3.0

# ============================================================================
# Colores para la interfaz
# ============================================================================

COLORS = {
    "thinking": "#4A90E2",      # Azul
    "hungry": "#F5D547",         # Amarillo
    "eating": "#7ED321",         # Verde
    "waiting": "#F5D547",        # Amarillo (igual que hungry)
    "deadlock": "#D0021B",       # Rojo
    "free_fork": "#B8B8B8",      # Gris
    "taken_fork": "#D0021B",     # Rojo
    "background": "#FFFFFF",     # Blanco
    "text": "#000000",           # Negro
    "panel_bg": "#F0F0F0",       # Gris claro
}

# ============================================================================
# Clases auxiliares
# ============================================================================

class Statistics:
    """Estadísticas por filósofo"""
    def __init__(self, philosopher_id):
        self.philosopher_id = philosopher_id
        self.meals_eaten = 0
        self.total_wait_time = 0.0
        self.max_wait_time = 0.0
        self.failed_attempts = 0
        self.start_wait_time = None
    
    def start_waiting(self):
        """Marca el inicio de una espera"""
        self.start_wait_time = time.time()
    
    def end_waiting(self):
        """Marca el fin de una espera y actualiza estadísticas"""
        if self.start_wait_time is not None:
            wait_time = time.time() - self.start_wait_time
            self.total_wait_time += wait_time
            self.max_wait_time = max(self.max_wait_time, wait_time)
            self.start_wait_time = None
    
    def record_meal(self):
        """Registra una comida"""
        self.meals_eaten += 1
    
    def record_failed_attempt(self):
        """Registra un intento fallido"""
        self.failed_attempts += 1


class Event:
    """Evento del sistema para logging"""
    def __init__(self, timestamp, philosopher_id, event_type, message):
        self.timestamp = timestamp
        self.philosopher_id = philosopher_id
        self.event_type = event_type  # "GRAB", "RELEASE", "EATING", "THINKING", etc.
        self.message = message
    
    def __str__(self):
        return f"[{self.timestamp:.2f}s] Filósofo {self.philosopher_id}: {self.message}"
