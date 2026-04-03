# GUÍA RÁPIDA DE USO

## Instalación (2 minutos)

### Requisitos
- Python 3.6+
- Tkinter (incluido normalmente)

### Verificar Requisitos

```bash
# Verificar Python
python --version

# Verificar Tkinter
python -m tkinter
# Debe abrirse una ventana pequeña
```

### Si Falta Tkinter

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (Homebrew)
brew install python3
```

---

## Ejecución (1 minuto)

```bash
# Navegar a la carpeta del proyecto
cd "ruta/del/proyecto"

# Ejecutar
python main.py
```

O en sistemas que requieren python3:
```bash
python3 main.py
```

---

## Primera Ejecución (5 minutos)

### Paso 1: Pantalla de Selector

Se abre una ventana con dos opciones:
```
┌─────────────────────────────────────┐
│  PROBLEMA DE LOS FILÓSOFOS          │
│  COMENSALES                         │
├─────────────────────────────────────┤
│                                     │
│  Modo 1: INGENUO (con Deadlock)     │
│  [Ejecutar Modo Ingenuo]            │
│                                     │
│  Modo 2: CORREGIDO (sin Deadlock)   │
│  [Ejecutar Modo Corregido]          │
│                                     │
└─────────────────────────────────────┘
```

**Elige**: "Modo Ingenuo" para ver deadlock, o "Modo Corregido" para ver solución sin deadlock.

### Paso 2: Interfaz Principal

Se abre la ventana principal con:
- **Arriba**: Controles (Iniciar, Pausar, etc.)
- **Centro-Izquierda**: Mesa redonda con filósofos y tenedores
- **Derecha**: Estadísticas y eventos

### Paso 3: Configuración (Opcional)

Antes de iniciar, puedes:
- Ajustar **Velocidad**: 0.1x (lento) a 3.0x (rápido)
- Activar **Inicio Sincronizado**: Todos comienzan juntos (aumenta probabilidad de deadlock)
- Activar **Logs Detallados**: Ver todos los eventos

### Paso 4: Iniciar

Presiona **[Iniciar]**

---

## Modo Ingenuo - Observar Deadlock

### Configuración Recomendada

```
Velocidad: 0.5x         (más lento, fácil de ver)
Inicio Sincronizado: ✓ Activado (fuerza deadlock)
Logs Detallados: ✓ Activado (ver qué pasa)
```

### Qué Observar

```
Segundo 0-2: Los filósofos comen alternativamente
             Estados: PENSANDO → COMIENDO → PENSANDO

Segundo 3-5: PROBLEMA
             Todos pasan a estado "ESPERANDO"
             Contador de comidas se congela

Segundo 6+:  ⚠️ DEADLOCK DETECTADO ⚠️
             Filósofos muestran en ROJO
             Mensaje: "DEADLOCK DETECTADO"
             Contador de comidas: sin cambios
```

### Por Qué Ocurre

```
┌─ Filósofo 0: [Tenedor 0] → espera [Tenedor 1]
├─ Filósofo 1: [Tenedor 1] → espera [Tenedor 2]
├─ Filósofo 2: [Tenedor 2] → espera [Tenedor 3]
├─ Filósofo 3: [Tenedor 3] → espera [Tenedor 4]
└─ Filósofo 4: [Tenedor 4] → espera [Tenedor 0]
    ↑_____________________________↓

RESULTADO: Espera circular infinita
           Ninguno puede avanzar
           = DEADLOCK
```

### Estadísticas Esperadas

```
Filósofo 0: Comidas: 3, Espera max: 0.45s, Espera total: 1.20s
Filósofo 1: Comidas: 2, Espera max: 0.38s, Espera total: 0.85s
Filósofo 2: Comidas: 3, Espera max: 0.42s, Espera total: 1.10s
Filósofo 3: Comidas: 2, Espera max: 0.40s, Espera total: 0.90s
Filósofo 4: Comidas: 2, Espera max: 0.43s, Espera total: 0.95s

Total comidas: 12
Espera máxima: 0.45s
Espera total: 5.00s

⚠️ DEADLOCK ACTIVO
```

---

## Modo Corregido - Verificar Solución

### Configuración Recomendada

```
Velocidad: 1.0x         (normal)
Inicio Sincronizado: ✓ Activado (mismas condiciones que modo ingenuo)
Logs Detallados: ✗ Desactivado (menos ruido)
```

### Qué Observar

```
Segundo 0+:  Los filósofos comen CONTINUAMENTE
             Nunca se detienen
             Contador de comidas incrementa constantemente

Segundo 30:  Total comidas: ~40-50 (muy superior al ingenuo)
             Ningún mensaje de DEADLOCK
             Sistema sigue funcionando
```

### Comparación Visual

**Modo Ingenuo**:
```
Comidas:  ▄▄▄  |  ▄▄  |  ▄▄▄  |  ▄▄  |  ▄▄  |  [CONGELADO]
Tiempo:   0-2s | 2-3s | 3-5s | 5-6s | 6-7s | 7s+
```

**Modo Corregido**:
```
Comidas:  ▄▄▄ ▄▄ ▄▄▄ ▄▄ ▄▄ ▄▄▄ ▄▄ ▄▄ ▄▄▄ ▄▄ ▄▄ [CONTINÚA]
Tiempo:   0s   5s   10s   15s   20s   25s   30s+
```

### Estadísticas Esperadas

```
Filósofo 0: Comidas: 9, Espera max: 0.12s, Espera total: 0.45s
Filósofo 1: Comidas: 8, Espera max: 0.14s, Espera total: 0.52s
Filósofo 2: Comidas: 9, Espera max: 0.11s, Espera total: 0.43s
Filósofo 3: Comidas: 8, Espera max: 0.13s, Espera total: 0.48s
Filósofo 4: Comidas: 9, Espera max: 0.12s, Espera total: 0.44s

Total comidas: 43
Espera máxima: 0.14s
Espera total: 2.32s

✓ NO HAY DEADLOCK
```

---

## Controles Explicados

| Control | Función | Cuándo Usar |
|---------|---------|-----------|
| **[Iniciar]** | Comienza la simulación | Antes de cualquier cosa |
| **[Pausar]** | Pausa la simulación | Para observar sin cambios |
| **[Reanudar]** | Continúa desde pausa | Después de pausar |
| **[Reiniciar]** | Limpia y reinicia | Cambiar de modo o repetir |
| **[Detener]** | Detiene completamente | Para cerrar sin bugs |
| **Velocidad** | 0.1x a 3.0x | 0.5x para ver deadlock lentamente |
| **Inicio Sincronizado** | Comienzan todos juntos | Fuerza deadlock en modo ingenuo |
| **Logs Detallados** | Muestra todos eventos | Para debugging |

---

## Entender la Visualización

### Mesa Circular

```
        Filósofo 0 (Azul)
              ●
              |
        [Tenedor] (Gris)
              |
    1 ●   ━━━ ━━━   ● 4
   /   \             /   \
```

### Códigos de Color

**Filósofos**:
- 🔵 **AZUL**: Pensando
- 🟡 **AMARILLO**: Hambriento o Esperando
- 🟢 **VERDE**: Comiendo
- 🔴 **ROJO**: Deadlock

**Tenedores**:
- ⬜ **GRIS**: Libre
- 🟥 **ROJO**: Tomado (muestra quién lo tiene)

---

## Panel de Estadísticas

```
ESTADÍSTICAS POR FILÓSOFO
════════════════════════════════════════
Filósofo 0:
  Comidas: 8
  Espera max: 0.45s
  Espera total: 2.13s

Filósofo 1:
  Comidas: 7
  Espera max: 0.42s
  Espera total: 1.95s

[... más filósofos ...]

════════════════════════════════════════
Total comidas: 42
Espera máxima: 0.58s
Espera total: 10.2s
```

### Cómo Interpretar

- **Comidas**: Cuántas veces comió ese filósofo (fairness: deben ser ≈ iguales)
- **Espera max**: Tiempo máximo esperando en una ocasión
- **Espera total**: Suma de todos los tiempos de espera

**Indicadores de Fairness**:
- ✓ Todos tienen ≈ similar número de comidas
- ✓ Esperas máximas son similares
- ✗ Uno tiene muchas más comidas: injusto
- ✗ Uno tiene espera muy larga: posible starvation

---

## Panel de Eventos

```
EVENTOS RECIENTES
════════════════════════════════════════
[0.12s] Filósofo 0: Quiere comer, solicita al monitor
[0.13s] Filósofo 0: Entra en cola. Posición: 1
[0.14s] Filósofo 0: Espera en monitor por tenedores
[0.16s] Filósofo 1: Libera ambos tenedores
[0.16s] Filósofo 0: Tomó ambos tenedores
[0.16s] Filósofo 0: Comienza a comer (0.45s)
[0.61s] Filósofo 0: Termina de comer
[0.61s] Filósofo 0: Suelta ambos tenedores
[0.62s] Filósofo 2: Tomó ambos tenedores
...
```

### Interpretar Eventos

En modo **Ingenuo**:
```
[Intentar tomar tenedor izquierdo]
[Tomó tenedor izquierdo]
[Intenta tomar tenedor derecho]
[← SE CONGELA AQUÍ EN DEADLOCK]
```

En modo **Corregido**:
```
[Quiere comer, solicita al monitor]
[Entra en cola. Posición: 2]
[Espera en monitor por tenedores]
[← Cuando es su turno →]
[Tomó ambos tenedores]
[Comienza a comer]
```

---

## Experimentos Propuestos

### Experimento 1: Forzar Deadlock (5 min)

1. Elegir Modo Ingenuo
2. Activar "Inicio Sincronizado"
3. Velocidad 0.5x
4. Presionar Iniciar
5. **Observar**: Sistema se congela ~segundo 3-5
6. **Concluir**: Deadlock fue reproducido con éxito

---

### Experimento 2: Comparar Eficiencia (10 min)

1. **Prueba A - Modo Ingenuo**:
   - Velocidad 2.0x
   - SIN sincronización
   - Correr 20 segundos
   - Anotar: Total de comidas

2. **Prueba B - Modo Corregido**:
   - Velocidad 2.0x
   - SIN sincronización
   - Correr 20 segundos
   - Anotar: Total de comidas

3. **Comparar**:
   - Modo Corregido típicamente: 2-3× más comidas
   - Por qué: Sin deadlocks, sin reintentos fallidos

---

### Experimento 3: Demostrar Fairness (10 min)

1. Elegir Modo Corregido
2. Velocidad 1.0x
3. Correr 30 segundos
4. Observar estadísticas
5. **Resultado esperado**: Todos los filósofos tienen ≈ mismo número de comidas (±1)

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'tkinter'"

**Solución**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS
brew install python3  # incluye Tkinter
```

---

### Error: "No se encuentra main.py"

**Solución**:
1. Navega a la carpeta correcta
2. Verifica que main.py existe: `ls main.py`
3. Ejecuta: `python main.py`

---

### La Interfaz Se Ve Rara/Pequeña

**Solución**:
1. Redimensiona la ventana manualmente
2. O cierra y vuelve a ejecutar

---

### El Deadlock NO Aparece en Modo Ingenuo

**Razón**: El scheduler no siempre sincroniza perfectamente.

**Solución**:
1. Activar "Inicio Sincronizado"
2. Bajar velocidad a 0.5x
3. Repetir varias veces (probablemente aparezca)

---

### Los Filósofos Nunca Comen

**Razón**: Posible error en la lógica o sincronización.

**Solución**:
1. Revisar que no hay errores en consola
2. Presionar Reiniciar
3. Volver a intentar

---

## Archivos Útiles para Referencia

| Archivo | Propósito |
|---------|-----------|
| `README_PHILOSOPHERS.md` | Explicación teórica completa |
| `ARQUITECTURA.md` | Diseño del código |
| `RESUMEN_EJECUTIVO.md` | Resumen ejecutivo |
| `check_install.py` | Verificar instalación |
| `test_simulation.py` | Pruebas sin GUI |

---

## Próximos Pasos

### Para Aprender Más

1. Leer `README_PHILOSOPHERS.md`
2. Estudiar `philosopher.py` y `simulation_corrected.py`
3. Entender el monitor FIFO en `simulation_corrected.py` línea ~60

### Para Extender

1. Cambiar `NUM_PHILOSOPHERS` en `utils.py`
2. Implementar otro algoritmo (Hierarchical solution)
3. Agregar persistencia de estadísticas

---

**¡Disfruta observando cómo funciona la concurrencia!** 🍽️🧑‍🔬
