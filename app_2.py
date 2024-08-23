import streamlit as st
from datetime import datetime
import os

# Configurar el tamaño de la página
st.set_page_config(
    page_title="MastersAccounting",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar la carpeta de subida principal
UPLOAD_FOLDER = os.path.abspath("archivos_usuarios")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Crear subcarpeta con la hora actual
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
subfolder = os.path.join(UPLOAD_FOLDER, timestamp)
os.makedirs(subfolder, exist_ok=True)

# Título de la aplicación
st.markdown("# MastersAccounting")

# Crear las pestañas
tabs = {
    "Inicio": "inicio",
    "Procesar Archivos": "procesar_archivos",
    "Comparar Archivos": "comparar_archivos",
    "Descargar Archivos": "descargar_archivos"
}
selected_tab = st.selectbox("Seleccione una pestaña", list(tabs.keys()))

# Importar y ejecutar el código correspondiente a la pestaña seleccionada
module = __import__(f"tabs.{tabs[selected_tab]}", fromlist=[None])
module.run(subfolder)
# streamlit run app_2.py