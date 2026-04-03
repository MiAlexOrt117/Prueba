# ARQUITECTURA Y DISEÑO DEL PROYECTO

## 1. Visión General

El proyecto implementa una simulación concurrente completa con dos algoritmos:

```
┌─────────────────────────────────────────────────────────┐
│         PROBLEMA DE LOS FILÓSOFOS COMENSALES             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  VERSIÓN INGENUA (Naive)                                │
│  ├─ 5 × NaivePhilosopher (threading.Thread)            │
│  ├─ 5 × Fork (threading.Lock)                          │
│  └─ Detector automático de deadlock                     │
│                                                          │
│  VERSIÓN CORREGIDA (Corrected)                          │
│  ├─ 5 × CorrectedPhilosopher (threading.Thread)        │
│  ├─ 5 × Fork (threading.Lock)                          │
│  ├─ Monitor FIFO (threading.Condition + deque)         │
│  └─ Garantía de fairness                               │
│                                                          │
│  INTERFAZ GRÁFICA (Tkinter)                            │
│  ├─ Canvas: Visualización de mesa circular             │
│  ├─ Panel estadísticas: Métricas por filósofo          │
│  ├─ Panel eventos: Log de acciones                     │
│  └─ Controles: Inicio, pausa, velocidad, etc.         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Módulos y Responsabilidades

### 2.1 utils.py - Utilidades Compartidas

**Responsabilidad**: Define enumeraciones, constantes y estructuras de datos.

**Contenido**:
```python
class PhilosopherState(Enum):
    THINKING = "Pensando"
    HUNGRY = "Hambriento"
    EATING = "Comiendo"
    WAITING = "Esperando"
    DEADLOCK = "Deadlock"

class ForkState(Enum):
    FREE = "Libre"
    TAKEN = "Tomado"

class Statistics:
    # Métrica: meals_eaten, total_wait_time, max_wait_time, etc.

class Event:
    # Registro: timestamp, philosopher_id, event_type, message

# Constantes
NUM_PHILOSOPHERS = 5
COLORS = {...}
DEADLOCK_DETECTION_THRESHOLD = 3.0
```

**Uso**: Importado por todos los módulos.

---

### 2.2 fork.py - Abstracción de Tenedor

**Responsabilidad**: Encapsular un tenedor con sincronización.

**Interfaz Pública**:
```python
class Fork:
    def __init__(self, fork_id)
    
    def acquire(philosopher_id: int) -> None
        """Toma el tenedor (bloqueante)"""
    
    def try_acquire(philosopher_id: int) -> bool
        """Intenta tomar sin bloquear"""
    
    def release() -> None
        """Libera el tenedor"""
    
    def is_free() -> bool
        """Consulta disponibilidad"""
```

**Implementación**:
- Usa `threading.Lock()` para exclusión mutua
- Mantiene estado (libre/tomado)
- Registra propietario

**Diagrama**:
```
Fork(id=0)
├─ state: ForkState.FREE
├─ owner_id: None
└─ lock: threading.Lock()

[acquire]→ state=TAKEN, owner_id=X
[release]→ state=FREE, owner_id=None
```

---

### 2.3 philosopher.py - Abstracción de Filósofo

**Responsabilidad**: Implementar la lógica de filosofía (pensar/comer).

**Jerarquía**:
```python
class Philosopher(threading.Thread):
    """Base abstracta"""
    - Gestiona estados
    - Simula pensar y comer
    - Control: pause/resume/stop
    
    class NaivePhilosopher(Philosopher):
        """Algoritmo ingenuo"""
        - Toma tenedor izquierdo
        - Luego tenedor derecho
        - Puede deadlock
    
    class CorrectedPhilosopher(Philosopher):
        """Algoritmo corregido"""
        - Solicita al monitor ambos tenedores
        - No puede deadlock
```

**Ciclo de Vida del Filósofo**:
```
[THINKING] → [HUNGRY] → [WAITING] → [EATING] → [THINKING]

En modo ingenuo, puede entrar a estado [DEADLOCK]
```

**Métodos Clave**:
```python
def think():
    """Simula pensamiento (tiempo aleatorio)"""
    set_state(THINKING)
    sleep(random_time)

def eat():
    """Simula comida (tiempo aleatorio)"""
    set_state(EATING)
    sleep(random_time)
    statistics.record_meal()

def run():
    """Override por subclases: ciclo principal"""
    # NaivePhilosopher: loop infinito
    # CorrectedPhilosopher: loop con monitor
```

---

### 2.4 simulation_naive.py - Simulación Ingenua

**Responsabilidad**: Gestionar simulación con algoritmo peligroso.

**Componentes**:
```python
class SimulationNaive:
    ├─ forks: [Fork] × 5
    ├─ philosophers: [NaivePhilosopher] × 5
    ├─ events: deque(maxlen=100)  # Log de eventos
    ├─ deadlock_detector_thread: Thread  # Detección
    └─ callbacks para UI
```

**Flujo de Ejecución**:
1. `start()` → Inicia 5 threads de filósofos
2. Cada filósofo: `think()` → toma tenedor izq → **BLOQUEA esperando derecho**
3. Si todos hace esto: **DEADLOCK DETECTADO**
4. `_detect_deadlock_loop()` → Detección automática
5. UI se actualiza con estado DEADLOCK

**Detección de Deadlock**:
```python
def _detect_deadlock_loop(self):
    while True:
        if (all_waiting_or_thinking and 
            no_eating and 
            circular_wait and 
            no_progress_for_N_seconds):
            
            deadlock_detected = True
            for philosopher in philosophers:
                philosopher.state = DEADLOCK
```

---

### 2.5 simulation_corrected.py - Simulación Corregida

**Responsabilidad**: Gestionar simulación con monitor FIFO.

**Componentes**:
```python
class SimulationCorrected:
    ├─ forks: [Fork] × 5
    ├─ philosophers: [CorrectedPhilosopher] × 5
    ├─ monitor_lock: threading.Lock()
    ├─ monitor_condition: threading.Condition(lock)
    ├─ waiting_queue: deque()  # FIFO para fairness
    ├─ fork_state: [bool] × 5  # Estado bajo monitor
    └─ events: deque(maxlen=100)
```

**Monitor FIFO - Lógica Central**:

```python
def acquire_forks(philosopher_id):
    with monitor_condition:  # ← Entrada al monitor
        waiting_queue.append(philosopher_id)
        
        # ESPERAR HASTA:
        # 1. Ser el primero en cola
        # 2. Ambos tenedores libres
        while (waiting_queue[0] != philosopher_id or
               fork_state[left] or fork_state[right]):
            # Libera monitor, espera
            monitor_condition.wait()
        
        # TOMAR AMBOS (OPERACIÓN ATÓMICA)
        fork_state[left] = True
        fork_state[right] = True
        waiting_queue.popleft()
        # Libera monitor automáticamente al salir del 'with'

def release_forks(philosopher_id):
    with monitor_condition:  # ← Entrada al monitor
        fork_state[left] = False
        fork_state[right] = False
        # Despertar a TODOS los que esperan
        monitor_condition.notify_all()
```

**¿Por Qué No Hay Deadlock?**

- **Hold-and-Wait eliminado**: No retienes un tenedor esperando otro
- **Operación atómica**: O tomas ambos O ninguno
- **Under the monitor**: Solo una operación de adquisición a la vez

**¿Por Qué No Hay Starvation?**

- **Cola FIFO**: Orden justo
- **notify_all()**: Despierta a todos, no solo uno
- **Garantía matemática**: Cada filósofo eventualmente está al frente

---

### 2.6 ui.py - Interfaz Gráfica

**Responsabilidad**: Visualizar y controlar la simulación.

**Componentes Tkinter**:
```
┌─────────────────────────────────────────────────────┐
│ FRAME SUPERIOR (Controles)                         │
├─────────────────────────────────────────────────────┤
│ [Modo Selector] [Botones] [Configuración]          │
├─────────────────────────────────────────────────────┤
│ FRAME PRINCIPAL                                     │
├─────────────────────────────────────────────────────┤
│ CANVAS (Mesa)     │ PANEL DERECHO                  │
│  ┌───────────────┐ │ ┌──────────────────┐         │
│  │   Filósofos   │ │ │  Estadísticas    │         │
│  │   Tenedores   │ │ ├──────────────────┤         │
│  │   Colores     │ │ │  Eventos         │         │
│  │   Estados     │ │ │  Recientes       │         │
│  └───────────────┘ │ └──────────────────┘         │
├─────────────────────────────────────────────────────┤
│ STATUS BAR                                          │
└─────────────────────────────────────────────────────┘
```

**Clase Principal**:
```python
class DiningPhilosophersUI:
    def __init__(self, root, simulation):
        # Crear widgets
        # Setup callbacks
        # Iniciar loop de actualización
    
    def _create_widgets(self):
        # Panel superior con controles
        # Canvas para mesa
        # Panel estadísticas
        # Panel eventos
    
    def _update_loop(self):
        # Llamado cada 100ms
        # Actualiza visualización
        # Redibuja mesa
        # Actualiza estadísticas
        # Muestra eventos
```

**Ciclo de Actualización**:
```
_update_loop() cada 100ms:
├─ _draw_philosophers_and_forks()
│  ├─ Obtener estado de cada filósofo
│  ├─ Obtener estado de cada tenedor
│  └─ Dibujar en canvas con colores
├─ _update_statistics()
│  ├─ Obtener estadísticas
│  └─ Mostrar en text widget
└─ _update_events()
   ├─ Obtener últimos eventos
   └─ Mostrar en text widget
```

**Mapeo de Eventos UI → Simulación**:
```
[Iniciar] → simulation.start()
[Pausar] → simulation.pause()
[Reanudar] → simulation.resume()
[Reiniciar] → simulation.reset()
[Detener] → simulation.stop()

[Velocidad slider] → set_simulation_speeds()
[Sincronización checkbox] → start(synchronize_start=True)
```

---

### 2.7 main.py - Punto de Entrada

**Responsabilidad**: Orquestar la aplicación.

**Flujo**:
```python
main()
├─ SimulationSelector()
│  └─ Usuario elige modo
│     ├─ "Naive" → SimulationNaive()
│     └─ "Corrected" → SimulationCorrected()
├─ DiningPhilosophersUI(root, simulation)
│  └─ Muestra interfaz
└─ root.mainloop()
   └─ Loop de eventos Tkinter
```

---

## 3. Flujo de Ejecución Detallado

### 3.1 Simulación Ingenua

```
main.py ejecuta:

1. SimulationNaive.start(synchronize_start=True)
   ├─ Crea 5 NaivePhilosopher threads
   ├─ start() en cada uno
   └─ Inicia detector de deadlock

2. Cada NaivePhilosopher.run() ejecuta:
   while True:
       think()                      # Estado: THINKING
       set_state(HUNGRY)            # Estado: HUNGRY
       
       left_fork.acquire(id)        # Bloquea até obtener
       set_state(WAITING)           # Estado: WAITING
       
       right_fork.acquire(id)       # ← PUEDE BLOQUEAR INDEFINIDAMENTE
       
       eat()                        # Estado: EATING
       statistics.record_meal()
       
       right_fork.release()
       left_fork.release()

3. _detect_deadlock_loop() verifica cada 0.5s:
   if (todos esperando and ninguno comiendo and 
       cada uno tiene 1 tenedor and 3+ sin cambios):
       deadlock_detected = True

4. UI._update_loop() cada 100ms:
   redibuja mesa con colores
   actualiza estadísticas
   muestra eventos
```

### 3.2 Simulación Corregida

```
main.py ejecuta:

1. SimulationCorrected.start(synchronize_start=True)
   ├─ Crea 5 CorrectedPhilosopher threads
   ├─ start() en cada uno
   └─ Cola FIFO lista

2. Cada CorrectedPhilosopher.run() ejecuta:
   while True:
       think()                      # Estado: THINKING
       set_state(HUNGRY)            # Estado: HUNGRY
       
       acquire_forks(id)            # → Monitor
           with condition:
               waiting_queue.append(id)
               while (no es primero or no tiene ambos):
                   condition.wait()  # Libera monitor
               fork_state[left] = True
               fork_state[right] = True
               waiting_queue.popleft()
       
       eat()                        # Estado: EATING
       statistics.record_meal()
       
       release_forks(id)            # → Monitor
           with condition:
               fork_state[left] = False
               fork_state[right] = False
               condition.notify_all()  # Despertar cola

3. No hay detector (no hay deadlock posible)

4. UI._update_loop() cada 100ms:
   redibuja mesa
   actualiza estadísticas
   muestra eventos
   (nunca muestra DEADLOCK)
```

---

## 4. Mecanismos de Sincronización

### 4.1 Fork - Exclusión Mutua

```python
class Fork:
    def __init__(self):
        self.lock = threading.Lock()  # ← Mecanismo
    
    def acquire():
        self.lock.acquire()  # Espera si está ocupado
    
    def release():
        self.lock.release()  # Libera
```

**Garantía**: Solo un filósofo a la vez puede tener el tenedor.

---

### 4.2 Monitor - Operaciones Atómicas

```python
with threading.Condition(lock):
    # Mutex: solo un thread aquí a la vez
    
    while not condition_ready():
        condition.wait()  # Libera mutex, espera, reacquiere mutex
    
    # Operación atómica bajo mutex
    do_atomic_operation()
    
    condition.notify_all()  # Despertar otros
```

**Garantía**: 
- `acquire_forks()` nunca se interrumpe a mitad
- No hay race condition entre verificar y tomar
- Fairness FIFO

---

### 4.3 Detector de Deadlock - Lógica

```python
def detect_deadlock():
    """Estado = Deadlock si:"""
    
    # Criterio 1: Todos esperando
    all_waiting = all(p.state in [HUNGRY, WAITING] 
                      for p in philosophers)
    
    # Criterio 2: Ninguno comiendo
    no_eating = not any(p.state == EATING 
                        for p in philosophers)
    
    # Criterio 3: Circular wait (cada uno tiene 1 tenedor)
    for philosopher in philosophers:
        if philosophers_has_exactly_one_fork(philosopher):
            has_partial = True
    
    # Criterio 4: Sin progreso
    if no_change_for_N_seconds:
        stable = True
    
    return all_waiting and no_eating and has_partial and stable
```

---

## 5. Estadísticas y Métricas

### 5.1 Statistics (por filósofo)

```python
class Statistics:
    meals_eaten: int                    # Contador de comidas
    total_wait_time: float              # Tiempo acumulado esperando
    max_wait_time: float                # Máximo esperado en una ocasión
    failed_attempts: int                # Intentos fallidos
    
    def start_waiting(): ...            # Marcar inicio de espera
    def end_waiting(): ...              # Calcular tiempo
    def record_meal(): ...              # Incrementar contador
```

### 5.2 Events (logs)

```python
class Event:
    timestamp: float                    # Tiempo relativo
    philosopher_id: int                # Quién
    event_type: str                    # Tipo: THINKING, GRAB, EATING, etc.
    message: str                       # Descripción
```

---

## 6. Garantías Formales

### 6.1 Modo Ingenuo

**Garantía**: Puede producir deadlock.

**Prueba**:
1. Todas las 4 condiciones de Coffman pueden satisfacerse
2. Sincronización de todos los filósofos es posible
3. Estado: [T0, T1, T2, T3, T4] con cada uno con tenedor izquierdo
4. Todos esperan tenedor derecho
5. Nadie puede liberar
6. **QED**: Deadlock es posible

---

### 6.2 Modo Corregido

**Garantía 1**: NO hay deadlock.

**Prueba**:
- Hold-and-Wait es eliminado
- Un filósofo no retiene recurso esperando otro
- Por lo tanto, no puede haber espera circular
- **QED**: Sin deadlock

**Garantía 2**: NO hay starvation.

**Prueba**:
- Cola FIFO: orden total de espera
- notify_all(): todos despiertan cuando recursos libres
- Primero en cola + recursos libres = procede
- Cada filósofo eventualmente es primero en cola
- **QED**: Ninguno espera infinitamente

---

## 7. Diagrama de Estados

### Filósofo Ingenuo

```
        THINKING
           ↓
        HUNGRY
           ↓
        WAITING
         ↙   ↖
    EATING   DEADLOCK
      ↓         ↓
    (sigue)  (congela)
```

### Filósofo Corregido

```
        THINKING
           ↓
        HUNGRY
           ↓
        WAITING
           ↓
        EATING
           ↓
        THINKING (ciclo)
```

---

## 8. Complejidad

### Temporal

| Operación | Costo |
|-----------|-------|
| Tomar tenedor (ingenuo) | O(1) bloqueante |
| Tomar ambos (corregido) | O(5) verificaciones + O(1) operación |
| Detect deadlock | O(5) + O(histórico) |
| UI update | O(canvas redraw) |

### Espacial

| Estructura | Espacio |
|-----------|---------|
| 5 Filósofos | 5 × (threading.Thread + estado) |
| 5 Tenedores | 5 × (Lock + estado) |
| Events log | deque(maxlen=100) |
| Waiting queue | O(5) máximo |

---

## 9. Extensibilidad

### Fácil de Agregar

1. **Nuevo algoritmo**: Crear `SimulationXYZ` con lógica alternativa
2. **Más filósofos**: Cambiar `NUM_PHILOSOPHERS` en `utils.py`
3. **Más eventos**: Agregar a `Event` enum
4. **Nuevas estadísticas**: Extender `Statistics` class

### Desafíos Potenciales

1. **Escala**: Con >50 filósofos, Tkinter puede ser lento
2. **Fairness avanzada**: Implementar prioridades requiere cambios en monitor

---

## Conclusión

La arquitectura está diseñada para:
- ✓ Claridad educativa
- ✓ Separación de concerns
- ✓ Facilidad de debugging
- ✓ Extensibilidad futura

Cada módulo tiene una responsabilidad clara, facilitando el entendimiento de cómo se relacionan concurrencia, sincronización y algoritmos.
