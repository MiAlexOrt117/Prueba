"""
Simulación con algoritmo corregido: monitor FIFO sin deadlock ni starvation.
"""
import random
import threading
import time
from collections import deque

from fork import Fork
from philosopher import CorrectedPhilosopher
from utils import Event, PhilosopherState, Statistics


class SimulationCorrected:
    """
    Solución corregida basada en monitor + cola FIFO justa.

    Un filósofo solo toma los dos tenedores de forma atómica cuando:
    - es el primero de la cola
    - ambos tenedores requeridos están libres
    """

    def __init__(self, ui_callback=None):
        self.ui_callback = ui_callback
        self.is_running = False
        self.is_paused = False
        self.should_stop = False

        self.thinking_time_min = 0.5
        self.thinking_time_max = 2.0
        self.eating_time_min = 0.5
        self.eating_time_max = 1.5
        self.random_seed = None

        self.forks = [Fork(i) for i in range(5)]
        self.philosophers = self._build_philosophers()

        self.monitor_lock = threading.Lock()
        self.monitor_condition = threading.Condition(self.monitor_lock)
        self.fork_state = [False] * 5
        self.waiting_queue = deque()

        self.events = deque(maxlen=300)
        self.start_time = None
        self.event_lock = threading.Lock()

    def _build_philosophers(self):
        philosophers = []
        for i in range(5):
            philosophers.append(
                CorrectedPhilosopher(i, self.forks[i], self.forks[(i + 1) % 5], self)
            )
        return philosophers

    def log_event(self, philosopher_id, event_type, message):
        if self.start_time is None:
            self.start_time = time.time()

        timestamp = time.time() - self.start_time
        event = Event(timestamp, philosopher_id, event_type, message)
        with self.event_lock:
            self.events.append(event)

        if self.ui_callback:
            try:
                self.ui_callback("update")
            except Exception:
                pass

    def set_simulation_speeds(self, thinking_min, thinking_max, eating_min, eating_max):
        self.thinking_time_min = thinking_min
        self.thinking_time_max = thinking_max
        self.eating_time_min = eating_min
        self.eating_time_max = eating_max

    def set_run_options(self, random_seed=None, high_contention=False):
        self.random_seed = random_seed

    def acquire_forks(self, philosopher_id):
        left_fork_id = philosopher_id
        right_fork_id = (philosopher_id + 1) % 5

        with self.monitor_condition:
            if philosopher_id not in self.waiting_queue:
                self.waiting_queue.append(philosopher_id)

            self.philosophers[philosopher_id].set_state(PhilosopherState.WAITING)
            self.log_event(
                philosopher_id,
                "QUEUE",
                f"Entra en cola FIFO. Posición: {self.get_queue_position(philosopher_id)}",
            )

            while not self.should_stop:
                is_first = self.waiting_queue and self.waiting_queue[0] == philosopher_id
                forks_free = not self.fork_state[left_fork_id] and not self.fork_state[right_fork_id]
                if is_first and forks_free and not self.is_paused:
                    break

                self.monitor_condition.wait(timeout=0.1)

            if self.should_stop:
                try:
                    self.waiting_queue.remove(philosopher_id)
                except ValueError:
                    pass
                return False

            self.fork_state[left_fork_id] = True
            self.fork_state[right_fork_id] = True
            self.forks[left_fork_id].state = True
            self.forks[left_fork_id].owner_id = philosopher_id
            self.forks[right_fork_id].state = True
            self.forks[right_fork_id].owner_id = philosopher_id
            self.waiting_queue.popleft()

            self.log_event(
                philosopher_id,
                "GRABBED_BOTH",
                "El monitor entregó ambos tenedores de forma atómica",
            )
            return True

    def release_forks(self, philosopher_id):
        left_fork_id = philosopher_id
        right_fork_id = (philosopher_id + 1) % 5

        with self.monitor_condition:
            self.fork_state[left_fork_id] = False
            self.fork_state[right_fork_id] = False
            self.forks[left_fork_id].state = False
            self.forks[left_fork_id].owner_id = None
            self.forks[right_fork_id].state = False
            self.forks[right_fork_id].owner_id = None
            self.monitor_condition.notify_all()

        self.log_event(philosopher_id, "RELEASED", "Liberó ambos tenedores")

    def start(self, synchronize_start=False):
        if self.is_running:
            return

        if self.random_seed is not None:
            random.seed(self.random_seed)

        self.is_running = True
        self.is_paused = False
        self.should_stop = False
        self.start_time = time.time()
        self.events.clear()

        with self.monitor_condition:
            self.waiting_queue.clear()
            self.fork_state = [False] * 5

        for philosopher in self.philosophers:
            philosopher.should_stop = False
            philosopher.is_paused = False
            philosopher.statistics = Statistics(philosopher.philosopher_id)
            philosopher.start()

        self.log_event(-1, "SYSTEM", "Simulación iniciada (modo corregido con monitor FIFO)")

    def pause(self):
        if not self.is_running or self.is_paused:
            return

        self.is_paused = True
        for philosopher in self.philosophers:
            philosopher.pause()
        with self.monitor_condition:
            self.monitor_condition.notify_all()
        self.log_event(-1, "SYSTEM", "Simulación pausada")

    def resume(self):
        if not self.is_running or not self.is_paused:
            return

        self.is_paused = False
        for philosopher in self.philosophers:
            philosopher.resume()
        with self.monitor_condition:
            self.monitor_condition.notify_all()
        self.log_event(-1, "SYSTEM", "Simulación reanudada")

    def stop(self):
        if not self.is_running:
            return

        self.should_stop = True
        self.is_paused = False

        for philosopher in self.philosophers:
            philosopher.stop()

        with self.monitor_condition:
            self.monitor_condition.notify_all()

        for philosopher in self.philosophers:
            philosopher.join(timeout=2.0)

        with self.monitor_condition:
            self.waiting_queue.clear()
            self.fork_state = [False] * 5
            for fork in self.forks:
                fork.state = False
                fork.owner_id = None

        self.is_running = False
        self.log_event(-1, "SYSTEM", "Simulación detenida")

    def reset(self):
        self.stop()
        time.sleep(0.1)

        self.forks = [Fork(i) for i in range(5)]
        self.philosophers = self._build_philosophers()
        self.events.clear()
        self.start_time = None

        with self.monitor_condition:
            self.waiting_queue.clear()
            self.fork_state = [False] * 5

    def get_philosopher_state(self, philosopher_id):
        return self.philosophers[philosopher_id].get_state()

    def get_fork_state(self, fork_id):
        fork = self.forks[fork_id]
        return {
            "is_free": not self.fork_state[fork_id],
            "owner_id": fork.owner_id,
            "label": "Libre" if fork.owner_id is None else f"F{fork.owner_id}",
        }

    def get_statistics(self):
        return [p.statistics for p in self.philosophers]

    def get_recent_events(self, count=10):
        with self.event_lock:
            return list(self.events)[-count:]

    def get_queue_position(self, philosopher_id):
        try:
            return list(self.waiting_queue).index(philosopher_id) + 1
        except ValueError:
            return 0

    def is_in_deadlock(self):
        return False

    def get_mode_name(self):
        return "Corregido"

    def get_system_status(self):
        if not self.is_running:
            return "Detenido"
        if self.is_paused:
            return "Pausado"
        return "En ejecución"

    def get_deadlock_timestamp(self):
        return None
