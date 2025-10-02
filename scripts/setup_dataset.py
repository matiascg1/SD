import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

def check_dataset():
    print("="*70)
    print(" "*20 + "VERIFICACIÓN DEL DATASET")
    print("="*70 + "\n")
    
    if not os.path.exists(settings.DATA_PATH):
        print(f"❌ Dataset no encontrado en: {settings.DATA_PATH}\n")
        print("Para obtener el dataset:")
        print("1. Descarga desde Kaggle:")
        print("   https://www.kaggle.com/datasets/jarupula/yahoo-answers-dataset")
        print("\n2. O usa el dataset oficial de Yahoo! Answers:")
        print("   https://webscope.sandbox.yahoo.com/catalog.php?datatype=l")
        print("\n3. Coloca el archivo test.csv en el directorio data/")
        return False
    
    print(f"✓ Dataset encontrado: {settings.DATA_PATH}\n")
    
    try:
        df = pd.read_csv(settings.DATA_PATH, header=None, nrows=5)
        print(f"Primeras filas del dataset:")
        print("-"*70)
        print(df.head())
        print("-"*70)
        
        if df.shape[1] < 4:
            print(f"\n⚠️  Advertencia: El dataset tiene {df.shape[1]} columnas.")
            print("   Se esperan 4 columnas: class_index, title, content, best_answer")
            return False
        
        print(f"\n✓ Formato correcto: {df.shape[1]} columnas")
        
        total_rows = sum(1 for _ in open(settings.DATA_PATH)) - 1  
        print(f"✓ Total de registros: {total_rows:,}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al leer el dataset: {e}")
        return False

def create_sample_dataset():
    print("\n" + "="*70)
    print("CREAR DATASET DE MUESTRA")
    print("="*70 + "\n")
    
    sample_data = [
        [1, "What is Python?", "I want to learn programming. What is Python?", 
         "Python is a high-level programming language known for its simplicity and readability."],
        [2, "Best pizza in NYC?", "Where can I find the best pizza in New York City?",
         "Try Joe's Pizza in Greenwich Village or Di Fara Pizza in Brooklyn."],
        [3, "How to learn guitar?", "I'm a beginner. How should I start learning guitar?",
         "Start with basic chords, practice daily, and use online tutorials or take lessons."],
        [4, "What is machine learning?", "Can someone explain machine learning in simple terms?",
         "Machine learning is a type of AI that allows computers to learn from data without being explicitly programmed."],
        [5, "Best books for entrepreneurs?", "What books should every entrepreneur read?",
         "The Lean Startup by Eric Ries and Zero to One by Peter Thiel are excellent choices."],
    ]
    
    df = pd.DataFrame(sample_data, columns=['class_index', 'title', 'content', 'best_answer'])
    
    sample_path = "data/sample_test.csv"
    os.makedirs("data", exist_ok=True)
    df.to_csv(sample_path, index=False, header=False)
    
    print(f"✓ Dataset de muestra creado: {sample_path}")
    print(f"  Contiene {len(df)} preguntas de ejemplo")
    print("\nPara usar este dataset de muestra, actualiza DATA_PATH en .env:")
    print(f"  DATA_PATH={sample_path}")
    
    return True

def main():
    if check_dataset():
        print("\n" + "="*70)
        print("✓ Dataset verificado correctamente")
        print("="*70 + "\n")
        return True
    else:
        print("\n¿Deseas crear un dataset de muestra para pruebas? (s/n): ", end="")
        response = input().strip().lower()
        
        if response in ['s', 'si', 'yes', 'y']:
            create_sample_dataset()
        
        print("\n" + "="*70)
        print("Configura el dataset antes de continuar")
        print("="*70 + "\n")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
