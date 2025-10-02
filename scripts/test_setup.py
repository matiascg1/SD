import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    print("1. Verificando imports de módulos...")
    try:
        from config import settings
        from src.cache_system import CacheSystem
        from src.llm_connector import LLMConnector
        from src.score_calculator import ScoreCalculator
        from src.data_store import DataStore
        from src.utils import load_dataset
        print("   ✓ Todos los módulos se importaron correctamente")
        return True
    except ImportError as e:
        print(f"   ✗ Error al importar módulos: {e}")
        return False

def test_dataset():
    print("\n2. Verificando dataset...")
    try:
        from src.utils import load_dataset
        from config import settings
        
        if not os.path.exists(settings.DATA_PATH):
            print(f"   ✗ Dataset no encontrado en: {settings.DATA_PATH}")
            print(f"   → Descarga el dataset de Yahoo! Answers y colócalo en {settings.DATA_PATH}")
            return False
        
        dataset = load_dataset()
        if dataset is None or dataset.empty:
            print("   ✗ El dataset está vacío o no se pudo cargar")
            return False
        
        print(f"   ✓ Dataset cargado correctamente: {len(dataset)} registros")
        return True
    except Exception as e:
        print(f"   ✗ Error al cargar dataset: {e}")
        return False

def test_redis():
    print("\n3. Verificando conexión a Redis...")
    try:
        from src.cache_system import CacheSystem
        cache = CacheSystem()
        cache.client.ping()
        print(f"   ✓ Conexión a Redis exitosa")
        return True
    except Exception as e:
        print(f"   ✗ Error al conectar a Redis: {e}")
        print("   → Asegúrate de que Redis esté corriendo (docker-compose up redis)")
        return False

def test_llm():
    print("\n4. Verificando configuración del LLM...")
    try:
        from config import settings
        from src.llm_connector import LLMConnector
        
        if settings.LLM_PROVIDER.upper() == "GEMINI":
            if not settings.GEMINI_API_KEY:
                print("   ✗ GEMINI_API_KEY no está configurada en .env")
                return False
            print(f"   ✓ Gemini configurado: {settings.GEMINI_MODEL_NAME}")
        elif settings.LLM_PROVIDER.upper() == "OLLAMA":
            print(f"   ✓ Ollama configurado: {settings.OLLAMA_HOST} - {settings.OLLAMA_MODEL_NAME}")
        else:
            print(f"   ✗ LLM_PROVIDER desconocido: {settings.LLM_PROVIDER}")
            return False
        
        llm = LLMConnector()
        print("   ✓ LLM Connector inicializado correctamente")
        return True
    except Exception as e:
        print(f"   ✗ Error al configurar LLM: {e}")
        return False

def test_database():
    print("\n5. Verificando base de datos...")
    try:
        from src.data_store import DataStore
        store = DataStore()
        print(f"   ✓ Base de datos inicializada: {store.db_path}")
        return True
    except Exception as e:
        print(f"   ✗ Error al inicializar base de datos: {e}")
        return False

def test_score_calculator():
    print("\n6. Verificando calculador de scores...")
    try:
        from src.score_calculator import ScoreCalculator
        calculator = ScoreCalculator()
        
        score = calculator.calculate_score(
            "Paris is the capital of France",
            "The capital of France is Paris"
        )
        
        if 0 <= score <= 1:
            print(f"   ✓ Score Calculator funciona correctamente (score de prueba: {score})")
            return True
        else:
            print(f"   ✗ Score fuera de rango: {score}")
            return False
    except Exception as e:
        print(f"   ✗ Error en Score Calculator: {e}")
        return False

def main():
    print("="*70)
    print(" "*15 + "VERIFICACIÓN DE CONFIGURACIÓN DEL SISTEMA")
    print("="*70)
    
    tests = [
        test_imports,
        test_dataset,
        test_redis,
        test_llm,
        test_database,
        test_score_calculator
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Pruebas pasadas: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ¡Todos los componentes están configurados correctamente!")
        print("  Puedes ejecutar el sistema con: docker-compose up --build")
    else:
        print("\n✗ Algunos componentes necesitan configuración.")
        print("  Revisa los errores arriba y corrige la configuración.")
    
    print("="*70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
