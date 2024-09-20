import streamlit as st
import os
from datetime import datetime
import subprocess
import sys

def run(subfolder):
    st.markdown("## Procesar Archivos")
    st.markdown("### Subida de Archivos")
    
    # Dividir en columnas para cargar los archivos
    col1, col2 = st.columns(2)

    with col1:
        # Permitir que el usuario suba varios archivos de factura (PDFs)
        uploaded_files = st.file_uploader("Cargar facturas (puede seleccionar múltiples archivos)", type="pdf", accept_multiple_files=True)
    
    with col2:
        # Permitir que el usuario suba el archivo CSV
        cuentas_file = st.file_uploader("Sube el archivo MovDocCuenta_CSV.csv", type="csv", key='cuentas')
        st.markdown("- **Nombre esperado:** MovDocCuenta_CSV.csv")
        st.markdown("- **Especificación:** Reporte *Mov por Doc y Cuenta* Histórico cuentas Costo y Gasto")
    
    # Cuando el usuario presione el botón de procesar
    if st.button('Procesar Facturas y CSV'):
        # Verificar que se hayan subido tanto los PDFs como el archivo CSV
        if uploaded_files and cuentas_file:
            # Obtener la fecha y hora actuales para crear una subcarpeta única
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")

            # Crear una subcarpeta en 'subfolder' con el nombre basado en la fecha y hora
            subfolder_path = os.path.join(subfolder, timestamp)
            os.makedirs(subfolder_path, exist_ok=True)

            # Guardar cada archivo PDF en la subcarpeta creada
            for uploaded_file in uploaded_files:
                file_path = os.path.join(subfolder_path, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            # Guardar el archivo CSV con el nombre fijo "MovDocCuenta_CSV.csv" en la subcarpeta
            csv_file_path = os.path.join(subfolder_path, "MovDocCuenta_CSV.csv")
            with open(csv_file_path, "wb") as f:
                f.write(cuentas_file.getbuffer())

            st.success(f'Se han guardado {len(uploaded_files)} archivos PDF y el archivo CSV en la carpeta {timestamp}')

            # Crear la barra de progreso
            st.markdown('<style>div[data-testid="stProgress"] { height: 24px; }</style>', unsafe_allow_html=True)
            progress_bar = st.progress(0)

            try:
                # Directorio donde están ubicados los scripts
                UPLOAD_FOLDER = os.path.abspath("codes_proceso_completo")
                # Ruta relativa del script ejecutar_downloand.py en la carpeta "codes_proceso_completo"
                fixed_script_path = os.path.join(UPLOAD_FOLDER, 'ejecutar_sin_descarga.py')

                # Iniciar el script en un subproceso desde la carpeta "codes_proceso_completo"
                process = subprocess.Popen(
                    [sys.executable, fixed_script_path, subfolder_path],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                # Número total de scripts para calcular el progreso
                total_scripts = 5
                completed_scripts = 0

                with st.spinner('Procesando...'):
                    # Leer la salida estándar del proceso en tiempo real
                    for line in iter(process.stdout.readline, ''):
                        line = line.strip()
                        if "Start:" in line:
                            pass
                        elif "End:" in line:
                            completed_scripts += 1
                            progress = completed_scripts / total_scripts
                            progress_bar.progress(progress)

                    process.wait()

                    # Verificar la salida del proceso al finalizar
                    stdout, stderr = process.communicate()
                    if process.returncode == 0:
                        st.success('Los archivos fueron procesados con éxito')
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
                        st.error(f'Error al procesar los archivos: {stderr}')
                        st.text(stderr)
            except Exception as e:
                st.error(f'Error al procesar los archivos: {str(e)}')
        else:
            st.error('Debe cargar al menos un archivo de factura y el archivo CSV')

# Llamar a la función run() en el archivo principal
if __name__ == "__main__":
    subfolder = os.path.abspath("archivos_usuarios")
    os.makedirs(subfolder, exist_ok=True)
    run(subfolder)
