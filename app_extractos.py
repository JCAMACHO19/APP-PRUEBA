import streamlit as st
import os
from datetime import datetime
import subprocess


# Configuración básica de la página
st.set_page_config(page_title="Cargar Extracto Bancario", layout="wide")

# Título de la aplicación
st.title("Cargar Extracto Bancario")

# Instrucciones
st.write("Sube un archivo PDF y selecciona el banco correspondiente. El archivo será guardado en la carpeta del banco seleccionado con una marca de tiempo y se ejecutará el script correspondiente.")

# Cargar archivo PDF
uploaded_file = st.file_uploader("Selecciona un archivo PDF", type="pdf")

# Selección de banco
bank = st.selectbox("Selecciona el banco del extracto", ["Fiducia", "Colpatria", "Bancoomeva Tradicional", "Bancoomeva Inteligente"])

# Configuración de la carpeta de destino y script a ejecutar según el banco seleccionado
if bank == "Fiducia":
    UPLOAD_FOLDER = os.path.abspath(os.path.join("extractos", "FIDUCIA"))
    file_name = "FIDUCIA.pdf"
    script_path = os.path.abspath(os.path.join("extractos", "FIDUCIA", "ejecutar_fiducia.py"))
elif bank == "Colpatria":
    UPLOAD_FOLDER = os.path.abspath(os.path.join("extractos", "COLPATRIA"))
    file_name = "COLPATRIA.pdf"
    script_path = os.path.abspath(os.path.join("extractos", "COLPATRIA", "ejecutar_colpatria.py"))
elif bank == "Bancoomeva Tradicional":
    UPLOAD_FOLDER = os.path.abspath(os.path.join("extractos", "BANCOOMEVA TRADICIONAL"))
    file_name = "BANCOOMEVA_TRADICIONAL.pdf"
    script_path = os.path.abspath(os.path.join("extractos", "BANCOOMEVA TRADICIONAL", "ejecutar_bancoomeva_tradicional.py"))
elif bank == "Bancoomeva Inteligente":
    UPLOAD_FOLDER = os.path.abspath(os.path.join("extractos", "BANCOOMEVA INTELIGENTE"))
    file_name = "BANCOOMEVA_INTELIGENTE.pdf"
    script_path = os.path.abspath(os.path.join("extractos", "BANCOOMEVA INTELIGENTE", "ejecutar_bancoomeva_inteligente.py"))

# Botón para guardar el archivo y ejecutar el script
if st.button("Guardar archivo PDF y ejecutar script"):
    if uploaded_file is not None:
        # Crear la carpeta con la marca de tiempo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_folder = os.path.join(UPLOAD_FOLDER, timestamp)
        os.makedirs(timestamped_folder, exist_ok=True)
        
        # Ruta completa del archivo
        file_path = os.path.join(timestamped_folder, file_name)
        
        # Guardar el archivo
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"Archivo guardado como {file_name} en {timestamped_folder}")
        
        # Ejecutar el script correspondiente
        try:
            subprocess.run(["python", script_path], check=True)
            st.success(f"Script {os.path.basename(script_path)} ejecutado correctamente.")
        except subprocess.CalledProcessError as e:
            st.error(f"Error al ejecutar el script {os.path.basename(script_path)}: {e}")
    else:
        st.error("Por favor, sube un archivo PDF.")

# Pie de página
st.markdown("<hr>", unsafe_allow_html=True)
st.write("Desarrollado por [Tu Nombre]")


# streamlit run app_extractos.py
