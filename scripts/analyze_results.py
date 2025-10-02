import sys
import os
import sqlite3
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

def print_header(title):
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

def get_connection():
    if not os.path.exists(settings.SQLITE_DB_PATH):
        print(f"Error: Base de datos no encontrada en {settings.SQLITE_DB_PATH}")
        print("Ejecuta el sistema primero para generar datos.")
        sys.exit(1)
    return sqlite3.connect(settings.SQLITE_DB_PATH)

def general_statistics():
    print_header("ESTADÍSTICAS GENERALES")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM query_results")
    total_unique = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(request_count) FROM query_results")
    total_requests = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(quality_score) FROM query_results")
    avg_score = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(quality_score), MIN(quality_score) FROM query_results")
    max_score, min_score = cursor.fetchone()
    
    cache_hits = total_requests - total_unique if total_requests else 0
    cache_hit_rate = (cache_hits / total_requests * 100) if total_requests else 0
    
    print(f"\nConsultas únicas procesadas: {total_unique}")
    print(f"Total de consultas (con repeticiones): {total_requests}")
    print(f"Cache hits: {cache_hits} ({cache_hit_rate:.2f}%)")
    print(f"\nQuality Score:")
    print(f"  - Promedio: {avg_score:.4f}")
    print(f"  - Máximo: {max_score:.4f}")
    print(f"  - Mínimo: {min_score:.4f}")
    
    conn.close()

def top_questions():
    print_header("TOP 10 PREGUNTAS MÁS CONSULTADAS")
    
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT question_title, request_count, quality_score
        FROM query_results
        ORDER BY request_count DESC
        LIMIT 10
    """, conn)
    
    if df.empty:
        print("\nNo hay datos disponibles.")
    else:
        print("\n")
        for idx, row in df.iterrows():
            print(f"{idx+1}. [{row['request_count']} consultas] Score: {row['quality_score']:.4f}")
            print(f"   {row['question_title'][:80]}...")
            print()
    
    conn.close()

def best_answers():
    print_header("TOP 10 RESPUESTAS CON MEJOR SCORE")
    
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT question_title, quality_score, llm_generated_answer
        FROM query_results
        ORDER BY quality_score DESC
        LIMIT 10
    """, conn)
    
    if df.empty:
        print("\nNo hay datos disponibles.")
    else:
        print("\n")
        for idx, row in df.iterrows():
            print(f"{idx+1}. Score: {row['quality_score']:.4f}")
            print(f"   Pregunta: {row['question_title'][:70]}...")
            print(f"   Respuesta: {row['llm_generated_answer'][:100]}...")
            print()
    
    conn.close()

def score_distribution():
    print_header("DISTRIBUCIÓN DE QUALITY SCORES")
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT quality_score FROM query_results", conn)
    
    if df.empty:
        print("\nNo hay datos disponibles.")
    else:
        # Crear rangos de scores
        bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
        labels = ['0.0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0']
        df['score_range'] = pd.cut(df['quality_score'], bins=bins, labels=labels, include_lowest=True)
        
        distribution = df['score_range'].value_counts().sort_index()
        
        print("\n")
        for range_label, count in distribution.items():
            percentage = (count / len(df)) * 100
            bar = '█' * int(percentage / 2)
            print(f"{range_label}: {bar} {count} ({percentage:.1f}%)")
    
    conn.close()

def export_to_csv():
    print_header("EXPORTAR RESULTADOS")
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM query_results", conn)
    
    output_file = "data/results_export.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\nResultados exportados a: {output_file}")
    print(f"Total de registros: {len(df)}")
    
    conn.close()

def main():
    print("\n" + "="*70)
    print(" "*15 + "ANÁLISIS DE RESULTADOS")
    print(" "*10 + "Sistema de Análisis Yahoo! Answers")
    print("="*70)
    
    try:
        general_statistics()
        top_questions()
        best_answers()
        score_distribution()
        
        print("\n")
        export = input("¿Deseas exportar los resultados a CSV? (s/n): ")
        if export.lower() in ['s', 'si', 'yes', 'y']:
            export_to_csv()
        
        print("\n" + "="*70)
        print("Análisis completado")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\nError durante el análisis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
