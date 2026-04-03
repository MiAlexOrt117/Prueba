"""
Clase Fork (Tenedor) para la simulación.
Representa un tenedor con estado de sincronización.
"""
import threading
from utils import ForkState


class Fork:
    """
    Representa un tenedor en la mesa.
    Usa un Lock para garantizar acceso exclusivo.
    """
    
    def __init__(self, fork_id):
        self.fork_id = fork_id
        self.state = ForkState.FREE
        self.owner_id = None  # ID del filósofo que lo tiene
        self.lock = threading.Lock()
    
    def try_acquire(self, philosopher_id):
        """
        Intenta tomar el tenedor de forma no-bloqueante.
        
        Args:
            philosopher_id: ID del filósofo que intenta tomar el tenedor
        
        Returns:
            True si logró tomar el tenedor, False si está ocupado
        """
        acquired = self.lock.acquire(blocking=False)
        if acquired:
            if self.state == ForkState.FREE:
                self.state = ForkState.TAKEN
                self.owner_id = philosopher_id
                return True
            else:
                # No estaba libre, liberar el lock
                self.lock.release()
                return False
        return False
    
    def acquire(self, philosopher_id):
        """
        Toma el tenedor de forma bloqueante.
        
        Args:
            philosopher_id: ID del filósofo que toma el tenedor
        """
        self.lock.acquire()
        self.state = ForkState.TAKEN
        self.owner_id = philosopher_id
    
    def release(self):
        """
        Suelta el tenedor.
        """
        self.state = ForkState.FREE
        self.owner_id = None
        self.lock.release()
    
    def is_free(self):
        """Retorna True si el tenedor está libre"""
        return self.state == ForkState.FREE
    
    def __repr__(self):
        return f"Fork({self.fork_id}, {self.state.value})"
