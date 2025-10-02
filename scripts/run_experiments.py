import sys
import os
import subprocess
import time
from datetime import datetime
import json
import yaml
from load_experiment_config import load_experiments_config, create_env_from_experiment

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

EXPERIMENTS = [
    {
        "name": "Experimento 1: LRU + Poisson (Baseline)",
        "config": {
            "CACHE_POLICY": "LRU",
            "CACHE_MAX_SIZE": "10000",
            "TRAFFIC_DISTRIBUTION_TYPE": "POISSON",
            "TRAFFIC_LAMBDA": "0.5",
            "TRAFFIC_NUM_REQUESTS": "1000",
            "TRAFFIC_MAX_DELAY_SECONDS": "10"
        },
        "db_file": "data/results_exp1_lru_poisson.db"
    },
    {
        "name": "Experimento 2: LFU + Poisson",
        "config": {
            "CACHE_POLICY": "LFU",
            "CACHE_MAX_SIZE": "10000",
            "TRAFFIC_DISTRIBUTION_TYPE": "POISSON",
            "TRAFFIC_LAMBDA": "0.5",
            "TRAFFIC_NUM_REQUESTS": "1000",
            "TRAFFIC_MAX_DELAY_SECONDS": "10"
        },
        "db_file": "data/results_exp2_lfu_poisson.db"
    },
    {
        "name": "Experimento 3: FIFO + Poisson",
        "config": {
            "CACHE_POLICY": "FIFO",
            "CACHE_MAX_SIZE": "10000",
            "TRAFFIC_DISTRIBUTION_TYPE": "POISSON",
            "TRAFFIC_LAMBDA": "0.5",
            "TRAFFIC_NUM_REQUESTS": "1000",
            "TRAFFIC_MAX_DELAY_SECONDS": "10"
        },
        "db_file": "data/results_exp3_fifo_poisson.db"
    },
    {
        "name": "Experimento 4: LRU + Uniforme",
        "config": {
            "CACHE_POLICY": "LRU",
            "CACHE_MAX_SIZE": "10000",
            "TRAFFIC_DISTRIBUTION_TYPE": "UNIFORM",
            "TRAFFIC_LAMBDA": "0.5",
            "TRAFFIC_NUM_REQUESTS": "1000",
            "TRAFFIC_MAX_DELAY_SECONDS": "10"
        },
        "db_file": "data/results_exp4_lru_uniform.db"
    },
    {
        "name": "Experimento 5: LRU + Exponencial",
        "config": {
            "CACHE_POLICY": "LRU",
            "CACHE_MAX_SIZE": "10000",
            "TRAFFIC_DISTRIBUTION_TYPE": "EXPONENTIAL",
            "TRAFFIC_LAMBDA": "0.5",
            "TRAFFIC_NUM_REQUESTS": "1000",
            "TRAFFIC_MAX_DELAY_SECONDS": "10"
        },
        "db_file": "data/results_exp5_lru_exponential.db"
    },
    {
        "name": "Experimento 6: LRU + Caché pequeña (1000)",
        "config": {
            "CACHE_POLICY": "LRU",
            "CACHE_MAX_SIZE": "1000",
            "TRAFFIC_DISTRIBUTION_TYPE": "POISSON",
            "TRAFFIC_LAMBDA": "0.5",
            "TRAFFIC_NUM_REQUESTS": "1000",
            "TRAFFIC_MAX_DELAY_SECONDS": "10"
        },
        "db_file": "data/results_exp6_lru_small_cache.db"
    },
    {
        "name": "Experimento 7: LRU + Caché grande (50000)",
        "config": {
            "CACHE_POLICY": "LRU",
            "CACHE_MAX_SIZE": "50000",
            "TRAFFIC_DISTRIBUTION_TYPE": "POISSON",
            "TRAFFIC_LAMBDA": "0.5",
            "TRAFFIC_NUM_REQUESTS": "1000",
            "TRAFFIC_MAX_DELAY_SECONDS": "10"
        },
        "db_file": "data/results_exp7_lru_large_cache.db"
    },
    {
        "name": "Experimento 8: Alta carga (Lambda 2.0)",
        "config": {
            "CACHE_POLICY": "LRU",
            "CACHE_MAX_SIZE": "10000",
            "TRAFFIC_DISTRIBUTION_TYPE": "POISSON",
            "TRAFFIC_LAMBDA": "2.0",
            "TRAFFIC_NUM_REQUESTS": "1000",
            "TRAFFIC_MAX_DELAY_SECONDS": "5"
        },
        "db_file": "data/results_exp8_high_load.db"
    }
]

def print_banner():
    print("\n" + "="*80)
    print(" "*25 + "EJECUTOR DE EXPERIMENTOS")
    print(" "*20 + "Sistema de Análisis Yahoo! Answers")
    print("="*80)

def update_env_file(config):
    env_path = ".env"
    
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    updated_lines = []
    for line in lines:
        key = line.split('=')[0].strip()
        if key in config:
            updated_lines.append(f"{key}={config[key]}\n")
        else:
            updated_lines.append(line)
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

def run_experiment(experiment):
    print("\n" + "="*80)
    print(f"EJECUTANDO: {experiment['name']}")
    print("="*80)
    print("\nConfiguración:")
    for key, value in experiment['config'].items():
        print(f"  {key}: {value}")
    print()
    
    print("[DEBUG] Actualizando archivo .env...")
    config_with_db = experiment['config'].copy()
    config_with_db['SQLITE_DB_PATH'] = experiment['db_file']
    update_env_file(config_with_db)
    print("[DEBUG] Archivo .env actualizado")
    
    print("[DEBUG] Iniciando subprocess de src/main.py...")
    start_time = time.time()
    try:
        result = subprocess.run(
            ['python', 'src/main.py'],
            text=True,
            timeout=3600  # 1 hora máximo
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"\nExperimento completado en {elapsed_time:.2f} segundos")
        
        if result.returncode == 0:
            print("✓ Experimento exitoso")
        else:
            print(f"✗ Experimento falló con código {result.returncode}")
        
        return {
            'name': experiment['name'],
            'success': result.returncode == 0,
            'elapsed_time': elapsed_time,
            'db_file': experiment['db_file']
        }
        
    except subprocess.TimeoutExpired:
        print(f"\n✗ Experimento excedió el tiempo límite (1 hora)")
        return {
            'name': experiment['name'],
            'success': False,
            'elapsed_time': 3600,
            'error': 'Timeout'
        }
    except Exception as e:
        print(f"\n✗ Error ejecutando experimento: {e}")
        import traceback
        traceback.print_exc()
        return {
            'name': experiment['name'],
            'success': False,
            'error': str(e)
        }

def run_single_experiment(experiment_id):
    print(f"[DEBUG] Iniciando ejecución del experimento {experiment_id}...")
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ['python', 'src/main.py'],
            text=True,
            timeout=3600  
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"\nExperimento completado en {elapsed_time:.2f} segundos")
        
        if result.returncode == 0:
            print(f"✓ Experimento {experiment_id} exitoso")
        else:
            print(f"✗ Experimento {experiment_id} falló con código {result.returncode}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"\n✗ Experimento {experiment_id} excedió el tiempo límite (1 hora)")
        return False
    except Exception as e:
        print(f"\n✗ Error ejecutando experimento {experiment_id}: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_experiments():
    print_banner()
    
    print(f"\nSe ejecutarán {len(EXPERIMENTS)} experimentos")
    print("Cada experimento generará su propia base de datos con resultados")
    print("\nEsto puede tomar varias horas dependiendo de tu hardware.")
    
    response = input("\n¿Deseas continuar? (s/n): ")
    if response.lower() not in ['s', 'si', 'yes', 'y']:
        print("Operación cancelada.")
        return
    
    os.makedirs('data', exist_ok=True)
    
    results = []
    start_time = datetime.now()
    
    for i, experiment in enumerate(EXPERIMENTS, 1):
        print(f"\n\n{'='*80}")
        print(f"PROGRESO: Experimento {i}/{len(EXPERIMENTS)}")
        print(f"{'='*80}")
        
        result = run_experiment(experiment)
        results.append(result)
        
        if i < len(EXPERIMENTS):
            print("\nEsperando 1 segundo antes del siguiente experimento...")
            time.sleep(1)
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    print("\n\n" + "="*80)
    print(" "*30 + "RESUMEN DE EXPERIMENTOS")
    print("="*80)
    print(f"\nTiempo total: {total_time/60:.2f} minutos")
    print(f"Inicio: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Fin: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nExperimentos exitosos: {sum(1 for r in results if r['success'])}/{len(results)}")
    
    print("\nDetalle de experimentos:")
    for result in results:
        status = "✓" if result['success'] else "✗"
        time_str = f"{result.get('elapsed_time', 0):.2f}s"
        print(f"  {status} {result['name']} - {time_str}")
        if 'db_file' in result:
            print(f"     DB: {result['db_file']}")
    
    summary_file = f"data/experiments_summary_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump({
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'total_time_seconds': total_time,
            'results': results
        }, f, indent=2)
    
    print(f"\nResumen guardado en: {summary_file}")
    print("\n" + "="*80)
    print("Todos los experimentos completados!")
    print("Ejecuta 'python scripts/compare_experiments.py' para analizar los resultados")
    print("="*80 + "\n")

def run_experiment_from_config(experiment_id, config_path='config/experiments.yaml'):
    """Ejecuta un experimento desde la configuración YAML."""
    print(f"\n{'='*60}")
    print(f"Ejecutando experimento: {experiment_id}")
    print(f"{'='*60}\n")
    
    temp_env = f'.env.{experiment_id}'
    create_env_from_experiment(experiment_id, config_path, temp_env)
    
    print(f"Archivo de configuración creado: {temp_env}")
    
    import shutil
    shutil.copy(temp_env, '.env')
    print("Configuración aplicada a .env")
    
    success = run_single_experiment(experiment_id)
    
    print(f"Archivo de configuración guardado: {temp_env}")
    
    if success:
        print(f"\n✓ Experimento {experiment_id} completado")
    else:
        print(f"\n✗ Experimento {experiment_id} falló")
    
    return success

def run_all_experiments_from_yaml(config_path='config/experiments.yaml'):
    config = load_experiments_config(config_path)
    experiments = list(config['experiments'].keys())
    
    print(f"\n{'='*60}")
    print(f"Ejecutando {len(experiments)} experimentos")
    print(f"{'='*60}\n")
    
    results = []
    for i, exp_id in enumerate(experiments, 1):
        print(f"\n[{i}/{len(experiments)}] Iniciando {exp_id}...")
        try:
            success = run_experiment_from_config(exp_id, config_path)
            results.append({'experiment': exp_id, 'success': success})
        except Exception as e:
            print(f"✗ Error en {exp_id}: {e}")
            results.append({'experiment': exp_id, 'success': False, 'error': str(e)})
            continue
    
    print(f"\n{'='*60}")
    print(f"Resumen de experimentos:")
    print(f"{'='*60}")
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"  {status} {result['experiment']}")
    print(f"\nExitosos: {sum(1 for r in results if r['success'])}/{len(results)}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--yaml':
            run_all_experiments_from_yaml()
        elif sys.argv[1] == '--experiment' and len(sys.argv) > 2:
            exp_ids = sys.argv[2:]
            print(f"\nEjecutando {len(exp_ids)} experimento(s): {', '.join(exp_ids)}\n")
            
            for exp_id in exp_ids:
                run_experiment_from_config(exp_id)
                print()  
        else:
            print("Uso:")
            print("  python run_experiments.py --yaml                              # Ejecutar todos desde YAML")
            print("  python run_experiments.py --experiment <exp_id> [exp_id2...] # Ejecutar uno o más específicos")
            print("  python run_experiments.py                                     # Ejecutar todos (modo legacy)")
    else:
        run_all_experiments()
