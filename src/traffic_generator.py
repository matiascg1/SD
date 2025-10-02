import time
import random
from src.utils import load_dataset, select_random_question, calculate_delay
from src.cache_system import CacheSystem
from src.llm_connector import LLMConnector
from src.score_calculator import ScoreCalculator
from src.data_store import DataStore
from config import settings
from datetime import datetime

class TrafficGenerator:
    def __init__(self):
        self.dataset = load_dataset()
        if self.dataset is None or self.dataset.empty:
            raise ValueError("No se pudo cargar el dataset. Verifica la ruta en .env")
        
        self.cache = CacheSystem()
        self.llm = LLMConnector()
        self.scorer = ScoreCalculator()
        self.store = DataStore()
        
        self.distribution_type = settings.TRAFFIC_DISTRIBUTION_TYPE
        self.lambda_param = settings.TRAFFIC_LAMBDA
        self.num_requests = settings.TRAFFIC_NUM_REQUESTS
        self.max_delay = settings.TRAFFIC_MAX_DELAY_SECONDS
        
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'llm_errors': 0,
            'successful_responses': 0
        }
        
        print(f"TrafficGenerator inicializado:")
        print(f"  - Distribución: {self.distribution_type}")
        print(f"  - Lambda: {self.lambda_param}")
        print(f"  - Número de requests: {self.num_requests}")
        print(f"  - Delay máximo: {self.max_delay}s")

    def process_query(self, question: dict):
        question_id = question['question_id']
        self.stats['total_requests'] += 1
        
        cached_result = self.cache.get(question_id)
        
        if cached_result:
            self.stats['cache_hits'] += 1
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Cache HIT para {question_id}")
            existing_result = self.store.get_result_by_question_id(question_id)
            if existing_result:
                existing_result['request_count'] = existing_result.get('request_count', 1) + 1
                self.store.save_query_result(existing_result)
        else:
            self.stats['cache_misses'] += 1
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Cache MISS para {question_id} - Consultando LLM...")
            
            llm_answer = self.llm.generate_answer(
                question['title'],
                question['content']
            )
            
            if llm_answer.startswith("[Error:"):
                self.stats['llm_errors'] += 1
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Error del LLM para {question_id}: {llm_answer}")
                return
            
            self.stats['successful_responses'] += 1
            
            quality_score = self.scorer.calculate_score(
                question['original_best_answer'],
                llm_answer
            )
            
            result = {
                'question_id': question_id,
                'question_title': question['title'],
                'question_content': question['content'],
                'original_best_answer': question['original_best_answer'],
                'llm_generated_answer': llm_answer,
                'quality_score': quality_score
            }
            
            self.store.save_query_result(result)
            
            self.cache.set(question_id, result)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Procesado {question_id} - Score: {quality_score}")

    def print_stats(self):
        print(f"\n{'='*60}")
        print("ESTADÍSTICAS DEL SISTEMA")
        print(f"{'='*60}")
        print(f"Total de requests: {self.stats['total_requests']}")
        print(f"Cache hits: {self.stats['cache_hits']} ({self.stats['cache_hits']/max(1, self.stats['total_requests'])*100:.2f}%)")
        print(f"Cache misses: {self.stats['cache_misses']} ({self.stats['cache_misses']/max(1, self.stats['total_requests'])*100:.2f}%)")
        print(f"Respuestas exitosas del LLM: {self.stats['successful_responses']}")
        print(f"Errores del LLM: {self.stats['llm_errors']}")
        print(f"Tamaño de caché: {self.cache.size()}")
        print(f"Registros en DB: {len(self.store.get_all_results())}")
        print(f"{'='*60}\n")

    def run(self):
        print(f"\n{'='*60}")
        print(f"Iniciando generación de tráfico...")
        print(f"{'='*60}\n")
        
        for i in range(self.num_requests):
            question = select_random_question(self.dataset)
            
            if question is None:
                print("Error: No se pudo seleccionar una pregunta. Saltando...")
                continue
            
            try:
                self.process_query(question)
            except Exception as e:
                print(f"Error procesando consulta {i+1}: {e}")
                import traceback
                traceback.print_exc()
            
            if i < self.num_requests - 1:
                delay = calculate_delay(
                    self.distribution_type,
                    self.lambda_param,
                    self.max_delay
                )
                time.sleep(delay)
            
            if (i + 1) % 50 == 0:
                self.print_stats()
        
        print(f"\n{'='*60}")
        print(f"Generación de tráfico completada!")
        print(f"{'='*60}")
        self.print_stats()


if __name__ == "__main__":
    print("--- Ejecutando Traffic Generator ---")
    try:
        generator = TrafficGenerator()
        generator.run()
    except Exception as e:
        print(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
