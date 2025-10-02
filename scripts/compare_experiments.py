import sys
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def load_experiment_data(db_path, experiment_name):
    if not os.path.exists(db_path):
        print(f"Advertencia: No se encontró {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM query_results", conn)
        conn.close()
        
        if df.empty:
            print(f"Advertencia: {db_path} está vacío")
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
        'total_unique_questions': total_unique,
        'total_requests': total_requests,
        'cache_hits': cache_hits,
        'cache_hit_rate': cache_hit_rate,
        'avg_quality_score': avg_score,
        'median_quality_score': median_score,
        'std_quality_score': std_score
    }

def plot_cache_performance(metrics_df, output_dir):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    ax1.bar(range(len(metrics_df)), metrics_df['cache_hit_rate'], color='steelblue')
    ax1.set_xlabel('Experimento')
    ax1.set_ylabel('Cache Hit Rate (%)')
    ax1.set_title('Tasa de Aciertos de Caché por Experimento')
    ax1.set_xticks(range(len(metrics_df)))
    ax1.set_xticklabels(metrics_df['experiment'], rotation=45, ha='right')
    ax1.grid(axis='y', alpha=0.3)
    
    for i, v in enumerate(metrics_df['cache_hit_rate']):
        ax1.text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom')
    
    x = np.arange(len(metrics_df))
    width = 0.35
    
    ax2.bar(x - width/2, metrics_df['total_requests'], width, label='Total Requests', color='lightcoral')
    ax2.bar(x + width/2, metrics_df['cache_hits'], width, label='Cache Hits', color='lightgreen')
    
    ax2.set_xlabel('Experimento')
    ax2.set_ylabel('Número de Requests')
    ax2.set_title('Total de Requests vs Cache Hits')
    ax2.set_xticks(x)
    ax2.set_xticklabels(metrics_df['experiment'], rotation=45, ha='right')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'cache_performance.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Gráfico guardado: {output_file}")
    plt.close()

def plot_quality_scores(all_data, output_dir):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    experiments = all_data['experiment'].unique()
    data_to_plot = [all_data[all_data['experiment'] == exp]['quality_score'].values 
                    for exp in experiments]
    
    bp = ax1.boxplot(data_to_plot, labels=experiments, patch_artist=True)
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
    
    ax1.set_xlabel('Experimento')
    ax1.set_ylabel('Quality Score')
    ax1.set_title('Distribución de Quality Scores por Experimento')
    ax1.tick_params(axis='x', rotation=45)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax1.grid(axis='y', alpha=0.3)
    
    for exp in experiments:
        exp_data = all_data[all_data['experiment'] == exp]['quality_score']
        ax2.hist(exp_data, alpha=0.5, label=exp, bins=20)
    
    ax2.set_xlabel('Quality Score')
    ax2.set_ylabel('Frecuencia')
    ax2.set_title('Distribución de Quality Scores')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'quality_scores.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Gráfico guardado: {output_file}")
    plt.close()

def plot_score_comparison(metrics_df, output_dir):
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(metrics_df))
    
    ax.bar(x, metrics_df['avg_quality_score'], color='skyblue', label='Promedio')
    ax.errorbar(x, metrics_df['avg_quality_score'], 
                yerr=metrics_df['std_quality_score'],
                fmt='none', color='black', capsize=5, label='Desviación estándar')
    
    ax.set_xlabel('Experimento')
    ax.set_ylabel('Quality Score')
    ax.set_title('Quality Score Promedio por Experimento')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_df['experiment'], rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Añadir valores sobre las barras
    for i, v in enumerate(metrics_df['avg_quality_score']):
        ax.text(i, v + 0.01, f'{v:.4f}', ha='center', va='bottom')
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'score_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Gráfico guardado: {output_file}")
    plt.close()

def generate_comparison_table(metrics_df, output_dir):
    metrics_df_sorted = metrics_df.sort_values('cache_hit_rate', ascending=False)
    
    csv_file = os.path.join(output_dir, 'comparison_table.csv')
    metrics_df_sorted.to_csv(csv_file, index=False)
    print(f"Tabla CSV guardada: {csv_file}")
    
    latex_file = os.path.join(output_dir, 'comparison_table.tex')
    with open(latex_file, 'w') as f:
        f.write("\\begin{table}[h]\n")
        f.write("\\centering\n")
        f.write("\\caption{Comparación de Experimentos}\n")
        f.write("\\label{tab:comparison}\n")
        f.write("\\begin{tabular}{|l|r|r|r|r|}\n")
        f.write("\\hline\n")
        f.write("\\textbf{Experimento} & \\textbf{Hit Rate (\\%)} & \\textbf{Total Requests} & \\textbf{Avg Score} & \\textbf{Std Score} \\\\\n")
        f.write("\\hline\n")
        
        for _, row in metrics_df_sorted.iterrows():
            exp_name = row['experiment'].replace('_', '\\_')
            f.write(f"{exp_name} & {row['cache_hit_rate']:.2f} & {int(row['total_requests'])} & {row['avg_quality_score']:.4f} & {row['std_quality_score']:.4f} \\\\\n")
        
        f.write("\\hline\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")
    
    print(f"Tabla LaTeX guardada: {latex_file}")

def main():
    print("\n" + "="*80)
    print(" "*25 + "COMPARADOR DE EXPERIMENTOS")
    print(" "*20 + "Sistema de Análisis Yahoo! Answers")
    print("="*80 + "\n")
    
    data_dir = 'data'
    db_files = [f for f in os.listdir(data_dir) if f.startswith('results_exp') and f.endswith('.db')]
    
    if not db_files:
        print("No se encontraron bases de datos de experimentos en el directorio 'data/'")
        print("Ejecuta primero 'python scripts/run_experiments.py'")
        return
    
    print(f"Se encontraron {len(db_files)} experimentos:\n")
    for db_file in sorted(db_files):
        print(f"  - {db_file}")
    
    all_data = []
    metrics_list = []
    
    print("\nCargando datos de experimentos...")
    for db_file in sorted(db_files):
        db_path = os.path.join(data_dir, db_file)
        exp_name = db_file.replace('results_', '').replace('.db', '')
        
        df = load_experiment_data(db_path, exp_name)
        if df is not None:
            all_data.append(df)
            metrics = calculate_metrics(df)
            metrics['experiment'] = exp_name
            metrics_list.append(metrics)
            print(f"  ✓ {exp_name}: {len(df)} registros")
    
    if not all_data:
        print("\nNo se pudieron cargar datos de ningún experimento.")
        return
    
    combined_data = pd.concat(all_data, ignore_index=True)
    metrics_df = pd.DataFrame(metrics_list)
    
    output_dir = f"data/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nGenerando análisis en: {output_dir}")
    
    print("\nGenerando visualizaciones...")
    plot_cache_performance(metrics_df, output_dir)
    plot_quality_scores(combined_data, output_dir)
    plot_score_comparison(metrics_df, output_dir)
    generate_comparison_table(metrics_df, output_dir)
    
    print("\n" + "="*80)
    print("RESUMEN DE MÉTRICAS")
    print("="*80 + "\n")
    print(metrics_df.to_string(index=False))
    
    print("\n" + "="*80)
    print("Análisis completado!")
    print(f"Resultados guardados en: {output_dir}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
