import streamlit as st
import os
import subprocess
import sys
import time
from datetime import datetime

def run(subfolder):
    st.markdown("## Descargar Archivos")
    st.markdown("### Subida de Archivos")
    col1, col2 = st.columns(2)

    with col1:
        dian_file = st.file_uploader("Sube el archivo DIAN.xlsx", type="xlsx", key='dian')
        st.markdown("- **Nombre esperado:** DIAN.xlsx")
        st.markdown("- **Especificación:** Reporte Dian de Documentos Recibidos")

    with col2:
        sinco_file = st.file_uploader("Sube el archivo SINCO.xlsx", type="xlsx", key='sinco')
        st.markdown("- **Nombre esperado:** SINCO.xlsx")
        st.markdown("- **Especificación:** Reporte *Mov por Doc y Cuenta* Seleccionando Concepto y Doc del tercero")

    if st.button('Descargar Archivos'):
        if dian_file and sinco_file:
            # Obtener la fecha y hora actuales para crear una subcarpeta única
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")

            # Crear una subcarpeta en 'subfolder' con el nombre basado en la fecha y hora
            subfolder_path = os.path.join(subfolder, timestamp)
            os.makedirs(subfolder_path, exist_ok=True)

            # Guardar los archivos subidos en la subcarpeta creada
            dian_path = os.path.join(subfolder_path, 'DIAN.xlsx')
            sinco_path = os.path.join(subfolder_path, 'SINCO.xlsx')

            with open(dian_path, 'wb') as f:
                f.write(dian_file.getbuffer())
            with open(sinco_path, 'wb') as f:
                f.write(sinco_file.getbuffer())

            # Crear la barra de progreso
            progress_bar = st.progress(0)

            try:
                # Directorio donde están ubicados los scripts
                UPLOAD_FOLDER = os.path.abspath(os.path.join("", "codes_proceso_completo"))
                # Ruta relativa del script ejecutar_descarg.py en la carpeta "codes_proceso_completo"
                fixed_script_path = os.path.join(UPLOAD_FOLDER, 'ejecutar_downloand.py')

                # Inicia el script en un subproceso desde la carpeta "codes_proceso_completo"
                process = subprocess.Popen([sys.executable, fixed_script_path, dian_path, sinco_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Lee el progreso desde el archivo
                while True:
                    time.sleep(1)  # Espera un momento antes de verificar el archivo de progreso
                    if process.poll() is not None:
                        break  # Sal del bucle si el proceso ha terminado
                    try:
                        with open(os.path.join(subfolder_path, 'progreso.txt'), 'r') as f:
                            progress = f.read().strip()
                            if progress:
                                progress_bar.progress(int(float(progress)))
                    except FileNotFoundError:
                        pass

                # Verificar la salida del proceso
                stdout, stderr = process.communicate()
                if process.returncode == 0:
                    st.success('Los archivos se descargaron con éxito')
                    st.text(stdout)
                else:
                    st.error(f'Error al descargar los archivos: {stderr}')
                    st.text(stderr)
            except Exception as e:
                st.error(f'Error al descargar los archivos: {str(e)}')
        else:
            st.error('Ambos archivos deben ser seleccionados')

