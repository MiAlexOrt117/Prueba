"""
Simulación con algoritmo ingenuo (propenso a deadlock).
"""
import random
import threading
import time
from collections import deque

from fork import Fork
from philosopher import NaivePhilosopher
from utils import (
    DEADLOCK_DETECTION_THRESHOLD,
    DEFAULT_LEFT_FORK_HOLD_DELAY,
    Event,
    PhilosopherState,
    Statistics,
)


class SimulationNaive:
    """
    Simulación del problema de los filósofos comensales con estrategia ingenua.

    Cada filósofo toma primero el tenedor izquierdo y luego espera el derecho.
    Con inicio sincronizado y alta contención, el deadlock aparece de forma
    reproducible.
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
        self.left_fork_hold_delay = 0.0
        self.random_seed = None
        self.high_contention = False

        self.forks = [Fork(i) for i in range(5)]
        self.philosophers = self._build_philosophers()

        self.events = deque(maxlen=300)
        self.start_time = None
        self.event_lock = threading.Lock()

        self.deadlock_detected = False
        self.deadlock_start_time = None
        self.last_progress_time = None
        self.deadlock_detector_thread = None
        self.round_barrier = None

    def _build_philosophers(self):
        philosophers = []
        for i in range(5):
            philosophers.append(
                NaivePhilosopher(i, self.forks[i], self.forks[(i + 1) % 5], self)
            )
        return philosophers

    def log_event(self, philosopher_id, event_type, message):
        if self.start_time is None:
            self.start_time = time.time()

        timestamp = time.time() - self.start_time
        event = Event(timestamp, philosopher_id, event_type, message)
        with self.event_lock:
            self.events.append(event)

        if event_type in {"EATING", "EATING_DONE", "RELEASE_LEFT", "RELEASE_RIGHT"}:
            self.last_progress_time = time.time()

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
        self.high_contention = high_contention

    def before_naive_pickup(self, philosopher_id):
        """
        Sincroniza el inicio del intento de comer cuando se pide alta contención.
        """
        if not self.round_barrier:
            return not self.should_stop

        self.log_event(
            philosopher_id,
            "BARRIER",
            "Esperando inicio sincronizado para intentar comer",
        )
        try:
            self.round_barrier.wait()
            return not self.should_stop
        except threading.BrokenBarrierError:
            return False

    def start(self, synchronize_start=False):
        if self.is_running:
            return

        if self.random_seed is not None:
            random.seed(self.random_seed)

        self.is_running = True
        self.is_paused = False
        self.should_stop = False
        self.deadlock_detected = False
        self.deadlock_start_time = None
        self.start_time = time.time()
        self.last_progress_time = self.start_time
        self.events.clear()

        if self.high_contention:
            self.left_fork_hold_delay = DEFAULT_LEFT_FORK_HOLD_DELAY
            self.thinking_time_min = 0.0
            self.thinking_time_max = 0.02
        else:
            self.left_fork_hold_delay = 0.0

        self.round_barrier = threading.Barrier(5) if synchronize_start else None

        for philosopher in self.philosophers:
            philosopher.should_stop = False
            philosopher.is_paused = False
            philosopher.statistics = Statistics(philosopher.philosopher_id)
            philosopher.start()

        self.deadlock_detector_thread = threading.Thread(
            target=self._detect_deadlock_loop,
            daemon=True,
        )
        self.deadlock_detector_thread.start()

        mode_message = "Simulación iniciada (modo ingenuo)"
        if synchronize_start:
            mode_message += " con inicio sincronizado"
        if self.high_contention:
            mode_message += " y alta contención"
        self.log_event(-1, "SYSTEM", mode_message)

    def pause(self):
        if not self.is_running or self.is_paused:
            return

        self.is_paused = True
        for philosopher in self.philosophers:
            philosopher.pause()
        self.log_event(-1, "SYSTEM", "Simulación pausada")

    def resume(self):
        if not self.is_running or not self.is_paused:
            return

        self.is_paused = False
        for philosopher in self.philosophers:
            philosopher.resume()
        self.log_event(-1, "SYSTEM", "Simulación reanudada")

    def stop(self):
        if not self.is_running:
            return

        self.should_stop = True

        if self.round_barrier:
            try:
                self.round_barrier.abort()
            except threading.BrokenBarrierError:
                pass

        for philosopher in self.philosophers:
            philosopher.stop()

        for fork in self.forks:
            if fork.owner_id is not None:
                fork.release()

        for philosopher in self.philosophers:
            philosopher.join(timeout=2.0)

        self.is_running = False
        self.is_paused = False
        self.deadlock_detected = False
        self.log_event(-1, "SYSTEM", "Simulación detenida")

    def reset(self):
        self.stop()
        time.sleep(0.1)

        self.forks = [Fork(i) for i in range(5)]
        self.philosophers = self._build_philosophers()
        self.events.clear()
        self.deadlock_detected = False
        self.deadlock_start_time = None
        self.start_time = None
        self.last_progress_time = None
        self.round_barrier = None

    def _detect_deadlock_loop(self):
        stable_time = 0.0
        previous_signature = None

        while self.is_running and not self.should_stop:
            time.sleep(0.25)
            if self.is_paused:
                continue

            states = tuple(p.get_state() for p in self.philosophers)
            meals = tuple(p.statistics.meals_eaten for p in self.philosophers)
            signature = (states, meals, tuple(f.owner_id for f in self.forks))

            if signature == previous_signature:
                stable_time += 0.25
            else:
                stable_time = 0.0
                previous_signature = signature

            everyone_holds_left = all(fork.owner_id == i for i, fork in enumerate(self.forks))
            nobody_eating = all(
                philosopher.get_state() != PhilosopherState.EATING
                for philosopher in self.philosophers
            )
            all_blocked = all(
                philosopher.get_state() in {
                    PhilosopherState.TOOK_LEFT,
                    PhilosopherState.WAITING,
                    PhilosopherState.DEADLOCK,
                }
                for philosopher in self.philosophers
            )

            no_progress = (
                self.last_progress_time is not None
                and (time.time() - self.last_progress_time) >= DEADLOCK_DETECTION_THRESHOLD
            )

            if everyone_holds_left and nobody_eating and all_blocked and no_progress and stable_time >= DEADLOCK_DETECTION_THRESHOLD:
                if not self.deadlock_detected:
                    self.deadlock_detected = True
                    self.deadlock_start_time = time.time()
                    for philosopher in self.philosophers:
                        philosopher.set_state(PhilosopherState.DEADLOCK)
                    self.log_event(
                        -1,
                        "DEADLOCK",
                        "DEADLOCK detectado: todos retienen el tenedor izquierdo y esperan el derecho",
                    )
            elif self.deadlock_detected:
                self.deadlock_detected = False

    def get_philosopher_state(self, philosopher_id):
        return self.philosophers[philosopher_id].get_state()

    def get_fork_state(self, fork_id):
        fork = self.forks[fork_id]
        return {
            "is_free": fork.is_free(),
            "owner_id": fork.owner_id,
            "label": "Libre" if fork.owner_id is None else f"F{fork.owner_id}",
        }

    def get_statistics(self):
        return [p.statistics for p in self.philosophers]

    def get_recent_events(self, count=10):
        with self.event_lock:
            return list(self.events)[-count:]

    def is_in_deadlock(self):
        return self.deadlock_detected

    def get_mode_name(self):
        return "Ingenuo"

    def get_system_status(self):
        if not self.is_running:
            return "Detenido"
        if self.is_paused:
            return "Pausado"
        if self.deadlock_detected:
            return "Deadlock"
        return "En ejecución"

    def get_deadlock_timestamp(self):
        if self.deadlock_start_time is None or self.start_time is None:
            return None
        return self.deadlock_start_time - self.start_time
