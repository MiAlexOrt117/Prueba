#!/usr/bin/env python3
"""
Script ejecutable para lanzar la simulación.
Equivalente a: python main.py
"""
import sys
import os

# Asegurar que el script se ejecuta desde su directorio
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Importar y ejecutar main
if __name__ == "__main__":
    try:
        from main import main
        main()
    except ImportError as e:
        print(f"Error al importar módulos: {e}")
        print("\nVerifique que todos los archivos .py estén en el mismo directorio:")
        print("  - main.py")
        print("  - philosopher.py")
        print("  - fork.py")
        print("  - simulation_naive.py")
        print("  - simulation_corrected.py")
        print("  - ui.py")
        print("  - utils.py")
        sys.exit(1)
    except Exception as e:
        print(f"Error ejecutando aplicación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
