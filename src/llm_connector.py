import google.generativeai as genai
import ollama
from config import settings
import os
import time
import random

class LLMConnector:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.upper()
        self.model = None
        self.max_retries = 5
        self.base_delay = 1
        self.max_delay = 30
        self.last_request_time = 0
        self.min_request_interval = 3.0
        self.consecutive_errors = 0
        self.max_consecutive_errors = 3
        self.groq_client = None
        self.ollama_client = None

        if self.provider == "GEMINI":
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY no configurada en .env para el proveedor GEMINI.")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
            print(f"LLMConnector inicializado: Google Gemini, Modelo: {settings.GEMINI_MODEL_NAME}")
            print(f"Rate limiting habilitado: {self.min_request_interval}s entre requests")
            
        elif self.provider == "OLLAMA":
            self.min_request_interval = 0 
            self.ollama_host = settings.OLLAMA_HOST
            self.ollama_model_name = settings.OLLAMA_MODEL_NAME
            self.ollama_client = ollama.Client(host=self.ollama_host)
            try:
                models = self.ollama_client.list()
                if not any(m['name'].startswith(self.ollama_model_name) for m in models['models']):
                    print(f"Advertencia: El modelo '{self.ollama_model_name}' no está disponible en Ollama.")
                    print(f"Por favor, ejecuta: ollama pull {self.ollama_model_name}")
                print(f"LLMConnector inicializado: Ollama (Local), Host: {self.ollama_host}, Modelo: {self.ollama_model_name}")
                print("Sin límites de rate - Modelo local")
            except Exception as e:
                print(f"Error al conectar con Ollama: {e}")
                print("Asegúrate de que Ollama esté corriendo: ollama serve")
                
        elif self.provider == "GROQ":
            try:
                from groq import Groq
            except ImportError:
                raise ImportError("La librería 'groq' no está instalada. Ejecuta: pip install groq")
            
            api_key = settings.GROQ_API_KEY
            if not api_key:
                raise ValueError("GROQ_API_KEY no configurada en .env para el proveedor GROQ.")
            self.groq_client = Groq(api_key=api_key)
            self.groq_model_name = settings.GROQ_MODEL_NAME
            self.min_request_interval = 0.5  
            print(f"LLMConnector inicializado: Groq, Modelo: {self.groq_model_name}")
            print(f"Rate limiting habilitado: {self.min_request_interval}s entre requests")
            print("Groq ofrece límites generosos en su tier gratuito")
            
        else:
            raise ValueError(f"Proveedor de LLM '{self.provider}' no soportado. Usa 'GEMINI', 'OLLAMA' o 'GROQ'.")

    def _wait_for_rate_limit(self):
        if self.min_request_interval == 0:
            return
            
        if self.consecutive_errors >= self.max_consecutive_errors:
            extra_wait = 30
            print(f"[Rate Limit] Detectados {self.consecutive_errors} errores consecutivos. Pausa extendida de {extra_wait}s...")
            time.sleep(extra_wait)
            self.consecutive_errors = 0
        
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def _handle_retry_with_backoff(self, attempt: int) -> float:
        delay = min(self.base_delay * (2.5 ** attempt), self.max_delay)
        jitter = delay * 0.20 * (random.random() * 2 - 1)
        final_delay = max(2, delay + jitter)
        
        print(f"[Retry {attempt + 1}/{self.max_retries}] Esperando {final_delay:.2f}s antes de reintentar...")
        return final_delay

    def generate_answer(self, question_title: str, question_content: str) -> str:
        prompt = f"Question: {question_title}\n\nDetails: {question_content}\n\nPlease provide a concise and helpful answer:"

        for attempt in range(self.max_retries):
            try:
                if self.provider in ["GEMINI", "GROQ"]:
                    self._wait_for_rate_limit()
                
                if self.provider == "GEMINI":
                    response = self.model.generate_content(prompt)
                    self.consecutive_errors = 0
                    return response.text.strip()
                    
                elif self.provider == "OLLAMA":
                    response = self.ollama_client.chat(
                        model=self.ollama_model_name,
                        messages=[{'role': 'user', 'content': prompt}]
                    )
                    self.consecutive_errors = 0
                    return response['message']['content'].strip()
                    
                elif self.provider == "GROQ":
                    response = self.groq_client.chat.completions.create(
                        model=self.groq_model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=1024
                    )
                    self.consecutive_errors = 0
                    return response.choices[0].message.content.strip()
                    
            except Exception as e:
                self.consecutive_errors += 1
                error_str = str(e).lower()
                
                if '429' in error_str or 'rate limit' in error_str or 'quota' in error_str:
                    if attempt < self.max_retries - 1:
                        delay = self._handle_retry_with_backoff(attempt)
                        time.sleep(delay)
                        continue
                    else:
                        print(f"Error 429: Se alcanzó el límite de rate limit después de {self.max_retries} intentos.")
                        return "[Error: Rate limit excedido - Por favor espera unos minutos e intenta de nuevo]"
                
                elif '500' in error_str or 'internal server error' in error_str:
                    if attempt < self.max_retries - 1:
                        print(f"Error del servidor (500). Reintentando...")
                        time.sleep(self.base_delay * (attempt + 1))
                        continue
                    else:
                        return "[Error: Error del servidor - No se pudo generar respuesta]"
                
                elif 'connection' in error_str or 'timeout' in error_str:
                    if attempt < self.max_retries - 1:
                        print(f"Error de conexión. Reintentando...")
                        time.sleep(self.base_delay)
                        continue
                    else:
                        return "[Error: Error de conexión - Verifica tu conexión a internet]"
                
                else:
                    print(f"Error al generar respuesta con {self.provider}: {e}")
                    return f"[Error: No se pudo generar respuesta - {str(e)}]"
        
        return "[Error: No se pudo generar respuesta después de múltiples intentos]"

if __name__ == "__main__":
    print("--- Probando src/llm_connector.py ---")

    try:
        llm = LLMConnector()
        
        test_question_title = "What is the capital of France?"
        test_question_content = "I need to know for my geography class."
        
        print(f"\nGenerando respuesta para: '{test_question_title}'")
        answer = llm.generate_answer(test_question_title, test_question_content)
        print(f"Respuesta del LLM: {answer}")
        
        assert len(answer) > 0, "La respuesta no debería estar vacía."
        print("\nPrueba de LLMConnector completada exitosamente.")
    except Exception as e:
        print(f"\nError en la prueba: {e}")
        print("Asegúrate de tener configurado correctamente el .env y el proveedor de LLM.")
