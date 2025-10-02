from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ScoreCalculator:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            max_features=1000
        )
        print("ScoreCalculator inicializado con TF-IDF y similitud de coseno.")

    def calculate_similarity(self, original_answer: str, llm_answer: str) -> float:
        try:
            if not original_answer or not llm_answer:
                print("Advertencia: Una de las respuestas está vacía. Retornando score 0.")
                return 0.0

            tfidf_matrix = self.vectorizer.fit_transform([original_answer, llm_answer])
            
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            similarity = max(0.0, min(1.0, similarity))
            
            return round(similarity, 4)
        except Exception as e:
            print(f"Error al calcular similitud: {e}")
            return 0.0

    def calculate_score(self, original_answer: str, llm_answer: str) -> float:
        return self.calculate_similarity(original_answer, llm_answer)


if __name__ == "__main__":
    print("--- Probando src/score_calculator.py ---")
    
    calculator = ScoreCalculator()
    
    original_1 = "Paris is the capital of France."
    llm_1 = "The capital of France is Paris."
    score_1 = calculator.calculate_score(original_1, llm_1)
    print(f"\nPrueba 1 - Respuestas similares:")
    print(f"Original: {original_1}")
    print(f"LLM: {llm_1}")
    print(f"Score: {score_1}")
    assert score_1 > 0.5, "El score debería ser alto para respuestas similares."
    
    original_2 = "Paris is the capital of France."
    llm_2 = "The sun is a star in our solar system."
    score_2 = calculator.calculate_score(original_2, llm_2)
    print(f"\nPrueba 2 - Respuestas diferentes:")
    print(f"Original: {original_2}")
    print(f"LLM: {llm_2}")
    print(f"Score: {score_2}")
    assert score_2 < 0.5, "El score debería ser bajo para respuestas diferentes."
    
    original_3 = "Photosynthesis is the process by which plants convert light into energy."
    llm_3 = "Photosynthesis is the process by which plants convert light into energy."
    score_3 = calculator.calculate_score(original_3, llm_3)
    print(f"\nPrueba 3 - Respuestas idénticas:")
    print(f"Original: {original_3}")
    print(f"LLM: {llm_3}")
    print(f"Score: {score_3}")
    assert score_3 > 0.9, "El score debería ser muy alto para respuestas idénticas."
    
    print("\nPruebas de ScoreCalculator completadas exitosamente.")
