"""
Script de prueba para verificar que la simulación funciona sin GUI.
Útil para debugging y verificación sin interfaz gráfica.
"""
import sys
import time
from simulation_naive import SimulationNaive
from simulation_corrected import SimulationCorrected


def test_naive_simulation():
    """Prueba la simulación ingenua"""
    print("\n" + "="*60)
    print("TEST: Simulación Ingenua (con deadlock probable)")
    print("="*60)
    
    sim = SimulationNaive()
    sim.set_simulation_speeds(0.2, 0.5, 0.2, 0.5)
    sim.set_run_options(random_seed=123, high_contention=True)
    
    print("\nIniciando simulación ingenua...")
    print("Con 'Inicio Sincronizado' para aumentar probabilidad de deadlock\n")
    
    # Simular inicio sincronizado
    sim.start(synchronize_start=True)
    
    # Correr durante 10 segundos
    try:
        for i in range(10):
            time.sleep(1)
            stats = sim.get_statistics()
            total_meals = sum(s.meals_eaten for s in stats)
            print(f"[{i+1}s] Total comidas: {total_meals}, Deadlock: {sim.is_in_deadlock()}")
            
            if sim.is_in_deadlock():
                print("\n⚠️  DEADLOCK DETECTADO EN SIMULACIÓN INGENUA ✓")
                break
    
    except KeyboardInterrupt:
        print("\nInterrupción del usuario")
    
    finally:
        sim.stop()
        print("\nSimulación detenida")


def test_corrected_simulation():
    """Prueba la simulación corregida"""
    print("\n" + "="*60)
    print("TEST: Simulación Corregida (sin deadlock)")
    print("="*60)
    
    sim = SimulationCorrected()
    sim.set_simulation_speeds(0.2, 0.5, 0.2, 0.5)
    sim.set_run_options(random_seed=123)
    
    print("\nIniciando simulación corregida...")
    print("Aunque sea con 'Inicio Sincronizado', NO habrá deadlock\n")
    
    sim.start(synchronize_start=True)
    
    # Correr durante 10 segundos
    try:
        prev_meals = 0
        for i in range(10):
            time.sleep(1)
            stats = sim.get_statistics()
            total_meals = sum(s.meals_eaten for s in stats)
            meals_this_second = total_meals - prev_meals
            prev_meals = total_meals
            
            print(f"[{i+1}s] Total comidas: {total_meals}, Este segundo: +{meals_this_second}, Deadlock: {sim.is_in_deadlock()}")
            
            if total_meals == 0:
                print("\n❌ Error: Ningún filósofo comió (posible deadlock)")
                break
    
    except KeyboardInterrupt:
        print("\nInterrupción del usuario")
    
    finally:
        sim.stop()
        print("\nSimulación detenida")
        
        # Mostrar estadísticas finales
        print("\nEstadísticas finales:")
        stats = sim.get_statistics()
        for i, s in enumerate(stats):
            print(f"  Filósofo {i}: {s.meals_eaten} comidas, espera máx: {s.max_wait_time:.2f}s")


def main():
    """Función principal"""
    print("\n" + "🍽️  PRUEBA DE SIMULACIÓN: PROBLEMA DE LOS FILÓSOFOS COMENSALES 🍽️")
    print("="*60)
    
    try:
        # Probar ambas simulaciones
        test_naive_simulation()
        time.sleep(2)
        test_corrected_simulation()
        
        print("\n" + "="*60)
        print("✓ Pruebas completadas exitosamente")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error durante prueba: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
