import subprocess
import sys
import os

# Directorio donde están ubicados los scripts
UPLOAD_FOLDER = os.path.abspath(os.path.join("", "codes_proceso_completo"))

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

# Ruta al archivo de progreso
progress_file_path = os.path.join(UPLOAD_FOLDER, 'progreso.txt')

# Función para actualizar el archivo de progreso
def update_progress(progress):
    with open(progress_file_path, 'w') as f:
        f.write(str(progress))

total_scripts = len(scripts)
for index, script in enumerate(scripts):
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
        
        # Actualiza el progreso
        progress_percentage = ((index + 1) / total_scripts) * 100
        update_progress(progress_percentage)

    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {script_path}")
        print(e.stderr, flush=True)
        break  # Detener la ejecución si hay un error

# Si todo termina con éxito, asegurar que el progreso llegue al 100%
update_progress(100)



