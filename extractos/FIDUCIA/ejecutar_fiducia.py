import subprocess
import os
import sys

# Directorio donde están ubicados los scripts
SCRIPTS_DIR = os.path.abspath(os.path.join("extractos", "FIDUCIA"))

# Lista de scripts a ejecutar en orden
scripts = [
    'FIDUCIA.py',
    'FIDUCIA_2.py',
    'FIDUCIA_3.py',
    'FIDUCIA_4.py',
    'FIDUCIA_5.py'
]

# Ejecutar los scripts en orden
for script in scripts:
    script_path = os.path.join(SCRIPTS_DIR, script)
    
    if os.path.isfile(script_path):
        try:
            # Ejecutar cada script
            result = subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
            print(f"Ejecutado {script_path} con éxito")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar {script_path}")
            print(e.stderr)
            break  # Detener la ejecución si hay un error
    else:
        print(f"Archivo no encontrado: {script_path}")
        break

