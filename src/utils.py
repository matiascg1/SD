import pandas as pd
import numpy as np
from config import settings
import random
import os

def load_dataset(path=settings.DATA_PATH):
    try:
        df = pd.read_csv(path, header=None, names=['class_index', 'title', 'content', 'best_answer'])
        df.dropna(subset=['title', 'content', 'best_answer'], inplace=True)
        df['class_index'] = df['class_index'].astype(int)
        print(f"Dataset cargado exitosamente desde {path}. Shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"Error: El archivo del dataset no se encontró en {path}. Asegúrate de que '{os.path.basename(path)}' esté en la carpeta '{os.path.dirname(path)}'.")
        return None
    except Exception as e:
        print(f"Ocurrió un error al cargar el dataset: {e}")
        return None

def select_random_question(dataset: pd.DataFrame) -> dict:
    if dataset is None or dataset.empty:
        return None

    random_row = dataset.sample(n=1).iloc[0]
    question_id = f"q_{random_row.name}"

    return {
        "question_id": question_id,
        "title": random_row['title'],
        "content": random_row['content'],
        "original_best_answer": random_row['best_answer']
    }

def calculate_delay(distribution_type: str, lambda_param: float, max_delay: float) -> float:
    if distribution_type.upper() == 'POISSON':
        delay = random.expovariate(lambda_param)
    elif distribution_type.upper() == 'EXPONENTIAL':
        delay = random.expovariate(lambda_param)
    elif distribution_type.upper() == 'UNIFORM':
        delay = random.uniform(0.1, max_delay) 
    else:
        print(f"Advertencia: Distribución '{distribution_type}' no reconocida. Usando uniforme.")
        delay = random.uniform(0.1, max_delay)

    return max(0.1, min(delay, max_delay))


if __name__ == "__main__":
    print("--- Probando src/utils.py ---")
    dataset = load_dataset()
    if dataset is not None:
        print("\nSeleccionando una pregunta aleatoria:")
        question = select_random_question(dataset)
        if question:
            print(f"ID: {question['question_id']}")
            print(f"Título: {question['title']}")
            print(f"Contenido: {question['content'][:100]}...") 
            print(f"Respuesta Original: {question['original_best_answer'][:100]}...")

        print("\nCalculando retrasos con diferentes distribuciones:")
        print(f"Poisson (lambda={settings.TRAFFIC_LAMBDA}): {calculate_delay('POISSON', settings.TRAFFIC_LAMBDA, 5):.2f}s")
        print(f"Exponential (lambda={settings.TRAFFIC_LAMBDA}): {calculate_delay('EXPONENTIAL', settings.TRAFFIC_LAMBDA, 5):.2f}s")
        print(f"Uniform (max_delay=5): {calculate_delay('UNIFORM', 0, 5):.2f}s")
