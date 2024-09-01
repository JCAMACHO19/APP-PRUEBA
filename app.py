import streamlit as st
import os

# Configurar el tamaño de la página y el diseño
st.set_page_config(
    page_title="Accounting Optimization",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar la carpeta de subida principal
UPLOAD_FOLDER = os.path.abspath("archivos_usuarios")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Crear subcarpeta con la hora actual
subfolder = os.path.join(UPLOAD_FOLDER)
os.makedirs(subfolder, exist_ok=True)

# Ruta de la imagen del título
title_image_path = os.path.join("imagen", "titulo_app.jpg")

# Verificar si la imagen existe y cargarla con st.image
if os.path.exists(title_image_path):
    st.image(title_image_path, use_column_width=True)
else:
    st.error("La imagen del título no se encontró en la ruta especificada.")

# Ruta de la imagen del logo
logo_image_path = os.path.join("imagen", "logo_american.png")

# Verificar si la imagen existe y cargarla en la barra lateral
if os.path.exists(logo_image_path):
    st.sidebar.image(logo_image_path, use_column_width=True)
else:
    st.sidebar.error("El logo no se encontró en la ruta especificada.")

# Barra lateral con opciones de navegación
st.sidebar.header("¿Qué Análisis Requieres?")
tabs = {
    "Inicio": "inicio",
    "Contabilización Masiva": "procesar_archivos",
    "Verificación de Facturas": "comparar_archivos",
    "Descargas Automáticas": "descargar_archivos"
}
selected_tab = st.sidebar.selectbox("Seleccione", list(tabs.keys()))

# Mostrar información de los autores en la barra lateral
st.sidebar.markdown("""
    <div style="margin-top: 20px;">
        <h4>By</h4>
        <ul>
            <li>American Lighting Group</li>
            <li>Jorge Camacho M.</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

# Importar y ejecutar el código correspondiente a la pestaña seleccionada
module = __import__(f"tabs.{tabs[selected_tab]}", fromlist=[None])
module.run(subfolder)

# Para ejecutar la aplicación usa: streamlit run app.py



