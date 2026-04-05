# Problema de los Filósofos Comensales

Proyecto didáctico en Python 3 y Tkinter que simula el problema clásico de concurrencia de los filósofos comensales con dos modos:

- `Modo ingenuo`: cada filósofo toma primero el tenedor izquierdo y luego espera el derecho. Con inicio sincronizado y alta contención puede aparecer un deadlock real.
- `Modo corregido`: usa un monitor con `Condition` y una cola FIFO justa para entregar ambos tenedores de forma atómica, evitando deadlock y starvation.

## Qué representa cada elemento

- Filósofo: un hilo concurrente.
- Tenedor: un recurso compartido exclusivo.
- Pensar: sección no crítica.
- Comer: sección crítica.
- Mesa circular: dependencia cíclica entre procesos y recursos.

## Cómo ocurre el deadlock en la versión ingenua

Si los cinco filósofos intentan comer al mismo tiempo:

1. Cada uno toma su tenedor izquierdo.
2. Luego cada uno intenta tomar el derecho.
3. El tenedor derecho de cada filósofo ya está retenido por su vecino.
4. Todos esperan indefinidamente.

En la interfaz esto se ve con filósofos en rojo, todos los tenedores retenidos y un aviso visual de `DEADLOCK DETECTADO`.

## Cómo evita deadlock y starvation la versión corregida

La solución corregida usa:

- `Lock` para exclusión mutua en el monitor.
- `Condition` para dormir y despertar hilos.
- Cola FIFO para fairness explícita.

Un filósofo solo avanza cuando:

1. Es el primero de la cola.
2. Sus dos tenedores están libres.

Entonces el monitor le entrega ambos tenedores atómicamente. Así se elimina `hold-and-wait` y se evita la inanición porque la cola FIFO garantiza turno justo.

## Relación con conceptos de concurrencia

- Exclusión mutua: un tenedor solo puede ser usado por un filósofo a la vez.
- Hold-and-wait: aparece en el modo ingenuo cuando un filósofo retiene el izquierdo y espera el derecho.
- No preemption: nadie puede arrebatar un tenedor ocupado.
- Circular wait: en el deadlock ingenuo se forma el ciclo `F0 -> F1 -> F2 -> F3 -> F4 -> F0`.
- Escasez de recursos: hay 5 filósofos y solo 5 tenedores, pero se necesitan 2 por comida.
- Sincronización: el monitor y las condiciones coordinan el acceso.
- Starvation: se evita en el modo corregido con cola FIFO.

## Ejecución

Requisitos:

- Python 3
- Tkinter disponible en la instalación de Python

Ejecuta:

```bash
python main.py
```

## Uso de la interfaz

- `Iniciar Modo Ingenuo`: lanza la versión que puede caer en deadlock.
- `Iniciar Modo Corregido`: lanza la solución con monitor FIFO.
- `Pausar`, `Reanudar`, `Reiniciar`, `Detener`: controlan la simulación actual.
- `Velocidad`: acelera o desacelera los tiempos de pensar y comer.
- `Semilla`: permite reproducir la misma ejecución.
- `Inicio sincronizado`: hace que todos intenten comer al mismo tiempo.
- `Alta contención`: fuerza una configuración didáctica para facilitar el deadlock ingenuo.
- `Logs detallados`: muestra todos los eventos recientes.

## Qué observar en clase

### Modo ingenuo

- Cada filósofo entra en hambre casi al mismo tiempo.
- Toma primero el tenedor izquierdo.
- Todos quedan esperando el derecho.
- El sistema detecta deadlock si no hay progreso por un intervalo.

### Modo corregido

- Los filósofos entran en una cola FIFO.
- El monitor solo entrega ambos tenedores cuando corresponde.
- El sistema sigue avanzando indefinidamente.
- Las estadísticas de espera y comidas muestran ausencia práctica de starvation.

## Estructura del proyecto

- `main.py`: punto de entrada.
- `ui.py`: interfaz Tkinter.
- `simulation_naive.py`: algoritmo ingenuo con detección de deadlock.
- `simulation_corrected.py`: monitor FIFO justo.
- `philosopher.py`: hilos de filósofos.
- `fork.py`: recurso compartido tenedor.
- `utils.py`: estados, constantes, colores y estadísticas.
