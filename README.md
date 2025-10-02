# Directorio de Datos

Este directorio contiene el dataset de Yahoo! Answers y la base de datos de resultados.

## Dataset de Yahoo! Answers

### Descarga

Descarga el dataset desde Kaggle:
- **URL**: https://www.kaggle.com/datasets/jarupula/yahoo-answers-dataset
- **Archivos necesarios**: `test.csv` o `train.csv`

### Instalación

1. Ve a la página de Kaggle y descarga el dataset
2. Extrae el archivo ZIP
3. Copia `test.csv` a este directorio (`data/test.csv`)

\`\`\`bash
# Ejemplo de comandos
cd data/
# Coloca aquí tu archivo test.csv descargado
\`\`\`

### Formato del Dataset

El archivo CSV debe tener el siguiente formato (sin cabecera):

\`\`\`
class_index,title,content,best_answer
\`\`\`

**Columnas:**
- `class_index` (int): Categoría de la pregunta (1-10)
- `title` (str): Título de la pregunta
- `content` (str): Contenido detallado de la pregunta
- `best_answer` (str): Mejor respuesta seleccionada por la comunidad

**Ejemplo de fila:**
\`\`\`
4,"How to learn Python?","I want to start learning Python programming. What are the best resources?","Start with the official Python tutorial at python.org, then practice on sites like LeetCode."
\`\`\`

### Categorías

El dataset de Yahoo! Answers tiene 10 categorías principales:
1. Society & Culture
2. Science & Mathematics
3. Health
4. Education & Reference
5. Computers & Internet
6. Sports
7. Business & Finance
8. Entertainment & Music
9. Family & Relationships
10. Politics & Government

## Base de Datos de Resultados

El archivo `results.db` se genera automáticamente cuando ejecutas el sistema.

### Estructura de la Tabla

\`\`\`sql
CREATE TABLE query_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL UNIQUE,
    question_title TEXT,
    question_content TEXT,
    original_best_answer TEXT,
    llm_generated_answer TEXT,
    quality_score REAL,
    request_count INTEGER DEFAULT 1,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

### Consultar Resultados

Puedes consultar los resultados usando SQLite:

\`\`\`bash
# Abrir la base de datos
sqlite3 data/results.db

# Ver todas las consultas
SELECT * FROM query_results;

# Ver estadísticas
SELECT 
    COUNT(*) as total_queries,
    AVG(quality_score) as avg_score,
    MAX(request_count) as max_repetitions
FROM query_results;

# Ver las preguntas más consultadas
SELECT question_title, request_count, quality_score
FROM query_results
ORDER BY request_count DESC
LIMIT 10;

# Ver las respuestas con mejor score
SELECT question_title, quality_score, llm_generated_answer
FROM query_results
ORDER BY quality_score DESC
LIMIT 10;
\`\`\`

## Archivos en este Directorio

- `test.csv` - Dataset de Yahoo! Answers (debes descargarlo)
- `results.db` - Base de datos SQLite con resultados (se genera automáticamente)
- `README.md` - Este archivo

build: ## Construye las imágenes Docker
	docker-compose build

up: ## Inicia todos los servicios
	docker-compose up

up-d: ## Inicia todos los servicios en segundo plano
	docker-compose up -d

down: ## Detiene todos los servicios
	docker-compose down

down-v: ## Detiene todos los servicios y elimina volúmenes
	docker-compose down -v

logs: ## Muestra los logs de todos los servicios
	docker-compose logs -f

logs-app: ## Muestra solo los logs de la aplicación
	docker-compose logs -f app

logs-redis: ## Muestra solo los logs de Redis
	docker-compose logs -f redis

test: ## Ejecuta el script de verificación de configuración
	python scripts/test_setup.py

test-cache: ## Prueba el sistema de caché
	python -m src.cache_system

test-llm: ## Prueba el conector LLM
	python -m src.llm_connector

test-score: ## Prueba el calculador de scores
	python -m src.score_calculator

test-store: ## Prueba el almacenamiento
	python -m src.data_store

test-utils: ## Prueba las utilidades
	python -m src.utils

install: ## Instala las dependencias Python localmente
	pip install -r requirements.txt

clean: ## Limpia archivos temporales y caché
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete

clean-db: ## Elimina la base de datos de resultados
	rm -f data/results.db
	@echo "Base de datos eliminada. Se creará una nueva al ejecutar el sistema."

clean-all: clean down-v clean-db ## Limpia todo (archivos, contenedores, volúmenes, DB)

restart: down up ## Reinicia todos los servicios

shell-app: ## Abre una shell en el contenedor de la aplicación
	docker-compose exec app /bin/bash

shell-redis: ## Abre una shell de Redis
	docker-compose exec redis redis-cli

status: ## Muestra el estado de los servicios
	docker-compose ps

stats: ## Muestra estadísticas de uso de recursos
	docker stats

query-db: ## Abre SQLite para consultar la base de datos
	sqlite3 data/results.db

# Comandos de desarrollo
dev-setup: install ## Configura el entorno de desarrollo
	@echo "Verificando configuración..."
	@python scripts/test_setup.py

dev-run: ## Ejecuta la aplicación localmente (sin Docker)
	python src/main.py

# Comandos de análisis
analyze-results: ## Muestra estadísticas de los resultados
	@echo "Analizando resultados..."
	@sqlite3 data/results.db "SELECT COUNT(*) as total_queries, AVG(quality_score) as avg_score, MAX(request_count) as max_repetitions FROM query_results;"

top-questions: ## Muestra las preguntas más consultadas
	@echo "Top 10 preguntas más consultadas:"
	@sqlite3 data/results.db "SELECT question_title, request_count FROM query_results ORDER BY request_count DESC LIMIT 10;"

best-scores: ## Muestra las respuestas con mejor score
	@echo "Top 10 respuestas con mejor score:"
	@sqlite3 data/results.db "SELECT question_title, quality_score FROM query_results ORDER BY quality_score DESC LIMIT 10;"
