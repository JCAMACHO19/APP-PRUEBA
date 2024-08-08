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
        # Ejecutar cada script
        result = subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
        print(f"Ejecutado {script_path} con éxito")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {script_path}")
        print(e.stderr)
        break  # Detener la ejecución si hay un error
