set -e

EXPERIMENT_ID=$1

if [ -z "$EXPERIMENT_ID" ]; then
    echo "Uso: ./quick_experiment.sh <experiment_id>"
    echo ""
    echo "Experimentos disponibles:"
    python scripts/load_experiment_config.py list
    exit 1
fi

echo "Preparando experimento: $EXPERIMENT_ID"

python scripts/load_experiment_config.py create-env "$EXPERIMENT_ID" .env

echo "Limpiando caché de Redis..."
redis-cli FLUSHALL

echo "Ejecutando experimento..."
python -m src.traffic_generator

echo ""
echo "Experimento completado!"
echo "Resultados guardados en: data/results_${EXPERIMENT_ID}.db"
echo ""
echo "Para analizar resultados:"
echo "  python scripts/analyze_results.py"
