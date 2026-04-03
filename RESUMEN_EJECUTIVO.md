# RESUMEN EJECUTIVO DEL PROYECTO

## Problema de los Filósofos Comensales - Simulación Concurrente

### ¿QUÉ ES ESTE PROYECTO?

Una **simulación completa, didáctica y ejecutable** del problema clásico de concurrencia en Sistemas Operacionales que demuestra:

1. **Cómo ocurre el DEADLOCK** con un algoritmo ingenuo
2. **Cómo se EVITA el DEADLOCK** con un algoritmo correcto
3. **Cómo se garantiza FAIRNESS** (ausencia de starvation)
4. Visualización en tiempo real de la concurrencia

---

## INSTALACIÓN Y EJECUCIÓN

### Requisitos
- Python 3.6+
- Tkinter (incluido por defecto)

### Ejecutar
```bash
python main.py
```

O:
```bash
python3 main.py
```

### Primera ejecución
1. Se abre una ventana de selector
2. Elegir modo:
   - **Ingenuo**: Ver deadlock real
   - **Corregido**: Ver ejecución sin deadlock
3. Se abre interfaz gráfica con mesa circular
4. Presionar "Iniciar"
5. Observar el comportamiento

---

## ARCHIVOS DEL PROYECTO

### Núcleo de la Simulación

| Archivo | Descripción |
|---------|------------|
| `philosopher.py` | Clases `Philosopher`, `NaivePhilosopher`, `CorrectedPhilosopher` |
| `fork.py` | Clase `Fork` con sincronización |
| `simulation_naive.py` | Simulación con algoritmo ingenuo (con deadlock) |
| `simulation_corrected.py` | Simulación con monitor FIFO (sin deadlock) |
| `utils.py` | Enumeraciones, constantes, estadísticas |

### Interfaz y Entrada

| Archivo | Descripción |
|---------|------------|
| `main.py` | Punto de entrada, selector de modo |
| `ui.py` | Interfaz gráfica Tkinter |

### Pruebas y Documentación

| Archivo | Descripción |
|---------|------------|
| `test_simulation.py` | Script de prueba sin GUI |
| `run.py` | Script auxiliar para ejecutar |
| `README_PHILOSOPHERS.md` | Documentación completa |
| `requirements.txt` | Dependencias (solo Python estándar) |

---

## MODO INGENUO (Con Deadlock)

### Algoritmo

```
1. Pensar
2. Tomar tenedor IZQUIERDO
3. Tomar tenedor DERECHO
4. Comer
5. Soltar ambos tenedores
6. Ir a paso 1
```

### Por Qué Genera Deadlock

```
Si todos los filósofos hacen esto simultáneamente:

Tiempo 1: Todos terminan de pensar
Tiempo 2: Todos toman tenedor izquierdo
Tiempo 3: PROBLEMA
  - Filósofo 0 tiene tenedor 0, necesita tenedor 1
  - Filósofo 1 tiene tenedor 1, necesita tenedor 2
  - ...
  - Filósofo 4 tiene tenedor 4, necesita tenedor 0
  
RESULTADO: Espera circular infinita → DEADLOCK
```

### Cómo Verlo

1. Elegir "Modo Ingenuo"
2. Activar "Inicio Sincronizado"
3. Presionar "Iniciar"
4. Observar que se congela con mensaje "⚠️ DEADLOCK DETECTADO"

---

## MODO CORREGIDO (Sin Deadlock)

### Algoritmo

```
1. Pensar
2. SOLICITAR A MONITOR: "Quiero comer"
3. MONITOR (atomicamente):
   - Si es mi turno Y ambos tenedores libres:
     a. Tomar AMBOS tenedores
     b. Permitir que coma
   - Si no:
     a. Esperar en cola FIFO
     b. Cuando sea su turno: tomar AMBOS
4. Comer
5. LIBERAR AL MONITOR: ambos tenedores
6. Ir a paso 1
```

### Por Qué No Hay Deadlock

**Razón clave**: Eliminamos **Hold-and-Wait**

- Con algoritmo ingenuo: toma 1, espera 2, puede esperar indefinidamente
- Con monitor: toma AMBOS O NINGUNO (operación atómica)

### Por Qué No Hay Starvation

**Razón clave**: Cola FIFO + notify_all()

- Los filósofos esperan en orden justo
- Cuando alguien libera, todos son despertados
- El primero en cola y con tenedores disponibles come
- Eventualmente todos llegan al frente

---

## VISUALIZACIÓN

### Mesa Circular

```
        Filósofo 0
              ●
              |
    T(0)      T(1)
      \       /
       \     /
    1 ●     ● 4
   /   \   /   \
  T(0)   X   T(4)
  /       \
 2 ●       ● 3
  \       /
   \     /
    T(2) T(3)
```

### Colores

- **🔵 Azul**: Pensando
- **🟡 Amarillo**: Hambriento/Esperando
- **🟢 Verde**: Comiendo
- **🔴 Rojo**: Deadlock

### Información Mostrada

- Comidas por filósofo
- Tiempo de espera máximo y acumulado
- Eventos recientes del sistema
- Estado de deadlock

---

## EXPERIMENTOS PROPUESTOS

### Experimento 1: Reproducir Deadlock

1. Modo Ingenuo + "Inicio Sincronizado"
2. Velocidad: 0.5x
3. Observar: Sistema se congela
4. Resultado esperado: Mensaje "DEADLOCK DETECTADO"

### Experimento 2: Comparar Modos

1. Ejecutar Ingenuo 30 segundos → X comidas
2. Ejecutar Corregido 30 segundos → Y comidas
3. Típicamente: Y >> X (corregido es más eficiente)

### Experimento 3: Justicia

1. Modo Corregido, velocidad 1.0x, 20 segundos
2. Ver estadísticas finales
3. Resultado esperado: Todos los filósofos tienen ≈ mismo número de comidas

---

## CONCEPTOS ACADÉMICOS ILUSTRADOS

### Condiciones de Coffman para Deadlock

El sistema demuestra las 4 condiciones necesarias:

1. **Exclusión Mutua**: ✓ Cada tenedor es exclusivo
2. **Hold-and-Wait**: ✓ En modo ingenuo
3. **No-Preemption**: ✓ No se quitan tenedores
4. **Circular Wait**: ✓ Espera cíclica

**Solución**: Modo corregido elimina Hold-and-Wait

### Monitor con Condition Variables

```python
with threading.Condition(lock):
    while not ready():
        condition.wait()  # Libera lock, espera
    hacer_operacion_atomica()
    condition.notify_all()  # Despertar otros
```

### Fairness

- **Injusto**: Algunos filósofos comen más que otros
- **Justo (FIFO)**: Todos tienen igual oportunidad

---

## ESTRUCTURA DEL CÓDIGO

### Jerarquía de Clases

```
threading.Thread
    └── Philosopher (base abstracta)
            ├── NaivePhilosopher (algoritmo ingenuo)
            └── CorrectedPhilosopher (algoritmo corregido)

threading.Lock
    └── Fork (tenedor con sincronización)

threading.Condition + deque
    └── Monitor FIFO (en SimulationCorrected)
```

### Flujo de Ejecución

```
main.py
  ↓
[Selector de Modo]
  ↓
SimulationNaive O SimulationCorrected
  ├─ 5 × Philosopher (threading.Thread)
  ├─ 5 × Fork (threading.Lock)
  └─ Monitor (threading.Condition + deque)
  ↓
DiningPhilosophersUI (Tkinter)
  ├─ Canvas (visualización mesa)
  ├─ Panel estadísticas
  └─ Panel eventos
```

---

## PREGUNTAS FRECUENTES

**P: ¿Es real el threading?**  
R: Sí, usa `threading` con hilos reales y sincronización real.

**P: ¿Se puede cambiar el número de filósofos?**  
R: Sí, en `utils.py`: `NUM_PHILOSOPHERS = 5`

**P: ¿Por qué no funciona en [plataforma]?**  
R: Tkinter debe estar disponible. En Linux: `sudo apt-get install python3-tk`

**P: ¿Se puede ver el código de ambos algoritmos?**  
R: Sí:
- Ingenuo: `simulation_naive.py` línea ~150-180
- Corregido: `simulation_corrected.py` línea ~60-120

**P: ¿Garantiza realmente que no hay deadlock en modo corregido?**  
R: Matemáticamente sí. Hold-and-Wait es eliminado. Solo toma si tiene ambos.

---

## PARA INSTRUCTORES

### Flujo de Clase Sugerido

1. **Introducción (5 min)**
   - Explicar problema de los filósofos
   - Mostrar algoritmo ingenuo en pseudocódigo

2. **Demostración Modo Ingenuo (10 min)**
   - Ejecutar con "Inicio Sincronizado"
   - Mostrar deadlock en vivo
   - Explicar por qué ocurre

3. **Teoría de Deadlock (10 min)**
   - Condiciones de Coffman
   - Hold-and-Wait como problema clave

4. **Presentar Solución (10 min)**
   - Explicar monitor FIFO
   - Mostrar pseudocódigo

5. **Demostración Modo Corregido (10 min)**
   - Ejecutar con mismas condiciones
   - Mostrar que NO hay deadlock
   - Mostrar estadísticas de fairness

6. **Conclusiones (5 min)**
   - Resumen de conceptos
   - Mencionar aplicaciones reales

---

## LIMITACIONES Y EXTENSIONES

### Limitaciones Actuales
- Solo 5 filósofos (número clásico)
- Tiempos aleatorios simples
- Interfaz 2D (no 3D)

### Extensiones Posibles
- Cambiar número de filósofos (con UI)
- Implementar otras soluciones (Resource Hierarchy, etc.)
- Agregar estadísticas más avanzadas
- Versión multi-ventana para comparar simultáneamente

---

## REFERENCIAS

- **Dijkstra, E. W.** (1965). "Cooperating Sequential Processes"
- **Stallings, W.** (2018). "Operating Systems: Internals and Design Principles"
- **Silberschatz, A., et al.** (2018). "Operating System Concepts"

---

## LICENCIA

Código abierto para fines educativos.

---

**Versión**: 1.0  
**Última actualización**: 2024  
**Propósito**: Material didáctico para cursos de Sistemas Operacionales  
**Idioma**: Español (comentarios bilingües)
