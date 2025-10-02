import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.traffic_generator import TrafficGenerator
from config import settings

def print_banner():
    print("\n" + "="*70)
    print(" "*15 + "SISTEMA DE ANÁLISIS DE PREGUNTAS Y RESPUESTAS")
    print(" "*20 + "Yahoo! Answers Dataset + LLM")
    print("="*70)
    print(f"Fecha de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

def print_configuration():
    print("CONFIGURACIÓN DEL SISTEMA:")
    print("-" * 70)
    print(f"Dataset: {settings.DATA_PATH}")
    print(f"LLM Provider: {settings.LLM_PROVIDER}")
    if settings.LLM_PROVIDER.upper() == "GEMINI":
        print(f"  - Modelo: {settings.GEMINI_MODEL_NAME}")
    elif settings.LLM_PROVIDER.upper() == "OLLAMA":
        print(f"  - Host: {settings.OLLAMA_HOST}")
        print(f"  - Modelo: {settings.OLLAMA_MODEL_NAME}")
    print(f"\nCaché:")
    print(f"  - Host: {settings.CACHE_HOST}:{settings.CACHE_PORT}")
    print(f"  - Política: {settings.CACHE_POLICY}")
    print(f"  - Tamaño máximo: {settings.CACHE_MAX_SIZE}")
    print(f"  - TTL: {settings.CACHE_TTL_SECONDS}s")
    print(f"\nAlmacenamiento:")
    print(f"  - Tipo: {settings.DB_TYPE}")
    print(f"  - Path: {settings.SQLITE_DB_PATH}")
    print(f"\nGenerador de Tráfico:")
    print(f"  - Distribución: {settings.TRAFFIC_DISTRIBUTION_TYPE}")
    print(f"  - Lambda: {settings.TRAFFIC_LAMBDA}")
    print(f"  - Número de requests: {settings.TRAFFIC_NUM_REQUESTS}")
    print(f"  - Delay máximo: {settings.TRAFFIC_MAX_DELAY_SECONDS}s")
    print("-" * 70 + "\n")

def main():
    try:
        print_banner()
        print_configuration()
        
        print("Inicializando componentes del sistema...\n")
        generator = TrafficGenerator()
        
        print("\nTodos los componentes inicializados correctamente.")
        print("Presiona Ctrl+C para detener el sistema en cualquier momento.\n")
        
        generator.run()
        
        print("\n" + "="*70)
        print("Sistema finalizado exitosamente.")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nSistema interrumpido por el usuario.")
        print("Cerrando conexiones...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError fatal en el sistema: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
