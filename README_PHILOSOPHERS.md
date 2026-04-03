# Problema de los Filósofos Comensales - Simulación Concurrente

## Índice

1. [Introducción](#introducción)
2. [Problema Teórico](#problema-teórico)
3. [Conceptos de Concurrencia Relacionados](#conceptos-de-concurrencia-relacionados)
4. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
5. [Algoritmo Ingenuo (con Deadlock)](#algoritmo-ingenuo-con-deadlock)
6. [Algoritmo Corregido (sin Deadlock)](#algoritmo-corregido-sin-deadlock)
7. [Instalación y Ejecución](#instalación-y-ejecución)
8. [Uso de la Interfaz](#uso-de-la-interfaz)
9. [Observaciones y Experimentos](#observaciones-y-experimentos)
10. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Introducción

Este proyecto es una **simulación completa, ejecutable y didáctica** del problema clásico de concurrencia en Sistemas Operacionales conocido como **"El Problema de los Filósofos Comensales"**.

### Objetivos

1. **Demostrar empíricamente** cómo ocurre el deadlock en una solución ingenua
2. **Ilustrar una solución correcta** que elimine deadlock y starvation
3. **Servir como material educativo** para cursos de Sistemas Operacionales
4. **Proporcionar visualización en tiempo real** de la concurrencia y sincronización

### Tecnología Empleada

- **Lenguaje**: Python 3
- **Concurrencia**: `threading` (hilos reales)
- **Sincronización**: `Lock`, `Condition`
- **Visualización**: Tkinter (interfaz gráfica nativa)

---

## Problema Teórico

### Planteamiento

> "Cinco filósofos se sientan alrededor de una mesa circular. Cada filósofo tiene un plato de espagueti y un tenedor. Hay exactamente cinco tenedores, uno entre cada par de filósofos adyacentes. 
> 
> Cada filósofo puede estar pensando o comiendo. Para comer, un filósofo debe tener dos tenedores: el de su izquierda y el de su derecha. 
> 
> Cuando termina de comer, suelta ambos tenedores y vuelve a pensar. 
> 
> El desafío es diseñar un algoritmo que permita a los filósofos comer indefinidamente sin quedarse bloqueados ni inanirse."

### Representación en Concurrencia

- **Filósofo** = Proceso/Hilo
- **Tenedor** = Recurso compartido
- **Pensar** = Sección no crítica
- **Comer** = Sección crítica
- **Tabla redonda** = Interdependencia cíclica

---

## Conceptos de Concurrencia Relacionados

### 1. Exclusión Mutua

Cada tenedor solo puede ser usado por un filósofo a la vez.

```python
fork.lock.acquire()  # Tomar
# usar tenedor
fork.lock.release()  # Liberar
```

### 2. Condiciones de Coffman para Deadlock

Un deadlock ocurre si y solo si se cumplen **TODAS**:

1. **Exclusión Mutua**: ✓ (tenedores son exclusivos)
2. **Hold-and-Wait**: ✓ (retenemos un recurso esperando otro)
3. **No-Preemption**: ✓ (no se quitan recursos)
4. **Circular Wait**: ✓ (espera cíclica)

**Solución**: Eliminar al menos UNA condición.

### 3. Hold-and-Wait

En el algoritmo **ingenuo**:
- Filósofo toma tenedor izquierdo (lo retiene)
- Espera tenedor derecho (puede esperar indefinidamente)

En el algoritmo **corregido**:
- Se toman AMBOS tenedores atómicamente o NINGUNO
- Esto elimina hold-and-wait

### 4. Starvation (Inanición)

Un proceso nunca obtiene los recursos que necesita (aunque no hay deadlock).

**Solución**: Fairness con política FIFO.

### 5. Monitor con Condition Variables

Estructura que garantiza:
- Exclusión mutua (Lock)
- Sincronización (Condition)
- Operaciones atómicas

```python
with threading.Condition(lock):
    while not condicion_lista():
        condition.wait()  # Libera lock temporalmente
    hacer_operacion_atomica()
    condition.notify_all()
```

---

## Arquitectura del Proyecto

### Archivos Principales

```
.
├── main.py                      # Punto de entrada y selector de modo
├── philosopher.py               # Clases Philosopher, NaivePhilosopher, CorrectedPhilosopher
├── fork.py                       # Clase Fork con sincronización
├── simulation_naive.py           # Simulación con algoritmo ingenuo (con deadlock)
├── simulation_corrected.py       # Simulación con algoritmo corregido (monitor FIFO)
├── ui.py                         # Interfaz gráfica Tkinter
├── utils.py                      # Enumeraciones, constantes, utilidades
├── README.md                     # Este archivo
└── requirements.txt              # Dependencias (solo Python estándar)
```

### Flujo de Ejecución

```
main.py
  ↓
[Selector de Modo]
  ├─→ Modo Ingenuo
  │   ├─→ SimulationNaive
  │   ├─→ [NaivePhilosopher × 5] + [Fork × 5]
  │   └─→ Detector de Deadlock
  │
  └─→ Modo Corregido
      ├─→ SimulationCorrected
      ├─→ [CorrectedPhilosopher × 5] + [Fork × 5]
      └─→ Monitor FIFO

    ↓
  ui.py (DiningPhilosophersUI)
    ├─→ Canvas: Visualización de mesa
    ├─→ Panel de estadísticas
    └─→ Panel de eventos
```

---

## Algoritmo Ingenuo (con Deadlock)

### Lógica

```python
while True:
    PENSAR()
    
    TOMAR_TENEDOR_IZQUIERDO()      # ← Puede retener indefinidamente
    TOMAR_TENEDOR_DERECHO()         # ← Puede esperar indefinidamente
    
    COMIENDO()
    
    SOLTAR_TENEDOR_DERECHO()
    SOLTAR_TENEDOR_IZQUIERDO()
```

### Escenario de Deadlock

**Tiempo T**:
```
Filósofo 0: [Tenedor 0] esperando [Tenedor 1]
Filósofo 1: [Tenedor 1] esperando [Tenedor 2]
Filósofo 2: [Tenedor 2] esperando [Tenedor 3]
Filósofo 3: [Tenedor 3] esperando [Tenedor 4]
Filósofo 4: [Tenedor 4] esperando [Tenedor 0]

→ Ciclo: 0 → 1 → 2 → 3 → 4 → 0
→ DEADLOCK: Nadie avanza
```

### Detección Automática

El sistema detecta deadlock cuando:
1. Todos esperan/hambrientos
2. Nadie come
3. Cada filósofo tiene exactamente 1 tenedor
4. Sin progreso durante 3+ segundos

```python
# Marca visual: Filósofos en rojo, mensaje ⚠️ DEADLOCK DETECTADO
```

---

## Algoritmo Corregido (sin Deadlock)

### Estrategia: Monitor FIFO

**Principio**: Tomar ambos tenedores atómicamente bajo un monitor.

```python
class Monitor:
    def acquire_forks(philosopher_id):
        with condition:  # Entra al monitor
            waiting_queue.append(philosopher_id)
            
            # Esperar hasta:
            # 1. Ser primero en la cola
            # 2. Ambos tenedores libres
            while (waiting_queue[0] != philosopher_id or
                   fork_state[left] or fork_state[right]):
                condition.wait()  # Esperar (libera monitor)
            
            # ATÓMICO: Tomar ambos
            fork_state[left] = True
            fork_state[right] = True
            waiting_queue.popleft()
    
    def release_forks(philosopher_id):
        with condition:  # Entra al monitor
            fork_state[left] = False
            fork_state[right] = False
            condition.notify_all()  # Despertar a cola
```

### ¿Por Qué No Hay Deadlock?

**Razón fundamental**: Se elimina **Hold-and-Wait**.

1. Un filósofo NUNCA retiene un tenedor sin tener el otro
2. O toma ambos o toma ninguno
3. La operación es atómica bajo el monitor

**Prueba**:
- Si no hay filósofo tomando tenedores (condición.wait())
- Entonces el primero en cola de todos los que esperan puede proceder
- Eventualmente TODOS proceden
- No hay ciclo de espera

### ¿Por Qué No Hay Starvation?

**Razón fundamental**: Cola FIFO + notify_all().

1. Los filósofos esperan en orden
2. Al liberar, se despiertan todos
3. El primero en cola con tenedores disponibles toma
4. Eventualmente, cada filósofo llega al frente

**Garantía de fairness**: FIFO ordena el acceso.

---

## Instalación y Ejecución

### Requisitos

- Python 3.6+
- Tkinter (incluido en Python estándar)

### Verificación Rápida

```bash
python --version
# Debe mostrar: Python 3.x.x

python -m tkinter
# Debe abrir una ventana pequeña de prueba
```

### Instalación en Linux (si es necesario)

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### Ejecución

```bash
python main.py
```

O:
```bash
python3 main.py
```

---

## Uso de la Interfaz

### 1. Pantalla Selector

Al iniciar, elige:
- **Modo Ingenuo**: Ver deadlock real
- **Modo Corregido**: Ver ejecución sin deadlock

### 2. Controles

- **Iniciar**: Comienza simulación
- **Pausar**: Pausa (hilos vivos)
- **Reanudar**: Continúa
- **Reiniciar**: Limpia y reinicia
- **Detener**: Finaliza

### 3. Configuración

- **Velocidad**: 0.1x a 3.0x (más lento/rápido)
- **Inicio Sincronizado**: Todos comienzan juntos (∼ deadlock probable)
- **Logs Detallados**: Mostrar todos eventos

### 4. Visualización

**Mesa Circular**:
- **Círculos**: Filósofos
  - 🔵 Azul: Pensando
  - 🟡 Amarillo: Hambriento/Esperando
  - 🟢 Verde: Comiendo
  - 🔴 Rojo: Deadlock

- **Cuadrados**: Tenedores
  - ⬜ Gris: Libre
  - 🟥 Rojo: Tomado

**Información**:
- Comidas por filósofo
- Espera máxima
- Espera total
- Status de deadlock

### 5. Panel de Estadísticas

```
ESTADÍSTICAS POR FILÓSOFO
═════════════════════════════════════════
Filósofo 0:
  Comidas: 8
  Espera max: 0.45s
  Espera total: 2.13s

Filósofo 1:
  ...

═════════════════════════════════════════
Total comidas: 42
Espera máxima: 0.58s
Espera total: 10.2s
```

### 6. Panel de Eventos

Últimos eventos del sistema (últimos 20):
```
[0.12s] Filósofo 0: Quiere comer
[0.15s] Filósofo 0: Tomó tenedor izquierdo
[0.17s] Filósofo 0: Tomó tenedor derecho
[0.17s] Filósofo 0: Comienza a comer
...
```

---

## Observaciones y Experimentos

### Experimento 1: Reproducir Deadlock (Modo Ingenuo)

**Objetivo**: Ver deadlock en vivo.

**Pasos**:
1. Elegir "Modo Ingenuo"
2. Activar "Inicio Sincronizado"
3. Velocidad: 0.5x
4. Presionar "Iniciar"
5. Observar

**Resultado Esperado**:
- Los filósofos comen alternativamente al principio
- En cierto momento, todos quedan en "Esperando"
- Contador de comidas se congela
- Mensaje: "⚠️ DEADLOCK DETECTADO ⚠️"
- Todos los filósofos pasan a rojo (DEADLOCK)

**¿Por Qué?**
- Todos tienen tenedor izquierdo
- Todos esperan tenedor derecho (del vecino)
- Espera circular indefinida

### Experimento 2: Ausencia de Deadlock (Modo Corregido)

**Objetivo**: Ver que no hay deadlock con monitor.

**Pasos**:
1. Elegir "Modo Corregido"
2. Activar "Inicio Sincronizado"
3. Velocidad: 1.0x
4. Presionar "Iniciar"
5. Observar

**Resultado Esperado**:
- Los filósofos comen continuamente
- Contador de comidas incrementa sin parar
- Nunca se detiene (NUNCA hay deadlock)
- Esperas son cortas y justas

### Experimento 3: Comparativa de Rendimiento

**Paso 1: Modo Ingenuo (sin sincronización)**
- Velocidad: 2.0x
- SIN "Inicio Sincronizado"
- Correr 30 segundos
- Anotar total de comidas

**Paso 2: Modo Corregido (sin sincronización)**
- Velocidad: 2.0x
- SIN "Inicio Sincronizado"
- Correr 30 segundos
- Anotar total de comidas

**Comparación**:
- Modo Ingenuo: Menos comidas (spins, reintentos, posible deadlock)
- Modo Corregido: Más comidas (eficiente, sin esperas circulares)

### Experimento 4: Justicia (Fairness)

**Objetivo**: Demostrar que modo corregido es justo.

**Pasos**:
1. Modo Corregido, velocidad 1.0x
2. Iniciar y esperar 20 segundos
3. Ver estadísticas

**Resultado Esperado**:
- Todos los filósofos tienen aproximadamente mismo número de comidas
- Esperas máximas son similares
- Ninguno se "muere de hambre"

**Comparación en Modo Ingenuo**:
- Algunos filósofos pueden tener muchas más comidas
- Otros pueden quedar estancados más tiempo
- Posible inanición si sincronización es adversa

---

## Preguntas Frecuentes

### P: ¿Por qué threading y no multiprocessing?

**R**: El problema de los filósofos es sobre **sincronización entre procesos**. Con threading y memoria compartida es más directo. Multiprocessing agregaría IPC innecesaria.

### P: ¿Se podría usar un único lock global?

**R**: Sí, pero **destruye la concurrencia**. El objetivo es que múltiples filósofos piensen juntos. Un lock global serializa todo.

### P: ¿Existe algún riesgo de deadlock en modo corregido?

**R**: No. La adquisición es atómica bajo el monitor. No hay hold-and-wait.

### P: ¿Cómo sé si es deadlock real vs pausa?

**R**: En deadlock:
- Ningún filósofo está comiendo
- Todos están esperando/hambrientos
- Hay ciclo de tenedores (cada uno con 1)
- Pasa 3+ segundos sin cambios

El sistema lo detecta y muestra "DEADLOCK DETECTADO".

### P: ¿Qué pasa si desactivo "Inicio Sincronizado"?

**R**: Deadlock es menos probable pero aún posible. Depende del timing del scheduler.

### P: ¿Funciona esto en PyCharm / VS Code?

**R**: Sí. Solo necesita Python 3 + Tkinter. Ejecutar `main.py` desde IDE.

### P: ¿Se puede modificar número de filósofos?

**R**: Sí, en `utils.py` cambiar `NUM_PHILOSOPHERS = 5`.

---

## Estrutura del Código

### fork.py

```python
class Fork:
    """Tenedor con sincronización"""
    - acquire(philosopher_id)      # Tomar (bloqueante)
    - try_acquire(philosopher_id)  # Tomar (no bloqueante)
    - release()                     # Soltar
    - is_free()                     # Consultar
```

### philosopher.py

```python
class Philosopher(Thread):
    """Base abstracta"""
    - think()                       # Simular pensamiento
    - eat()                         # Simular comida
    
class NaivePhilosopher(Philosopher):
    """Algoritmo ingenuo (deadlock probable)"""
    - run()                         # Loop: tomar izq, derecho, comer
    
class CorrectedPhilosopher(Philosopher):
    """Algoritmo corregido (monitor FIFO)"""
    - run()                         # Loop: usar monitor para tomar ambos
```

### simulation_naive.py

```python
class SimulationNaive:
    """Simulación con algoritmo ingenuo"""
    - start()
    - pause() / resume()
    - stop() / reset()
    - _detect_deadlock_loop()       # Thread detector
    - get_philosopher_state(id)
    - get_fork_state(id)
    - get_statistics()
    - get_recent_events(n)
    - is_in_deadlock()
```

### simulation_corrected.py

```python
class SimulationCorrected:
    """Simulación con monitor FIFO"""
    - start()
    - pause() / resume()
    - stop() / reset()
    - acquire_forks(philosopher_id)  # Bajo monitor
    - release_forks(philosopher_id)  # Bajo monitor
    - get_philosopher_state(id)
    - get_fork_state(id)
    - get_statistics()
    - get_recent_events(n)
    - get_queue_position(id)
```

### ui.py

```python
class DiningPhilosophersUI:
    """Interfaz gráfica Tkinter"""
    - _create_widgets()             # Construir UI
    - _on_start() / _on_pause() / _on_resume()
    - _on_reset() / _on_stop()
    - _update_loop()                # Loop de actualización
    - _draw_philosophers_and_forks()  # Dibujar mesa
    - _update_statistics()          # Actualizar stats
    - _update_events()              # Actualizar eventos
```

---

## Referencias Académicas

- **Dijkstra, E. W.** (1965). "Cooperating Sequential Processes"
- **Stallings, W.** (2018). "Operating Systems: Internals and Design Principles"
- **Silberschatz, A., et al.** (2018). "Operating System Concepts"

---

## Licencia

Código abierto para fines educativos.

---

**Versión**: 1.0  
**Última actualización**: 2024  
**Propósito**: Material didáctico para cursos de Sistemas Operacionales
