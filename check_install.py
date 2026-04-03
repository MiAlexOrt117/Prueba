#!/usr/bin/env python3
"""
Script de verificación e instalación del proyecto.
Comprueba que todas las dependencias están disponibles.
"""
import sys
import subprocess
import importlib.util


def check_python_version():
    """Verifica que Python 3.6+ esté disponible"""
    print("Verificando versión de Python...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print(f"❌ Se requiere Python 3.6+. Tienes: {version.major}.{version.minor}")
        return False
    
    print(f"✓ Python {version.major}.{version.minor} detectado")
    return True


def check_tkinter():
    """Verifica que Tkinter esté disponible"""
    print("\nVerificando Tkinter...")
    
    try:
        import tkinter
        print("✓ Tkinter disponible")
        return True
    except ImportError:
        print("❌ Tkinter no está disponible")
        print("\nPara instalarlo:")
        print("  Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  Fedora: sudo dnf install python3-tkinter")
        print("  macOS: brew install python3 (incluye Tkinter)")
        print("  Windows: Re-ejecutar instalador de Python marcando Tkinter")
        return False


def check_project_files():
    """Verifica que todos los archivos del proyecto existan"""
    print("\nVerificando archivos del proyecto...")
    
    required_files = [
        "main.py",
        "philosopher.py",
        "fork.py",
        "simulation_naive.py",
        "simulation_corrected.py",
        "ui.py",
        "utils.py",
    ]
    
    import os
    all_exist = True
    
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✓ {filename}")
        else:
            print(f"❌ {filename} NO ENCONTRADO")
            all_exist = False
    
    return all_exist


def check_standard_modules():
    """Verifica que módulos estándar estén disponibles"""
    print("\nVerificando módulos estándar...")
    
    modules = [
        "threading",
        "time",
        "random",
        "math",
        "collections",
        "enum",
    ]
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"❌ {module} NO DISPONIBLE")
            return False
    
    return True


def main():
    """Función principal"""
    print("=" * 60)
    print("VERIFICACIÓN DEL PROYECTO: FILÓSOFOS COMENSALES")
    print("=" * 60)
    
    checks = [
        ("Python 3.6+", check_python_version),
        ("Tkinter", check_tkinter),
        ("Archivos del proyecto", check_project_files),
        ("Módulos estándar", check_standard_modules),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Error verificando {name}: {e}")
            results.append(False)
    
    # Resumen
    print("\n" + "=" * 60)
    if all(results):
        print("✓ TODAS LAS VERIFICACIONES PASARON")
        print("\nPara ejecutar la aplicación:")
        print("  python main.py")
        print("  o")
        print("  python3 main.py")
        print("=" * 60)
        return 0
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("\nResolve los problemas anteriores y vuelve a intentar")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
