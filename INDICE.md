# ÍNDICE DEL PROYECTO - Problema de los Filósofos Comensales

## 📋 Archivos del Proyecto

### 🚀 ENTRADA Y EJECUCIÓN

| Archivo | Tipo | Descripción |
|---------|------|------------|
| `main.py` | Python | **Punto de entrada principal**. Selector de modo y orquestación |
| `run.py` | Python | Script auxiliar para ejecutar |
| `check_install.py` | Python | Verificar requisitos e instalación |

### 🎯 NÚCLEO DE SIMULACIÓN

| Archivo | Tipo | Descripción |
|---------|------|------------|
| `philosopher.py` | Python | Clases: `Philosopher`, `NaivePhilosopher`, `CorrectedPhilosopher` |
| `fork.py` | Python | Clase `Fork` con sincronización con Lock |
| `simulation_naive.py` | Python | Simulación con algoritmo ingenuo (con deadlock) |
| `simulation_corrected.py` | Python | Simulación con algoritmo corregido (monitor FIFO) |
| `utils.py` | Python | Utilidades, enumeraciones, constantes |

### 🎨 INTERFAZ GRÁFICA

| Archivo | Tipo | Descripción |
|---------|------|------------|
| `ui.py` | Python | Interfaz gráfica Tkinter con visualización |

### 🧪 PRUEBAS

| Archivo | Tipo | Descripción |
|---------|------|------------|
| `test_simulation.py` | Python | Pruebas sin GUI (para verificar lógica) |

### 📚 DOCUMENTACIÓN

| Archivo | Tipo | Descripción |
|---------|------|------------|
| `README_PHILOSOPHERS.md` | Markdown | **Documentación completa** (~15kb) |
| `GUIA_RAPIDA.md` | Markdown | **Guía de uso práctico** |
| `ARQUITECTURA.md` | Markdown | **Análisis de diseño y arquitectura** |
| `RESUMEN_EJECUTIVO.md` | Markdown | **Resumen ejecutivo** |
| `requirements.txt` | Text | Dependencias (solo Python estándar) |

### 📁 ESTRUCTURA

```
Prueba/
├── README_PHILOSOPHERS.md      (← LEER PRIMERO PARA TEORÍA)
├── GUIA_RAPIDA.md             (← LEER PARA USAR)
├── RESUMEN_EJECUTIVO.md       (← RESUMEN RÁPIDO)
├── ARQUITECTURA.md            (← PARA ENTENDER CÓDIGO)
│
├── main.py                    (← EJECUTAR: python main.py)
├── run.py                     (← O: python run.py)
├── check_install.py           (← VERIFICAR: python check_install.py)
│
├── philosopher.py
├── fork.py
├── simulation_naive.py        ← Modo Ingenuo (con deadlock)
├── simulation_corrected.py    ← Modo Corregido (sin deadlock)
├── utils.py
├── ui.py
│
├── test_simulation.py         (← PRUEBAS: python test_simulation.py)
├── requirements.txt           (← Dependencias)
│
└── .git/                      (← Control de versión)
```

---

## 📖 CÓMO EMPEZAR

### 1️⃣ Leer Documentación (15 min)

**Principiante**: Leer en este orden
1. `RESUMEN_EJECUTIVO.md` (5 min)
2. `GUIA_RAPIDA.md` (10 min)

**Profundo**: Leer todo
1. `README_PHILOSOPHERS.md` (20 min) - Teoría completa
2. `RESUMEN_EJECUTIVO.md` (5 min) - Resumen
3. `GUIA_RAPIDA.md` (10 min) - Uso
4. `ARQUITECTURA.md` (20 min) - Diseño

### 2️⃣ Verificar Instalación (2 min)

```bash
python check_install.py
```

### 3️⃣ Ejecutar Aplicación (1 min)

```bash
python main.py
```

### 4️⃣ Realizar Experimentos (15-30 min)

Ver ejemplos en `GUIA_RAPIDA.md`

---

## 🎓 CONTENIDO DE APRENDIZAJE

### Conceptos Teóricos Cubiertos

✓ Problema de los filósofos comensales  
✓ Exclusión mutua (Mutex/Lock)  
✓ Sincronización con Condition Variables  
✓ Deadlock: condiciones y detección  
✓ Starvation e inanición  
✓ Monitor: Operaciones atómicas  
✓ Fairness y FIFO  
✓ Condiciones de Coffman  
✓ Hold-and-wait, No-preemption, Circular wait  
✓ Threading real en Python  

### Prácticas Incluidas

✓ Concurrencia real con `threading`  
✓ Sincronización con `Lock` y `Condition`  
✓ Detección automática de deadlock  
✓ Visualización en tiempo real (Tkinter)  
✓ Logging y estadísticas  
✓ Arquitectura limpia y modular  

---

## 🔬 EXPERIMENTOS INCLUIDOS

### Experimento 1: Reproducir Deadlock
- **Objetivo**: Ver deadlock en vivo
- **Tiempo**: 5 minutos
- **Modo**: Ingenuo + Inicio Sincronizado

### Experimento 2: Comparar Eficiencia
- **Objetivo**: Ver diferencia de rendimiento
- **Tiempo**: 10 minutos
- **Comparar**: Ingenuo vs Corregido

### Experimento 3: Demostrar Fairness
- **Objetivo**: Verificar equidad de acceso
- **Tiempo**: 10 minutos
- **Modo**: Corregido

Ver detalles completos en `GUIA_RAPIDA.md`

---

## 💡 DECISIONES DE DISEÑO

### ¿Por Qué Python?
- Sintaxis clara para conceptos de concurrencia
- `threading` para hilos reales
- Tkinter nativo sin dependencias externas

### ¿Por Qué Dos Modos?
- Modo Ingenuo: Demostrar el **problema**
- Modo Corregido: Demostrar la **solución**
- Comparación directa muy educativa

### ¿Por Qué Monitor FIFO?
- Solución clásica y bien documentada
- Fácil de entender: cola + mutex + condition
- Garantías matemáticas formales
- Didáctico para estudiantes

### ¿Por Qué Tkinter?
- Incluido con Python (sin dependencias)
- Visualización clara en tiempo real
- Controles interactivos
- Multiplataforma

---

## 📊 ESTADÍSTICAS DEL PROYECTO

| Métrica | Valor |
|---------|-------|
| Líneas de código Python | ~1500 |
| Archivos Python | 9 |
| Líneas de documentación | ~3000 |
| Archivos de documentación | 4 |
| Conceptos cubiertos | 15+ |
| Experimentos | 3+ |
| Plataformas soportadas | Windows, macOS, Linux |

---

## 🚀 CÓMO EJECUTAR

### Opción 1: Directa
```bash
cd ruta/al/proyecto
python main.py
```

### Opción 2: Verificar primero
```bash
cd ruta/al/proyecto
python check_install.py
python main.py
```

### Opción 3: Script auxiliar
```bash
cd ruta/al/proyecto
python run.py
```

### Opción 4: Pruebas sin GUI
```bash
cd ruta/al/proyecto
python test_simulation.py
```

---

## ✅ CRITERIOS DE ACEPTACIÓN CUMPLIDOS

✓ Concurrencia real con threading  
✓ Visualización gráfica en tiempo real  
✓ Dos versiones: ingenua y corregida  
✓ Versión ingenua muestra deadlock real  
✓ Versión corregida evita deadlock por diseño  
✓ Versión corregida evita starvation con FIFO  
✓ Detección automática de deadlock  
✓ Estadísticas y métricas completas  
✓ Código bien estructurado y comentado  
✓ Documentación completa en español  
✓ Sin dependencias externas innecesarias  
✓ Código ejecutable y funcional  

---

## 📝 CARACTERÍSTICAS PRINCIPALES

### Modo Ingenuo
- Algoritmo simple: izquierdo → derecho
- Puede producir deadlock
- Detector automático
- Visualización de estado DEADLOCK

### Modo Corregido
- Monitor con Condition Variable
- Cola FIFO para fairness
- Garantía matemática sin deadlock
- Garantía sin starvation

### Interfaz Gráfica
- Mesa circular visualizada
- Colores por estado
- Estadísticas en tiempo real
- Eventos recientes
- Controles: Iniciar, Pausar, Reanudar, Reiniciar, Detener
- Configuración: Velocidad, Sincronización, Logs

### Estadísticas
- Comidas por filósofo
- Tiempo de espera máximo
- Tiempo de espera acumulado
- Detección de deadlock
- Eventos del sistema

---

## 🎯 PARA INSTRUCTORES

### Sugerencia de Clase (50 min)

```
00:00 - Introducción (5 min)
       - Explicar problema
       - Mostrar algoritmo ingenuo

05:00 - Demostración Modo Ingenuo (10 min)
       - Ejecutar con sincronización
       - Mostrar deadlock
       - Explicar causas

15:00 - Teoría de Deadlock (10 min)
       - Condiciones de Coffman
       - Hold-and-wait como clave

25:00 - Presentar Solución (5 min)
       - Explicar monitor FIFO
       - Mostrar pseudocódigo

30:00 - Demostración Modo Corregido (10 min)
       - Ejecutar con mismas condiciones
       - Mostrar que NO hay deadlock
       - Mostrar fairness

40:00 - Preguntas y Discusión (10 min)
```

### Recursos para Alumnos

1. **Para leer**: `README_PHILOSOPHERS.md`
2. **Para usar**: `GUIA_RAPIDA.md`
3. **Para estudiar**: `ARQUITECTURA.md`
4. **Para experimentar**: Interfaz gráfica interactiva

---

## 🐛 SOPORTE Y TROUBLESHOOTING

Ver `GUIA_RAPIDA.md` sección **Troubleshooting**.

Problemas comunes:
- Tkinter no disponible → Instalar
- Módulos no encontrados → Verificar carpeta
- Deadlock no aparece → Activar "Inicio Sincronizado"

---

## 📚 REFERENCIAS

- Dijkstra, E. W. (1965). "Cooperating Sequential Processes"
- Stallings, W. (2018). "Operating Systems: Internals and Design Principles"
- Silberschatz, A., et al. (2018). "Operating System Concepts"
- Python threading: https://docs.python.org/3/library/threading.html

---

## 📄 LICENCIA

Código abierto para fines educativos.

---

## 👤 INFORMACIÓN DEL PROYECTO

**Versión**: 1.0  
**Fecha**: 2024  
**Propósito**: Material didáctico para Sistemas Operacionales  
**Idioma**: Español (comentarios en código)  
**Plataformas**: Windows, macOS, Linux  
**Requisitos**: Python 3.6+ + Tkinter  

---

**¿Por dónde empiezo?**

1. **Principiante**: `GUIA_RAPIDA.md` → Ejecutar `main.py`
2. **Estudiante**: `README_PHILOSOPHERS.md` → `ARQUITECTURA.md`
3. **Instructor**: `RESUMEN_EJECUTIVO.md` → Preparar clase
4. **Desarrollador**: `ARQUITECTURA.md` → Estudiar código

---

**¡Bienvenido al Problema de los Filósofos Comensales!** 🍽️
