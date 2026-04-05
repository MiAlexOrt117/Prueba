"""
Clases de filósofos para la simulación.
Cada filósofo corre en su propio hilo y delega la coordinación al motor.
"""
import random
import threading
import time

from utils import (
    DEFAULT_ACQUIRE_POLL_INTERVAL,
    PhilosopherState,
    Statistics,
)


class Philosopher(threading.Thread):
    """
    Representa un filósofo en la mesa.
    Ejecuta en su propio hilo.
    """

    def __init__(self, philosopher_id, left_fork, right_fork, simulation):
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
        """Cambia el estado del filósofo de forma segura."""
        with self.state_lock:
            self.state = new_state

    def get_state(self):
        """Obtiene el estado actual del filósofo."""
        with self.state_lock:
            return self.state

    def _responsive_sleep(self, duration):
        """
        Duerme sin perder la capacidad de pausar o detener el hilo.

        Returns:
            False si el hilo debe detenerse, True si completó la espera.
        """
        end_time = time.time() + duration
        while time.time() < end_time:
            if self.should_stop:
                return False

            if self.is_paused:
                time.sleep(0.05)
                continue

            time.sleep(min(0.02, end_time - time.time()))

        return not self.should_stop

    def _wait_if_paused(self):
        while self.is_paused and not self.should_stop:
            time.sleep(0.05)

    def think(self):
        """Simula que el filósofo piensa."""
        self.set_state(PhilosopherState.THINKING)
        think_time = random.uniform(
            self.simulation.thinking_time_min,
            self.simulation.thinking_time_max,
        )

        self.simulation.log_event(
            self.philosopher_id,
            "THINKING",
            f"Comienza a pensar ({think_time:.2f}s)",
        )
        return self._responsive_sleep(think_time)

    def eat(self):
        """Simula que el filósofo come."""
        self.set_state(PhilosopherState.EATING)
        eating_time = random.uniform(
            self.simulation.eating_time_min,
            self.simulation.eating_time_max,
        )

        self.simulation.log_event(
            self.philosopher_id,
            "EATING",
            f"Comienza a comer ({eating_time:.2f}s)",
        )

        completed = self._responsive_sleep(eating_time)
        if completed:
            self.statistics.record_meal()
            self.simulation.log_event(
                self.philosopher_id,
                "EATING_DONE",
                "Termina de comer",
            )
        return completed

    def pause(self):
        """Pausa el hilo del filósofo."""
        self.is_paused = True

    def resume(self):
        """Reanuda el hilo del filósofo."""
        self.is_paused = False

    def stop(self):
        """Detiene el hilo del filósofo."""
        self.should_stop = True
        self.is_paused = False

    def run(self):
        raise NotImplementedError("Subclases deben implementar run()")


class NaivePhilosopher(Philosopher):
    """
    Filósofo con algoritmo ingenuo.
    Toma primero el tenedor izquierdo y luego espera el derecho.
    """

    def _acquire_interruptible(self, fork, label):
        while not self.should_stop:
            self._wait_if_paused()
            if self.should_stop:
                return False

            if fork.try_acquire(self.philosopher_id):
                self.simulation.log_event(
                    self.philosopher_id,
                    f"GOT_{label}",
                    f"Tomó tenedor {label.lower()}",
                )
                return True

            time.sleep(DEFAULT_ACQUIRE_POLL_INTERVAL)

        return False

    def run(self):
        """Ciclo principal del filósofo ingenuo."""
        while not self.should_stop:
            self._wait_if_paused()
            if self.should_stop:
                break

            if not self.think():
                break

            self.set_state(PhilosopherState.HUNGRY)
            self.statistics.start_waiting()
            self.simulation.log_event(self.philosopher_id, "HUNGRY", "Quiere comer")

            if not self.simulation.before_naive_pickup(self.philosopher_id):
                self.statistics.end_waiting()
                break

            self.simulation.log_event(
                self.philosopher_id,
                "GRAB_LEFT",
                "Intenta tomar tenedor izquierdo",
            )
            if not self._acquire_interruptible(self.left_fork, "LEFT"):
                self.statistics.end_waiting()
                break

            self.set_state(PhilosopherState.TOOK_LEFT)

            if self.simulation.left_fork_hold_delay > 0:
                if not self._responsive_sleep(self.simulation.left_fork_hold_delay):
                    self.left_fork.release()
                    self.statistics.end_waiting()
                    break

            self.set_state(PhilosopherState.WAITING)
            self.simulation.log_event(
                self.philosopher_id,
                "GRAB_RIGHT",
                "Intenta tomar tenedor derecho",
            )
            if not self._acquire_interruptible(self.right_fork, "RIGHT"):
                self.left_fork.release()
                self.statistics.end_waiting()
                break

            self.set_state(PhilosopherState.TOOK_RIGHT)
            self.set_state(PhilosopherState.HAS_BOTH)
            self.statistics.end_waiting()

            if not self.eat():
                self.right_fork.release()
                self.left_fork.release()
                break

            self.right_fork.release()
            self.simulation.log_event(
                self.philosopher_id,
                "RELEASE_RIGHT",
                "Suelta tenedor derecho",
            )
            self.left_fork.release()
            self.simulation.log_event(
                self.philosopher_id,
                "RELEASE_LEFT",
                "Suelta tenedor izquierdo",
            )


class CorrectedPhilosopher(Philosopher):
    """
    Filósofo con algoritmo corregido.
    Usa un monitor centralizado para tomar ambos tenedores de forma atómica.
    """

    def run(self):
        """Ciclo principal del filósofo corregido."""
        while not self.should_stop:
            self._wait_if_paused()
            if self.should_stop:
                break

            if not self.think():
                break

            self.set_state(PhilosopherState.HUNGRY)
            self.statistics.start_waiting()
            self.simulation.log_event(
                self.philosopher_id,
                "HUNGRY",
                "Quiere comer, solicita al monitor",
            )

            acquired = self.simulation.acquire_forks(self.philosopher_id)
            if not acquired:
                self.statistics.end_waiting()
                break

            self.set_state(PhilosopherState.HAS_BOTH)
            self.statistics.end_waiting()
            self.simulation.log_event(
                self.philosopher_id,
                "GOT_BOTH",
                "Tiene ambos tenedores",
            )

            if not self.eat():
                self.simulation.release_forks(self.philosopher_id)
                break

            self.simulation.release_forks(self.philosopher_id)
            self.simulation.log_event(
                self.philosopher_id,
                "RELEASE_BOTH",
                "Suelta ambos tenedores",
            )
