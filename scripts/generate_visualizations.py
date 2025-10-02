import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

def load_experiment_results():
    results_file = "data/experiment_results.csv"
    if not os.path.exists(results_file):
        print(f"Error: No se encontró {results_file}")
        print("Ejecuta primero: python scripts/run_experiments.py")
        sys.exit(1)
    return pd.read_csv(results_file)

def plot_cache_policy_comparison(df):
    policy_data = df[df['experiment_name'].str.contains('Policy_')]
    
    if policy_data.empty:
        print("No hay datos de políticas de caché")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].bar(policy_data['cache_policy'], policy_data['hit_rate'] * 100)
    axes[0].set_xlabel('Política de Caché')
    axes[0].set_ylabel('Hit Rate (%)')
    axes[0].set_title('Comparación de Hit Rate por Política de Caché')
    axes[0].set_ylim(0, 100)
    
    axes[1].bar(policy_data['cache_policy'], policy_data['elapsed_time'])
    axes[1].set_xlabel('Política de Caché')
    axes[1].set_ylabel('Tiempo (segundos)')
    axes[1].set_title('Tiempo de Ejecución por Política')
    
    plt.tight_layout()
    plt.savefig('data/cache_policy_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico guardado: cache_policy_comparison.png")
    plt.close()

def plot_cache_size_comparison(df):
    size_data = df[df['experiment_name'].str.contains('Size_')]
    
    if size_data.empty:
        print("No hay datos de tamaños de caché")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].plot(size_data['cache_size'], size_data['hit_rate'] * 100, marker='o', linewidth=2)
    axes[0].set_xlabel('Tamaño de Caché')
    axes[0].set_ylabel('Hit Rate (%)')
    axes[0].set_title('Hit Rate vs Tamaño de Caché')
    axes[0].set_xscale('log')
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(size_data['cache_size'], size_data['cache_hits'], marker='o', label='Hits', linewidth=2)
    axes[1].plot(size_data['cache_size'], size_data['cache_misses'], marker='s', label='Misses', linewidth=2)
    axes[1].set_xlabel('Tamaño de Caché')
    axes[1].set_ylabel('Cantidad')
    axes[1].set_title('Cache Hits y Misses vs Tamaño')
    axes[1].set_xscale('log')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/cache_size_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico guardado: cache_size_comparison.png")
    plt.close()

def plot_distribution_comparison(df):
    dist_data = df[df['experiment_name'].str.contains('Dist_')]
    
    if dist_data.empty:
        print("No hay datos de distribuciones")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].bar(dist_data['distribution'], dist_data['hit_rate'] * 100)
    axes[0].set_xlabel('Distribución de Tráfico')
    axes[0].set_ylabel('Hit Rate (%)')
    axes[0].set_title('Hit Rate por Distribución de Tráfico')
    axes[0].set_ylim(0, 100)
    axes[0].tick_params(axis='x', rotation=45)
    
    x = range(len(dist_data))
    width = 0.35
    axes[1].bar([i - width/2 for i in x], dist_data['cache_hits'], width, label='Hits')
    axes[1].bar([i + width/2 for i in x], dist_data['cache_misses'], width, label='Misses')
    axes[1].set_xlabel('Distribución de Tráfico')
    axes[1].set_ylabel('Cantidad')
    axes[1].set_title('Cache Hits y Misses por Distribución')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(dist_data['distribution'], rotation=45)
    axes[1].legend()
    
    plt.tight_layout()
    plt.savefig('data/distribution_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico guardado: distribution_comparison.png")
    plt.close()

def plot_quality_scores():
    import sqlite3
    from config import settings
    
    if not os.path.exists(settings.SQLITE_DB_PATH):
        print("No hay datos de quality scores")
        return
    
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    df = pd.read_sql_query("SELECT quality_score FROM query_results", conn)
    conn.close()
    
    if df.empty:
        print("No hay datos de quality scores")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].hist(df['quality_score'], bins=50, edgecolor='black', alpha=0.7)
    axes[0].set_xlabel('Quality Score')
    axes[0].set_ylabel('Frecuencia')
    axes[0].set_title('Distribución de Quality Scores')
    axes[0].axvline(df['quality_score'].mean(), color='red', linestyle='--', label=f'Media: {df["quality_score"].mean():.3f}')
    axes[0].legend()
    
    axes[1].boxplot(df['quality_score'], vert=True)
    axes[1].set_ylabel('Quality Score')
    axes[1].set_title('Box Plot de Quality Scores')
    axes[1].set_xticklabels(['Scores'])
    
    plt.tight_layout()
    plt.savefig('data/quality_scores_distribution.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico guardado: quality_scores_distribution.png")
    plt.close()

def generate_summary_table(df):
    summary = df[['experiment_name', 'cache_policy', 'cache_size', 'distribution', 
                  'hit_rate', 'cache_hits', 'cache_misses', 'elapsed_time']].copy()
    summary['hit_rate'] = (summary['hit_rate'] * 100).round(2)
    summary['elapsed_time'] = summary['elapsed_time'].round(2)
    
    summary.to_csv('data/experiment_summary.csv', index=False)
    print("✓ Tabla resumen guardada: experiment_summary.csv")
    
    print("\n" + "="*70)
    print("RESUMEN DE EXPERIMENTOS")
    print("="*70)
    print(summary.to_string(index=False))
    print("="*70 + "\n")

def main():
    print("\n" + "="*70)
    print(" "*20 + "GENERACIÓN DE VISUALIZACIONES")
    print("="*70 + "\n")
    
    os.makedirs('data', exist_ok=True)
    
    try:
        df = load_experiment_results()
        print(f"Datos cargados: {len(df)} experimentos\n")
        
        print("Generando gráficos...")
        plot_cache_policy_comparison(df)
        plot_cache_size_comparison(df)
        plot_distribution_comparison(df)
        plot_quality_scores()
        
        generate_summary_table(df)
        
        print("\n" + "="*70)
        print("Visualizaciones generadas exitosamente")
        print("Archivos guardados en el directorio 'data/'")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
