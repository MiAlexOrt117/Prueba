"""
Clase de simulación con algoritmo corregido (sin deadlock ni starvation).
Usa un monitor con Condition Variables y una cola FIFO de fairness.
"""
import threading
import time
from collections import deque
from fork import Fork
from philosopher import CorrectedPhilosopher
from utils import PhilosopherState, Event


class SimulationCorrected:
    """
    Simulación del problema de los filósofos comensales con algoritmo corregido.
    
    Usa un Monitor con:
    - Mutex (Lock) para exclusión mutua
    - Condition Variable para sincronización
    - Cola FIFO para fairness
    - Garantía de que ambos tenedores se toman atómicamente
    
    Esto elimina:
    - Deadlock: un filósofo no retiene un tenedor mientras espera el otro
    - Starvation: la cola FIFO garantiza que eventualmente todos serán atendidos
    """
    
    def __init__(self, ui_callback=None):
        """
        Inicializa la simulación.
        
        Args:
            ui_callback: Función para actualizar la interfaz gráfica
        """
        self.ui_callback = ui_callback
        self.is_running = False
        self.is_paused = False
        self.should_stop = False
        
        # Tiempos de simulación
        self.thinking_time_min = 0.5
        self.thinking_time_max = 2.0
        self.eating_time_min = 0.5
        self.eating_time_max = 1.5
        
        # Crear tenedores
        self.forks = [Fork(i) for i in range(5)]
        
        # Crear filósofos
        self.philosophers = []
        for i in range(5):
            left_fork = self.forks[i]
            right_fork = self.forks[(i + 1) % 5]
            philosopher = CorrectedPhilosopher(i, left_fork, right_fork, self)
            self.philosophers.append(philosopher)
        
        # Monitor (Mutex + Condition Variable)
        self.monitor_lock = threading.Lock()
        self.monitor_condition = threading.Condition(self.monitor_lock)
        
        # Estado de los filósofos visto por el monitor
        self.fork_state = [False] * 5  # False = libre, True = tomado
        self.philosopher_states = [PhilosopherState.THINKING] * 5
        
        # Cola FIFO para fairness
        self.waiting_queue = deque()
        
        # Registro de eventos
        self.events = deque(maxlen=100)
        self.start_time = None
        self.event_lock = threading.Lock()
    
    def log_event(self, philosopher_id, event_type, message):
        """Registra un evento en el log"""
        if self.start_time is None:
            self.start_time = time.time()
        
        timestamp = time.time() - self.start_time
        event = Event(timestamp, philosopher_id, event_type, message)
        
        with self.event_lock:
            self.events.append(event)
        
        if self.ui_callback:
            try:
                self.ui_callback("update")
            except:
                pass
    
    def acquire_forks(self, philosopher_id):
        """
        Adquiere ambos tenedores de forma atómica usando el monitor.
        
        Esta es la pieza clave del algoritmo corregido.
        El filósofo NO debe ser interrumpido entre tomar el tenedor izquierdo
        y el derecho.
        
        Args:
            philosopher_id: ID del filósofo que solicita los tenedores
        """
        with self.monitor_condition:
            # Agregar a la cola de espera
            self.waiting_queue.append(philosopher_id)
            self.philosophers[philosopher_id].set_state(PhilosopherState.WAITING)
            
            self.log_event(
                philosopher_id,
                "QUEUE",
                f"Entra en cola. Posición: {len(self.waiting_queue)}"
            )
            
            # Esperar hasta que:
            # 1. Sea el primero en la cola
            # 2. Ambos tenedores estén libres
            while (self.waiting_queue[0] != philosopher_id or
                   self.fork_state[philosopher_id] or
                   self.fork_state[(philosopher_id + 4) % 5]):
                
                self.log_event(
                    philosopher_id,
                    "WAIT",
                    "Esperando en el monitor por tenedores"
                )
                
                self.monitor_condition.wait()
            
            # Tomar ambos tenedores (operación atómica)
            left_fork_id = philosopher_id
            right_fork_id = (philosopher_id + 4) % 5
            
            self.fork_state[left_fork_id] = True
            self.fork_state[right_fork_id] = True
            self.philosopher_states[philosopher_id] = PhilosopherState.EATING
            
            # Actualizar objetos Fork también
            self.forks[left_fork_id].state = True
            self.forks[left_fork_id].owner_id = philosopher_id
            self.forks[right_fork_id].state = True
            self.forks[right_fork_id].owner_id = philosopher_id
            
            # Salir de la cola
            self.waiting_queue.popleft()
            
            self.log_event(
                philosopher_id,
                "GRABBED_BOTH",
                f"Tomó ambos tenedores (sale de cola)"
            )
    
    def release_forks(self, philosopher_id):
        """
        Suelta ambos tenedores y notifica a otros filósofos en espera.
        
        Args:
            philosopher_id: ID del filósofo que libera los tenedores
        """
        with self.monitor_condition:
            left_fork_id = philosopher_id
            right_fork_id = (philosopher_id + 4) % 5
            
            # Liberar tenedores
            self.fork_state[left_fork_id] = False
            self.fork_state[right_fork_id] = False
            self.philosopher_states[philosopher_id] = PhilosopherState.THINKING
            
            # Actualizar objetos Fork
            self.forks[left_fork_id].state = False
            self.forks[left_fork_id].owner_id = None
            self.forks[right_fork_id].state = False
            self.forks[right_fork_id].owner_id = None
            
            self.log_event(
                philosopher_id,
                "RELEASED",
                "Liberó ambos tenedores"
            )
            
            # Notificar a todos (notify_all para despertar a los en espera)
            self.monitor_condition.notify_all()
    
    def start(self, synchronize_start=False):
        """Inicia la simulación"""
        if self.is_running:
            return
        
        self.is_running = True
        self.should_stop = False
        self.start_time = time.time()
        self.events.clear()
        self.waiting_queue.clear()
        
        # Reinicializar estados del monitor
        self.fork_state = [False] * 5
        self.philosopher_states = [PhilosopherState.THINKING] * 5
        
        # Iniciar hilos de filósofos
        for philosopher in self.philosophers:
            philosopher.should_stop = False
            philosopher.is_paused = False
            philosopher.statistics = type(philosopher.statistics)(philosopher.philosopher_id)
            philosopher.start()
        
        self.log_event(-1, "SYSTEM", "Simulación iniciada (modo corregido)")
    
    def pause(self):
        """Pausa la simulación"""
        if not self.is_running or self.is_paused:
            return
        
        self.is_paused = True
        for philosopher in self.philosophers:
            philosopher.pause()
        
        self.log_event(-1, "SYSTEM", "Simulación pausada")
    
    def resume(self):
        """Reanuda la simulación pausada"""
        if not self.is_running or not self.is_paused:
            return
        
        self.is_paused = False
        for philosopher in self.philosophers:
            philosopher.resume()
        
        self.log_event(-1, "SYSTEM", "Simulación reanudada")
    
    def stop(self):
        """Detiene completamente la simulación"""
        if not self.is_running:
            return
        
        self.should_stop = True
        
        for philosopher in self.philosophers:
            philosopher.stop()
        
        for philosopher in self.philosophers:
            philosopher.join(timeout=2.0)
        
        self.is_running = False
        self.log_event(-1, "SYSTEM", "Simulación detenida")
    
    def reset(self):
        """Reinicia la simulación desde cero"""
        self.stop()
        time.sleep(0.5)
        
        # Reinicializar
        self.forks = [Fork(i) for i in range(5)]
        self.philosophers = []
        for i in range(5):
            left_fork = self.forks[i]
            right_fork = self.forks[(i + 1) % 5]
            philosopher = CorrectedPhilosopher(i, left_fork, right_fork, self)
            self.philosophers.append(philosopher)
        
        self.events.clear()
        self.waiting_queue.clear()
        self.fork_state = [False] * 5
        self.philosopher_states = [PhilosopherState.THINKING] * 5
        self.start_time = None
    
    def get_philosopher_state(self, philosopher_id):
        """Obtiene el estado actual de un filósofo"""
        return self.philosophers[philosopher_id].get_state()
    
    def get_fork_state(self, fork_id):
        """Obtiene el estado actual de un tenedor"""
        fork = self.forks[fork_id]
        return {
            "is_free": not self.fork_state[fork_id],
            "owner_id": fork.owner_id
        }
    
    def get_statistics(self):
        """Obtiene estadísticas de todos los filósofos"""
        return [p.statistics for p in self.philosophers]
    
    def get_recent_events(self, count=10):
        """Obtiene los últimos N eventos"""
        with self.event_lock:
            return list(self.events)[-count:]
    
    def get_queue_position(self, philosopher_id):
        """Retorna la posición del filósofo en la cola (1-indexed), o 0 si no está"""
        try:
            return list(self.waiting_queue).index(philosopher_id) + 1
        except ValueError:
            return 0
    
    def is_in_deadlock(self):
        """Retorna False siempre (no hay deadlock)"""
        return False
    
    def set_simulation_speeds(self, thinking_min, thinking_max, eating_min, eating_max):
        """Ajusta los tiempos de simulación"""
        self.thinking_time_min = thinking_min
        self.thinking_time_max = thinking_max
        self.eating_time_min = eating_min
        self.eating_time_max = eating_max
