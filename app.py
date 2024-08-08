import streamlit as st
import subprocess
import sys
import os
import time

# Configurar el tamaño de la página
st.set_page_config(
    page_title="MastersAccounting",
    page_icon=":bar_chart:",
    layout="wide",  # Cambiar a "wide" para más ancho
    initial_sidebar_state="expanded"
)

# Configurar la carpeta de subida
UPLOAD_FOLDER = os.path.abspath("")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Título de la aplicación
st.markdown("# MastersAccounting")

# Crear las pestañas
tabs = ["Inicio", "Procesar Archivos", "Comparar Archivos", "Descargar Archivos"]
selected_tab = st.selectbox("Seleccione una pestaña", tabs)

if selected_tab == "Inicio":
    # Página de inicio con bienvenida y descripción
    st.markdown("## Bienvenido a MastersAccounting")
    st.markdown("Selecciona una de las opciones disponibles para ejecutar:")
    st.markdown("1. **Procesar Archivos**: Verifica y procesa facturas para integrarlas en tu sistema contable.")
    st.markdown("2. **Comparar Archivos**: Compara diferentes reportes para verificar inconsistencias.")
    st.markdown("3. **Descargar Archivos**: Descarga reportes procesados.")
    
elif selected_tab == "Procesar Archivos":
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
            dian_path = os.path.join(UPLOAD_FOLDER, "archivos_usuarios", 'DIAN.xlsx')
            sinco_path = os.path.join(UPLOAD_FOLDER, "archivos_usuarios", 'SINCO.xlsx')
            cuentas_path = os.path.join(UPLOAD_FOLDER, "archivos_usuarios", 'MovDocCuenta_CSV.csv')

            with open(dian_path, 'wb') as f:
                f.write(dian_file.getbuffer())
            with open(sinco_path, 'wb') as f:
                f.write(sinco_file.getbuffer())
            with open(cuentas_path, 'wb') as f:
                f.write(cuentas_file.getbuffer())

            # Crear la barra de progreso
            progress_bar = st.progress(0)

            try:
                # Inicia el script en un subproceso
                process = subprocess.Popen([sys.executable, os.path.join(UPLOAD_FOLDER, "codes_proceso_completo", 'ejecutar_complet.py'), dian_path, sinco_path, cuentas_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Lee el progreso desde el archivo
                while True:
                    time.sleep(1)  # Espera un momento antes de verificar el archivo de progreso
                    if process.poll() is not None:
                        break  # Sal del bucle si el proceso ha terminado
                    try:
                        with open(os.path.join(UPLOAD_FOLDER, "codes_proceso_completo", 'progreso.txt'), 'r') as f:
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
                else:
                    st.error(f'Error al ejecutar el script: {stderr}')
                    st.text(stderr)
            except Exception as e:
                st.error(f'Error al ejecutar el script: {str(e)}')
        else:
            st.error('Todos los archivos deben ser seleccionados')

elif selected_tab == "Comparar Archivos":
    st.markdown("## Comparar Archivos")
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

    if st.button('Comparar Archivos'):
        if dian_file and sinco_file:
            dian_path = os.path.join(UPLOAD_FOLDER, "archivos_usuarios", 'DIAN.xlsx')
            sinco_path = os.path.join(UPLOAD_FOLDER, "archivos_usuarios", 'SINCO.xlsx')

            with open(dian_path, 'wb') as f:
                f.write(dian_file.getbuffer())
            with open(sinco_path, 'wb') as f:
                f.write(sinco_file.getbuffer())

            # Crear la barra de progreso
            progress_bar = st.progress(0)

            try:
                # Inicia el script en un subproceso
                process = subprocess.Popen([sys.executable, os.path.join(UPLOAD_FOLDER, "codes_proceso_completo", 'ejecutar_comparativ.py'), dian_path, sinco_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Lee el progreso desde el archivo
                while True:
                    time.sleep(1)  # Espera un momento antes de verificar el archivo de progreso
                    if process.poll() is not None:
                        break  # Sal del bucle si el proceso ha terminado
                    try:
                        with open(os.path.join(UPLOAD_FOLDER, "codes_proceso_completo", 'progreso.txt'), 'r') as f:
                            progress = f.read().strip()
                            if progress:
                                progress_bar.progress(int(float(progress)))
                    except FileNotFoundError:
                        pass

                # Verificar la salida del proceso
                stdout, stderr = process.communicate()
                if process.returncode == 0:
                    st.success('La comparación se ejecutó con éxito')
                    st.text(stdout)
                else:
                    st.error(f'Error al ejecutar la comparación: {stderr}')
                    st.text(stderr)
            except Exception as e:
                st.error(f'Error al ejecutar la comparación: {str(e)}')
        else:
            st.error('Ambos archivos deben ser seleccionados')

elif selected_tab == "Descargar Archivos":
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
            dian_path = os.path.join(UPLOAD_FOLDER, "archivos_usuarios", 'DIAN.xlsx')
            sinco_path = os.path.join(UPLOAD_FOLDER, "archivos_usuarios", 'SINCO.xlsx')

            with open(dian_path, 'wb') as f:
                f.write(dian_file.getbuffer())
            with open(sinco_path, 'wb') as f:
                f.write(sinco_file.getbuffer())

            # Crear la barra de progreso
            progress_bar = st.progress(0)

            try:
                # Inicia el script en un subproceso
                process = subprocess.Popen([sys.executable, os.path.join(UPLOAD_FOLDER, "codes_proceso_completo", 'ejecutar_downloand.py'), dian_path, sinco_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Lee el progreso desde el archivo
                while True:
                    time.sleep(1)  # Espera un momento antes de verificar el archivo de progreso
                    if process.poll() is not None:
                        break  # Sal del bucle si el proceso ha terminado
                    try:
                        with open(os.path.join(UPLOAD_FOLDER, "codes_proceso_completo", 'progreso.txt'), 'r') as f:
                            progress = f.read().strip()
                            if progress:
                                progress_bar.progress(int(float(progress)))
                    except FileNotFoundError:
                        pass

                # Verificar la salida del proceso
                stdout, stderr = process.communicate()
                if process.returncode == 0:
                    st.success('La descarga se ejecutó con éxito')
                    st.text(stdout)
                else:
                    st.error(f'Error al ejecutar la descarga: {stderr}')
                    st.text(stderr)
            except Exception as e:
                st.error(f'Error al ejecutar la descarga: {str(e)}')
        else:
            st.error('Ambos archivos deben ser seleccionados')

# Para ejecutar la aplicación, usa el siguiente comando en tu terminal:
# streamlit run app.py