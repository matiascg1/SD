import redis
import json
from config import settings
from datetime import datetime

class CacheSystem:
    def __init__(self, host=settings.CACHE_HOST, port=settings.CACHE_PORT, db=settings.CACHE_DB,
                 ttl_seconds=settings.CACHE_TTL_SECONDS, max_size=settings.CACHE_MAX_SIZE,
                 policy=settings.CACHE_POLICY):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.policy = policy.upper() 
        print(f"CacheSystem inicializado: Host={host}, Port={port}, DB={db}, TTL={ttl_seconds}s, MaxSize={max_size}, Policy={policy}")

        try:
            self.client.ping()
            print("Conexión a Redis exitosa.")
        except redis.exceptions.ConnectionError as e:
            print(f"Error al conectar a Redis: {e}. Asegúrate de que Redis esté corriendo.")

    def _apply_lru(self):
        if self.client.dbsize() > self.max_size:
            print(f"Caché excedió el tamaño máximo ({self.max_size}). Aplicando política {self.policy} (delegado a Redis).")

    def get(self, key: str):
        value = self.client.get(key)
        if value:

            print(f"[{datetime.now().strftime('%H:%M:%S')}] CACHE HIT para key: {key}")
            return json.loads(value)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] CACHE MISS para key: {key}")
        return None

    def set(self, key: str, value: dict):
        try:
            json_value = json.dumps(value)
            self.client.setex(key, self.ttl_seconds, json_value)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Elemento guardado en caché para key: {key} con TTL: {self.ttl_seconds}s")
        except Exception as e:
            print(f"Error al guardar en caché para key {key}: {e}")

    def invalidate(self, key: str):
        self.client.delete(key)
        print(f"Elemento invalidado de caché para key: {key}")

    def clear(self):
        self.client.flushdb()
        print("Caché limpiada.")

    def size(self):
        return self.client.dbsize()


if __name__ == "__main__":
    print("--- Probando src/cache_system.py ---")

    cache = CacheSystem()
    cache.clear() 

    key1 = "q_test_cache_001"
    value1 = {"answer": "Cached answer 1", "score": 0.85, "timestamp": datetime.now().isoformat()}
    cache.set(key1, value1)
    retrieved_value = cache.get(key1)
    print(f"Recuperado (Hit): {retrieved_value}")
    assert retrieved_value['answer'] == value1['answer'], "El valor recuperado no coincide."

    key2 = "q_test_cache_002"
    retrieved_value_miss = cache.get(key2)
    print(f"Recuperado (Miss): {retrieved_value_miss}")
    assert retrieved_value_miss is None, "No debería haber recuperado nada para una clave inexistente."

    value2 = {"answer": "Cached answer 2", "score": 0.90, "timestamp": datetime.now().isoformat()}
    cache.set(key2, value2)

    print(f"Tamaño actual de la caché: {cache.size()}")
    assert cache.size() == 2, "El tamaño de la caché no es el esperado."

    import time
    print(f"\nEsperando {settings.CACHE_TTL_SECONDS + 1} segundos para que el TTL expire...")
    