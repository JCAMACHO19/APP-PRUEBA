import subprocess
import sys
import os

# Directorio donde están ubicados los scripts
UPLOAD_FOLDER = os.path.abspath(os.path.join("", "codes_proceso_completo"))

# Lista de scripts a ejecutar en orden
scripts = [
    'dian_contable_coparativo.py',
    'downloand.py',
    'archivo_comprimido.py'
]

for script in scripts:
    script_path = os.path.join(UPLOAD_FOLDER, script)
    
    if not os.path.isfile(script_path):
        print(f"Archivo no encontrado: {script_path}")
        break
    
    try:
        # Imprime el inicio de la ejecución
        print(f"Start: {script}", flush=True)
        # Ejecutar cada script
        result = subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
        # Imprime el final de la ejecución
        print(f"End: {script}", flush=True)
        print(f"Ejecutado {script_path} con éxito")
        print(result.stdout, flush=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {script_path}")
        print(e.stderr, flush=True)
        break  # Detener la ejecución si hay un error
