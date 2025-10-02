import sys
import os
import sqlite3
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_experiment_data(db_path, experiment_name):
    if not os.path.exists(db_path):
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM query_results", conn)
        conn.close()
        
        if df.empty:
            return None
        
        df['experiment'] = experiment_name
        return df
    except Exception as e:
        print(f"Error cargando {db_path}: {e}")
        return None

def calculate_metrics(df):
    total_unique = len(df)
    total_requests = df['request_count'].sum()
    cache_hits = total_requests - total_unique
    cache_hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0
    
    avg_score = df['quality_score'].mean()
    median_score = df['quality_score'].median()
    std_score = df['quality_score'].std()
    
    return {
        'experiment': df['experiment'].iloc[0],
        'total_unique_questions': total_unique,
        'total_requests': total_requests,
        'cache_hits': cache_hits,
        'cache_hit_rate': cache_hit_rate,
        'avg_quality_score': avg_score,
        'median_quality_score': median_score,
        'std_quality_score': std_score
    }

def generate_latex_table(metrics_df, output_file):
    with open(output_file, 'w') as f:
        f.write("\\begin{table}[H]\n")
        f.write("\\centering\n")
        f.write("\\caption{Comparación de Experimentos}\n")
        f.write("\\label{tab:comparison}\n")
        f.write("\\begin{tabular}{|l|r|r|r|r|}\n")
        f.write("\\hline\n")
        f.write("\\textbf{Experimento} & \\textbf{Hit Rate (\\%)} & \\textbf{Total Requests} & \\textbf{Avg Score} & \\textbf{Std Score} \\\\\n")
        f.write("\\hline\n")
        
        for _, row in metrics_df.iterrows():
            exp_name = row['experiment'].replace('_', '\\_')
            f.write(f"{exp_name} & {row['cache_hit_rate']:.2f} & {int(row['total_requests'])} & {row['avg_quality_score']:.4f} & {row['std_quality_score']:.4f} \\\\\n")
        
        f.write("\\hline\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")
    
    print(f"Tabla LaTeX generada: {output_file}")

def main():
    print("Generando tablas LaTeX desde resultados de experimentos...\n")
    
    data_dir = 'data'
    db_files = [f for f in os.listdir(data_dir) if f.startswith('results_exp') and f.endswith('.db')]
    
    if not db_files:
        print("No se encontraron bases de datos de experimentos.")
        return
    
    metrics_list = []
    
    for db_file in sorted(db_files):
        db_path = os.path.join(data_dir, db_file)
        exp_name = db_file.replace('results_', '').replace('.db', '')
        
        df = load_experiment_data(db_path, exp_name)
        if df is not None:
            metrics = calculate_metrics(df)
            metrics_list.append(metrics)
            print(f"✓ {exp_name}")
    
    if not metrics_list:
        print("No se pudieron cargar datos.")
        return
    
    metrics_df = pd.DataFrame(metrics_list)
    metrics_df = metrics_df.sort_values('cache_hit_rate', ascending=False)
    
    output_file = 'docs/comparison_table.tex'
    os.makedirs('docs', exist_ok=True)
    generate_latex_table(metrics_df, output_file)
    
    print(f"\nTabla guardada en: {output_file}")
    print("Copia el contenido en tu informe LaTeX.")

if __name__ == "__main__":
    main()
