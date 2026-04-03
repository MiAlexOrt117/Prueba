"""
Clase de simulación con algoritmo ingenuo (propenso a deadlock).
"""
import threading
import time
from collections import deque
from fork import Fork
from philosopher import NaivePhilosopher
from utils import PhilosopherState, Event, DEADLOCK_DETECTION_THRESHOLD


class SimulationNaive:
    """
    Simulación del problema de los filósofos comensales con algoritmo ingenuo.
    
    El algoritmo es:
    1. Filósofo intenta tomar tenedor izquierdo (bloqueante)
    2. Filósofo intenta tomar tenedor derecho (bloqueante)
    3. Si ambos tenedores están ocupados en orden circular, DEADLOCK
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
        
        # Tiempos de simulación (pueden ser ajustados)
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
            philosopher = NaivePhilosopher(i, left_fork, right_fork, self)
            self.philosophers.append(philosopher)
        
        # Registro de eventos y métricas
        self.events = deque(maxlen=100)  # Últimos 100 eventos
        self.start_time = None
        self.last_meal_times = [0] * 5  # Último tiempo en que cada filósofo comió
        self.deadlock_detected = False
        self.deadlock_start_time = None
        
        # Lock para acceso seguro a eventos
        self.event_lock = threading.Lock()
        
        # Thread para detección de deadlock
        self.deadlock_detector_thread = None
    
    def log_event(self, philosopher_id, event_type, message):
        """Registra un evento en el log"""
        if self.start_time is None:
            self.start_time = time.time()
        
        timestamp = time.time() - self.start_time
        event = Event(timestamp, philosopher_id, event_type, message)
        
        with self.event_lock:
            self.events.append(event)
        
        # Actualizar UI si está disponible
        if self.ui_callback:
            try:
                self.ui_callback("update")
            except:
                pass
    
    def start(self, synchronize_start=False):
        """
        Inicia la simulación.
        
        Args:
            synchronize_start: Si True, todos los filósofos comienzan a la vez
                              (aumenta probabilidad de deadlock)
        """
        if self.is_running:
            return
        
        self.is_running = True
        self.should_stop = False
        self.deadlock_detected = False
        self.start_time = time.time()
        self.last_meal_times = [self.start_time] * 5
        
        # Limpiar eventos previos
        self.events.clear()
        
        # Iniciar hilos de filósofos
        for philosopher in self.philosophers:
            philosopher.should_stop = False
            philosopher.is_paused = False
            philosopher.statistics = type(philosopher.statistics)(philosopher.philosopher_id)
            philosopher.start()
        
        # Si synchronize_start, poner todos en estado HUNGRY simultáneamente
        if synchronize_start:
            time.sleep(0.1)
            for philosopher in self.philosophers:
                philosopher.set_state(PhilosopherState.HUNGRY)
        
        # Iniciar detector de deadlock
        self.deadlock_detector_thread = threading.Thread(
            target=self._detect_deadlock_loop,
            daemon=True
        )
        self.deadlock_detector_thread.start()
        
        self.log_event(-1, "SYSTEM", "Simulación iniciada (modo ingenuo)")
    
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
        
        # Detener filósofos
        for philosopher in self.philosophers:
            philosopher.stop()
        
        # Esperar a que terminen (con timeout)
        for philosopher in self.philosophers:
            philosopher.join(timeout=2.0)
        
        self.is_running = False
        self.deadlock_detected = False
        
        self.log_event(-1, "SYSTEM", "Simulación detenida")
    
    def reset(self):
        """Reinicia la simulación desde cero"""
        self.stop()
        time.sleep(0.5)
        
        # Reinicializar tenedores
        self.forks = [Fork(i) for i in range(5)]
        
        # Recrear filósofos
        self.philosophers = []
        for i in range(5):
            left_fork = self.forks[i]
            right_fork = self.forks[(i + 1) % 5]
            philosopher = NaivePhilosopher(i, left_fork, right_fork, self)
            self.philosophers.append(philosopher)
        
        self.events.clear()
        self.deadlock_detected = False
        self.deadlock_start_time = None
        self.start_time = None
    
    def _detect_deadlock_loop(self):
        """
        Thread que detecta deadlock continuamente.
        
        Criterios de deadlock:
        1. Todos los filósofos están en estado HUNGRY/WAITING
        2. Nadie ha comido en los últimos N segundos
        3. No hay progreso (ningún filósofo se mueve a EATING)
        """
        stable_time = 0
        last_state_check = {}
        
        while self.is_running and not self.should_stop:
            time.sleep(0.5)  # Verificar cada 0.5 segundos
            
            if self.is_paused:
                continue
            
            # Verificar criterios de deadlock
            all_waiting_or_thinking = all(
                p.get_state() in [PhilosopherState.HUNGRY, PhilosopherState.WAITING, PhilosopherState.THINKING]
                for p in self.philosophers
            )
            
            someone_eating = any(
                p.get_state() == PhilosopherState.EATING
                for p in self.philosophers
            )
            
            # Verificar si alguien tiene exactamente un tenedor (circular wait)
            fork_owners = {}
            for fork in self.forks:
                if fork.owner_id is not None:
                    if fork.owner_id not in fork_owners:
                        fork_owners[fork.owner_id] = 0
                    fork_owners[fork.owner_id] += 1
            
            has_partial_forks = any(
                count == 1 for count in fork_owners.values()
            )
            
            # Verificar si hay progreso (alguien comió recientemente)
            current_time = time.time()
            meals_eaten = [p.statistics.meals_eaten for p in self.philosophers]
            state_signature = (
                tuple(p.get_state() for p in self.philosophers),
                tuple(meals_eaten)
            )
            
            # Si el estado no cambió desde hace DEADLOCK_DETECTION_THRESHOLD segundos
            if state_signature == last_state_check.get("signature"):
                stable_time += 0.5
            else:
                stable_time = 0
                last_state_check["signature"] = state_signature
            
            # Condiciones para declarar deadlock
            if (all_waiting_or_thinking and has_partial_forks and 
                stable_time >= DEADLOCK_DETECTION_THRESHOLD and not someone_eating):
                
                if not self.deadlock_detected:
                    self.deadlock_detected = True
                    self.deadlock_start_time = current_time
                    
                    # Marcar filósofos en deadlock
                    for philosopher in self.philosophers:
                        if philosopher.get_state() in [PhilosopherState.HUNGRY, PhilosopherState.WAITING]:
                            philosopher.set_state(PhilosopherState.DEADLOCK)
                    
                    self.log_event(-1, "DEADLOCK", "¡DEADLOCK DETECTADO!")
            else:
                if self.deadlock_detected:
                    self.deadlock_detected = False
                    # Restaurar estados
                    for philosopher in self.philosophers:
                        if philosopher.get_state() == PhilosopherState.DEADLOCK:
                            philosopher.set_state(PhilosopherState.HUNGRY)
    
    def get_philosopher_state(self, philosopher_id):
        """Obtiene el estado actual de un filósofo"""
        return self.philosophers[philosopher_id].get_state()
    
    def get_fork_state(self, fork_id):
        """Obtiene el estado actual de un tenedor"""
        fork = self.forks[fork_id]
        return {
            "is_free": fork.is_free(),
            "owner_id": fork.owner_id
        }
    
    def get_statistics(self):
        """Obtiene estadísticas de todos los filósofos"""
        return [p.statistics for p in self.philosophers]
    
    def get_recent_events(self, count=10):
        """Obtiene los últimos N eventos"""
        with self.event_lock:
            return list(self.events)[-count:]
    
    def is_in_deadlock(self):
        """Retorna True si hay deadlock detectado"""
        return self.deadlock_detected
    
    def set_simulation_speeds(self, thinking_min, thinking_max, eating_min, eating_max):
        """Ajusta los tiempos de simulación"""
        self.thinking_time_min = thinking_min
        self.thinking_time_max = thinking_max
        self.eating_time_min = eating_min
        self.eating_time_max = eating_max
