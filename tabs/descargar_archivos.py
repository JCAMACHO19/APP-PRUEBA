import streamlit as st
import os
import subprocess
import sys
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
            st.markdown('<style>div[data-testid="stProgress"] { height: 24px; }</style>', unsafe_allow_html=True)
            progress_bar = st.progress(0)

            try:
                # Directorio donde están ubicados los scripts
                UPLOAD_FOLDER = os.path.abspath("codes_proceso_completo")
                # Ruta relativa del script ejecutar_downloand.py en la carpeta "codes_proceso_completo"
                fixed_script_path = os.path.join(UPLOAD_FOLDER, 'ejecutar_downloand.py')

                # Inicia el script en un subproceso desde la carpeta "codes_proceso_completo"
                process = subprocess.Popen(
                    [sys.executable, fixed_script_path, dian_path, sinco_path],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                # Número total de scripts para calcular el progreso
                total_scripts = 3
                completed_scripts = 0

                with st.spinner('LOADING...'):
                    # Lee la salida estándar del proceso en tiempo real
                    for line in iter(process.stdout.readline, ''):
                        line = line.strip()
                        if "Start:" in line:
                            # No hacer nada en el inicio, solo leer la línea
                            pass
                        elif "End:" in line:
                            completed_scripts += 1
                            progress = completed_scripts / total_scripts
                            progress_bar.progress(progress)

                    # Espera a que el proceso termine
                    process.wait()

                    # Verificar la salida del proceso al finalizar
                    stdout, stderr = process.communicate()
                    if process.returncode == 0:
                        st.success('Los archivos se descargaron con éxito')
                        st.text(stdout)

                        # Buscar el archivo .zip generado en la carpeta
                        zip_filename = f"{timestamp}.zip"
                        zip_filepath = os.path.join(subfolder, zip_filename)

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
                        st.error(f'Error al descargar los archivos: {stderr}')
                        st.text(stderr)
            except Exception as e:
                st.error(f'Error al descargar los archivos: {str(e)}')
        else:
            st.error('Ambos archivos deben ser seleccionados')

