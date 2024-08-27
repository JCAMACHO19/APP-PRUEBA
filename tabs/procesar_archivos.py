import streamlit as st
import os
import subprocess
import sys
import time
from datetime import datetime
import socket

def run(subfolder):
    st.markdown("## Procesar Archivos")
    st.markdown("### Subida de Archivos")
    col1, col2, col3 = st.columns(3)

    with col1:
        dian_file = st.file_uploader("Sube el archivo DIAN.xlsx", type="xlsx", key='dian')
        st.markdown("- **Nombre esperado:** DIAN.xlsx")
        st.markdown("- **Especificación:** Reporte Dian de Documentos Recibidos")

    with col2:
        sinco_file = st.file_uploader("Sube el archivo SINCO.xlsx", type="xlsx", key='sinco')
        st.markdown("- **Nombre esperado:** SINCO.xlsx")
        st.markdown("- **Especificación:** Reporte *Mov por Doc y Cuenta* Seleccionando Concepto y Doc del tercero")

    with col3:
        cuentas_file = st.file_uploader("Sube el archivo MovDocCuenta_CSV.csv", type="csv", key='cuentas')
        st.markdown("- **Nombre esperado:** MovDocCuenta_CSV.csv")
        st.markdown("- **Especificación:** Reporte *Mov por Doc y Cuenta* Histórico cuentas Costo y Gasto")

    if st.button('Procesar Archivos'):
        if dian_file and sinco_file and cuentas_file:
            # Obtener la fecha y hora actuales para crear una subcarpeta única
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")

            # Crear una subcarpeta en 'archivos_usuarios' con el nombre basado en la fecha y hora
            subfolder = os.path.join("archivos_usuarios", timestamp)
            os.makedirs(subfolder, exist_ok=True)

            # Guardar los archivos subidos en la subcarpeta creada
            dian_path = os.path.join(subfolder, 'DIAN.xlsx')
            sinco_path = os.path.join(subfolder, 'SINCO.xlsx')
            cuentas_path = os.path.join(subfolder, 'MovDocCuenta_CSV.csv')

            with open(dian_path, 'wb') as f:
                f.write(dian_file.getbuffer())
            with open(sinco_path, 'wb') as f:
                f.write(sinco_file.getbuffer())
            with open(cuentas_path, 'wb') as f:
                f.write(cuentas_file.getbuffer())

            # Crear la barra de progreso
            progress_bar = st.progress(0)

            try:
                # Directorio donde están ubicados los scripts
                UPLOAD_FOLDER = os.path.abspath("archivos_usuarios")
                # Ruta relativa del script ejecutar_complet.py en la carpeta "codes_proceso_completo"
                fixed_script_path = os.path.abspath("codes_proceso_completo/ejecutar_complet.py")

                # Inicia el script en un subproceso desde la carpeta fija
                process = subprocess.Popen(
                    [sys.executable, fixed_script_path, dian_path, sinco_path, cuentas_path],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                # Lee el progreso desde el archivo
                while True:
                    time.sleep(1)  # Espera un momento antes de verificar el archivo de progreso
                    if process.poll() is not None:
                        break  # Sal del bucle si el proceso ha terminado
                    try:
                        with open(os.path.join(subfolder, 'progreso.txt'), 'r') as f:
                            progress = f.read().strip()
                            if progress:
                                progress_bar.progress(int(float(progress)))
                    except FileNotFoundError:
                        pass

                # Verificar la salida del proceso
                stdout, stderr = process.communicate()
                if process.returncode == 0:
                    st.success('El script se ejecutó con éxito')
                    st.text(stdout)

                    # Buscar el archivo .zip generado en la carpeta 'archivos_usuarios'
                    zip_filename = f"{timestamp}.zip"
                    zip_filepath = os.path.join("archivos_usuarios", zip_filename)

                    if os.path.exists(zip_filepath):
                        with open(zip_filepath, "rb") as f:
                            st.download_button(
                                label="Descargar archivo ZIP",
                                data=f,
                                file_name=zip_filename,
                                mime='application/zip'
                            )
                    else:
                        st.error(f'No se encontró el archivo {zip_filename}')
                else:
                    st.error(f'Error al ejecutar el script: {stderr}')
                    st.text(stderr)
            except Exception as e:
                st.error(f'Error al ejecutar el script: {str(e)}')
        else:
            st.error('Todos los archivos deben ser seleccionados')


