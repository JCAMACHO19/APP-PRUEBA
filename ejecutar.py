import subprocess
import sys
import os

# Lista de scripts a ejecutar en orden
scripts = [
    'dian_contable_coparativo.py',
    'fe_anulada.py',
    'downloand.py', 
    'info_dian.py', 
    'cuenta_proveedor.py', 
    'importar_doc.py', 
    'info_complem.py',
    'archivo_comprimido.py'
]

for script in scripts:
    if not os.path.isfile(script):
        print(f"Archivo no encontrado: {script}")
        break
    
    try:
        # Ejecutar cada script
        result = subprocess.run([sys.executable, script], check=True, capture_output=True, text=True)
        print(f"Ejecutado {script} con éxito")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {script}")
        print(e.stderr)
        break  # Detener la ejecución si hay un error

