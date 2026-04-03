"""
Clase Philosopher (Filósofo) para la simulación.
Representa un filósofo que alterna entre pensar y comer.
"""
import threading
import time
import random
from utils import PhilosopherState, Statistics, Event


class Philosopher(threading.Thread):
    """
    Representa un filósofo en la mesa.
    Ejecuta en su propio hilo.
    """
    
    def __init__(self, philosopher_id, left_fork, right_fork, simulation):
        """
        Inicializa un filósofo.
        
        Args:
            philosopher_id: ID único del filósofo (0-4)
            left_fork: Tenedor a su izquierda
            right_fork: Tenedor a su derecha
            simulation: Referencia a la simulación (para callbacks)
        """
        super().__init__(daemon=True)
        self.philosopher_id = philosopher_id
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.simulation = simulation
        
        self.state = PhilosopherState.THINKING
        self.statistics = Statistics(philosopher_id)
        self.should_stop = False
        self.is_paused = False
        self.state_lock = threading.Lock()
    
    def set_state(self, new_state):
        """Cambia el estado del filósofo de forma segura"""
        with self.state_lock:
            self.state = new_state
    
    def get_state(self):
        """Obtiene el estado actual del filósofo"""
        with self.state_lock:
            return self.state
    
    def think(self):
        """Simula que el filósofo piensa"""
        self.set_state(PhilosopherState.THINKING)
        think_time = random.uniform(
            self.simulation.thinking_time_min,
            self.simulation.thinking_time_max
        )
        
        self.simulation.log_event(
            self.philosopher_id,
            "THINKING",
            f"Comienza a pensar ({think_time:.2f}s)"
        )
        
        # Simular pensamiento (puede ser interrumpido por pausa)
        end_time = time.time() + think_time
        while time.time() < end_time and not self.should_stop:
            if self.is_paused:
                time.sleep(0.01)
            else:
                time.sleep(0.01)
    
    def eat(self):
        """Simula que el filósofo come"""
        self.set_state(PhilosopherState.EATING)
        eating_time = random.uniform(
            self.simulation.eating_time_min,
            self.simulation.eating_time_max
        )
        
        self.simulation.log_event(
            self.philosopher_id,
            "EATING",
            f"Comienza a comer ({eating_time:.2f}s)"
        )
        
        # Simular comida (puede ser interrumpida por pausa)
        end_time = time.time() + eating_time
        while time.time() < end_time and not self.should_stop:
            if self.is_paused:
                time.sleep(0.01)
            else:
                time.sleep(0.01)
        
        self.statistics.record_meal()
        self.simulation.log_event(
            self.philosopher_id,
            "EATING_DONE",
            "Termina de comer"
        )
    
    def pause(self):
        """Pausa el hilo del filósofo"""
        self.is_paused = True
    
    def resume(self):
        """Reanuda el hilo del filósofo"""
        self.is_paused = False
    
    def stop(self):
        """Detiene el hilo del filósofo"""
        self.should_stop = True
    
    # El método run() será sobrescrito por las subclases específicas
    # de algoritmo (SimulationNaive, SimulationCorrected)
    def run(self):
        """Implementado por las subclases"""
        raise NotImplementedError("Subclases deben implementar run()")


class NaivePhilosopher(Philosopher):
    """
    Filósofo con algoritmo ingenuo (propenso a deadlock).
    Toma primero el tenedor izquierdo, luego el derecho.
    """
    
    def run(self):
        """Ciclo principal del filósofo (algoritmo ingenuo)"""
        while not self.should_stop:
            # Esperar si está pausado
            while self.is_paused and not self.should_stop:
                time.sleep(0.01)
            
            if self.should_stop:
                break
            
            # Pensar
            self.think()
            
            if self.should_stop:
                break
            
            # Intentar comer
            self.set_state(PhilosopherState.HUNGRY)
            self.statistics.start_waiting()
            
            self.simulation.log_event(
                self.philosopher_id,
                "HUNGRY",
                "Quiere comer"
            )
            
            # Tomar tenedor izquierdo (bloqueante en naive)
            self.simulation.log_event(
                self.philosopher_id,
                "GRAB_LEFT",
                "Intenta tomar tenedor izquierdo"
            )
            self.left_fork.acquire(self.philosopher_id)
            self.set_state(PhilosopherState.WAITING)
            
            self.simulation.log_event(
                self.philosopher_id,
                "GOT_LEFT",
                "Tomó tenedor izquierdo"
            )
            
            # Tomar tenedor derecho (aquí puede bloquear indefinidamente)
            self.simulation.log_event(
                self.philosopher_id,
                "GRAB_RIGHT",
                "Intenta tomar tenedor derecho"
            )
            self.right_fork.acquire(self.philosopher_id)
            
            self.simulation.log_event(
                self.philosopher_id,
                "GOT_RIGHT",
                "Tomó tenedor derecho"
            )
            
            self.statistics.end_waiting()
            
            # Comer
            self.eat()
            
            if self.should_stop:
                # Liberar tenedores antes de salir
                self.right_fork.release()
                self.left_fork.release()
                break
            
            # Soltar tenedores
            self.right_fork.release()
            self.simulation.log_event(
                self.philosopher_id,
                "RELEASE_RIGHT",
                "Suelta tenedor derecho"
            )
            
            self.left_fork.release()
            self.simulation.log_event(
                self.philosopher_id,
                "RELEASE_LEFT",
                "Suelta tenedor izquierdo"
            )


class CorrectedPhilosopher(Philosopher):
    """
    Filósofo con algoritmo corregido (sin deadlock ni starvation).
    Usa un monitor centralizado para tomar ambos tenedores atómicamente.
    """
    
    def run(self):
        """Ciclo principal del filósofo (algoritmo corregido)"""
        while not self.should_stop:
            # Esperar si está pausado
            while self.is_paused and not self.should_stop:
                time.sleep(0.01)
            
            if self.should_stop:
                break
            
            # Pensar
            self.think()
            
            if self.should_stop:
                break
            
            # Intentar comer usando el monitor
            self.set_state(PhilosopherState.HUNGRY)
            self.statistics.start_waiting()
            
            self.simulation.log_event(
                self.philosopher_id,
                "HUNGRY",
                "Quiere comer, solicita al monitor"
            )
            
            # Adquirir ambos tenedores de forma atómica
            self.simulation.acquire_forks(self.philosopher_id)
            
            self.statistics.end_waiting()
            self.simulation.log_event(
                self.philosopher_id,
                "GOT_BOTH",
                "Tiene ambos tenedores"
            )
            
            # Comer
            self.eat()
            
            if self.should_stop:
                # Liberar tenedores antes de salir
                self.simulation.release_forks(self.philosopher_id)
                break
            
            # Soltar tenedores
            self.simulation.release_forks(self.philosopher_id)
            self.simulation.log_event(
                self.philosopher_id,
                "RELEASE_BOTH",
                "Suelta ambos tenedores"
            )
