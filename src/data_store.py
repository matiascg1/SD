import sqlite3
import pandas as pd
from config import settings
import os
from datetime import datetime

class DataStore:
    def __init__(self, db_path=settings.SQLITE_DB_PATH):
        self.db_path = db_path
        self._ensure_data_directory_exists()
        self._create_table_if_not_exists()
        print(f"DataStore inicializado con base de datos: {self.db_path}")

    def _ensure_data_directory_exists(self):
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_table_if_not_exists(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id TEXT NOT NULL,
                question_title TEXT,
                question_content TEXT,
                original_best_answer TEXT,
                llm_generated_answer TEXT,
                quality_score REAL,
                request_count INTEGER DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(question_id) ON CONFLICT REPLACE
            );
        """)
        conn.commit()
        conn.close()

    def save_query_result(self, result: dict):
        conn = self._get_connection()
        cursor = conn.cursor()

        question_id = result.get('question_id')
        current_timestamp = datetime.now().isoformat()

        # Primero, intenta ver si ya existe esta question_id
        cursor.execute("SELECT request_count FROM query_results WHERE question_id = ?", (question_id,))
        existing_record = cursor.fetchone()

        if existing_record:
            # Si existe, actualiza el request_count y los otros campos
            new_request_count = existing_record[0] + 1
            cursor.execute("""
                UPDATE query_results
                SET
                    question_title = ?,
                    question_content = ?,
                    original_best_answer = ?,
                    llm_generated_answer = ?,
                    quality_score = ?,
                    request_count = ?,
                    timestamp = ?
                WHERE question_id = ?;
            """, (
                result.get('question_title'),
                result.get('question_content'),
                result.get('original_best_answer'),
                result.get('llm_generated_answer'),
                result.get('quality_score'),
                new_request_count,
                current_timestamp,
                question_id
            ))
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Resultado actualizado para Q_ID: {question_id}. Contador: {new_request_count}")
        else:
            # Si no existe, inserta un nuevo registro
            cursor.execute("""
                INSERT INTO query_results (
                    question_id, question_title, question_content,
                    original_best_answer, llm_generated_answer,
                    quality_score, request_count, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                question_id,
                result.get('question_title'),
                result.get('question_content'),
                result.get('original_best_answer'),
                result.get('llm_generated_answer'),
                result.get('quality_score'),
                1, 
                current_timestamp
            ))
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Nuevo resultado guardado para Q_ID: {question_id}")

        conn.commit()
        conn.close()

    def get_all_results(self) -> pd.DataFrame:
        conn = self._get_connection()
        df = pd.read_sql_query("SELECT * FROM query_results;", conn)
        conn.close()
        return df

    def get_result_by_question_id(self, question_id: str) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM query_results WHERE question_id = ?", (question_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            # Obtener nombres de columnas para crear un diccionario
            col_names = [description[0] for description in cursor.description]
            return dict(zip(col_names, row))
        return None

if __name__ == "__main__":
    print("--- Probando src/data_store.py ---")
    store = DataStore()

    # Eliminar el archivo de la DB para un test limpio
    if os.path.exists(settings.SQLITE_DB_PATH):
        os.remove(settings.SQLITE_DB_PATH)
        print(f"Archivo de DB '{settings.SQLITE_DB_PATH}' eliminado para una prueba limpia.")
        store = DataStore() # Reiniciar para crear la tabla de nuevo

    # Prueba de guardar un nuevo resultado
    new_result = {
        "question_id": "q_test_001",
        "question_title": "What is the capital of France?",
        "question_content": "I need to know for my geography class.",
        "original_best_answer": "Paris is the capital of France.",
        "llm_generated_answer": "The capital of France is Paris.",
        "quality_score": 0.95
    }
    store.save_query_result(new_result)

    # Prueba de actualizar un resultado existente 
    updated_result = {
        "question_id": "q_test_001",
        "question_title": "What is the capital of France? (Updated)",
        "question_content": "I need to know for my geography class.",
        "original_best_answer": "Paris is the capital of France.",
        "llm_generated_answer": "Paris is indeed the capital.",
        "quality_score": 0.98 # Mejor score
    }
    store.save_query_result(updated_result)

    # Prueba de guardar otro nuevo resultado
    new_result_2 = {
        "question_id": "q_test_002",
        "question_title": "How does photosynthesis work?",
        "question_content": "Explain the process simply.",
        "original_best_answer": "Plants use sunlight, water, and CO2 to make food.",
        "llm_generated_answer": "Photosynthesis is the process by which green plants convert light energy into chemical energy.",
        "quality_score": 0.88
    }
    store.save_query_result(new_result_2)

    print("\nTodos los resultados almacenados:")
    all_results_df = store.get_all_results()
    print(all_results_df)

    print(f"\nNúmero de registros en la DB: {len(all_results_df)}")
    assert len(all_results_df) == 2, "Debería haber 2 registros únicos."
    assert all_results_df[all_results_df['question_id'] == 'q_test_001']['request_count'].iloc[0] == 2, "request_count debería ser 2."
    print("Pruebas de DataStore pasadas exitosamente.")
