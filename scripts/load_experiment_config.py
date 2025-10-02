import yaml
import os
import sys

def load_experiments_config(config_path='config/experiments.yaml'):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config

def validate_experiment_config(exp_config):
    required_fields = {
        'name': str,
        'description': str,
        'cache': dict,
        'traffic': dict,
        'llm': dict,
        'output': dict
    }
    
    for field, field_type in required_fields.items():
        if field not in exp_config:
            raise ValueError(f"Campo requerido faltante: {field}")
        if not isinstance(exp_config[field], field_type):
            raise ValueError(f"Campo {field} debe ser de tipo {field_type}")
    
    cache_fields = ['policy', 'max_size', 'ttl_seconds']
    for field in cache_fields:
        if field not in exp_config['cache']:
            raise ValueError(f"Campo de caché requerido faltante: {field}")
    
    traffic_fields = ['distribution', 'lambda', 'num_requests', 'max_delay_seconds']
    for field in traffic_fields:
        if field not in exp_config['traffic']:
            raise ValueError(f"Campo de tráfico requerido faltante: {field}")
    
    llm_fields = ['provider', 'model']
    for field in llm_fields:
        if field not in exp_config['llm']:
            raise ValueError(f"Campo de LLM requerido faltante: {field}")
    
    if 'db_path' not in exp_config['output']:
        raise ValueError("Campo de output requerido faltante: db_path")
    
    return True

def get_experiment_config(experiment_id, config_path='config/experiments.yaml'):
    config = load_experiments_config(config_path)
    
    if experiment_id not in config['experiments']:
        available = ', '.join(config['experiments'].keys())
        raise ValueError(f"Experimento '{experiment_id}' no encontrado. Disponibles: {available}")
    
    exp_config = config['experiments'][experiment_id]
    validate_experiment_config(exp_config)
    
    return exp_config

def list_experiments(config_path='config/experiments.yaml'):
    config = load_experiments_config(config_path)
    
    print("Experimentos disponibles:\n")
    for exp_id, exp_config in config['experiments'].items():
        print(f"  {exp_id}:")
        print(f"    Nombre: {exp_config['name']}")
        print(f"    Descripción: {exp_config['description']}")
        print(f"    Política de Caché: {exp_config['cache']['policy']}")
        print(f"    Distribución: {exp_config['traffic']['distribution']}")
        print(f"    Requests: {exp_config['traffic']['num_requests']}")
        print()

def create_env_from_experiment(experiment_id, config_path='config/experiments.yaml', output_path='.env.experiment'):
    exp_config = get_experiment_config(experiment_id, config_path)
    
    env_lines = [
        "# Configuración generada automáticamente desde experiments.yaml",
        f"# Experimento: {exp_config['name']}",
        "",
        "# Dataset",
        "DATA_PATH=data/test.csv",
        "",
        "# Cache Configuration",
        f"CACHE_HOST=localhost",
        f"CACHE_PORT=6379",
        f"CACHE_DB=0",
        f"CACHE_TTL_SECONDS={exp_config['cache']['ttl_seconds']}",
        f"CACHE_POLICY={exp_config['cache']['policy']}",
        f"CACHE_MAX_SIZE={exp_config['cache']['max_size']}",
        "",
        "# LLM Configuration",
        f"LLM_PROVIDER={exp_config['llm']['provider']}",
    ]
    
    provider = exp_config['llm']['provider'].upper()
    if provider == 'OLLAMA':
        env_lines.extend([
            "OLLAMA_HOST=http://localhost:11434",
            f"OLLAMA_MODEL_NAME={exp_config['llm']['model']}",
        ])
    elif provider == 'GEMINI':
        env_lines.extend([
            "GEMINI_API_KEY=your_api_key_here",
            f"GEMINI_MODEL_NAME={exp_config['llm']['model']}",
        ])
    elif provider == 'GROQ':
        env_lines.extend([
            "GROQ_API_KEY=your_api_key_here",
            f"GROQ_MODEL_NAME={exp_config['llm']['model']}",
        ])
    
    env_lines.extend([
        "",
        "# Database Configuration",
        "DB_TYPE=SQLITE",
        f"SQLITE_DB_PATH={exp_config['output']['db_path']}",
        "",
        "# Traffic Configuration",
        f"TRAFFIC_DISTRIBUTION_TYPE={exp_config['traffic']['distribution']}",
        f"TRAFFIC_LAMBDA={exp_config['traffic']['lambda']}",
        f"TRAFFIC_NUM_REQUESTS={exp_config['traffic']['num_requests']}",
        f"TRAFFIC_MAX_DELAY_SECONDS={exp_config['traffic']['max_delay_seconds']}",
    ])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(env_lines))
    
    print(f"Archivo de configuración creado: {output_path}")
    print(f"Para usar esta configuración, ejecuta:")
    print(f"  cp {output_path} .env")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'list':
            list_experiments()
        elif command == 'show' and len(sys.argv) > 2:
            exp_id = sys.argv[2]
            config = get_experiment_config(exp_id)
            print(yaml.dump({exp_id: config}, default_flow_style=False))
        elif command == 'create-env' and len(sys.argv) > 2:
            exp_id = sys.argv[2]
            output = sys.argv[3] if len(sys.argv) > 3 else '.env.experiment'
            create_env_from_experiment(exp_id, output_path=output)
        else:
            print("Uso:")
            print("  python load_experiment_config.py list")
            print("  python load_experiment_config.py show <experiment_id>")
            print("  python load_experiment_config.py create-env <experiment_id> [output_file]")
    else:
        list_experiments()
