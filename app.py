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

# Crear subcarpeta
subfolder = os.path.join(UPLOAD_FOLDER)
os.makedirs(subfolder, exist_ok=True)

# Ruta de la imagen del título
title_image_path = os.path.join("imagen", "titulo_app.png")

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

# Define la ruta a la carpeta "users" (misma jerarquía que archivos_usuarios)
USERS_FOLDER = os.path.abspath("users")
os.makedirs(USERS_FOLDER, exist_ok=True)

# Ruta completa al archivo de credenciales
CREDENTIALS_FILE = os.path.join(USERS_FOLDER, "users.txt")

# Función para cargar usuarios y contraseñas desde el archivo
def load_credentials(file_path):
    credentials = {}
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                # Verificar si la línea tiene el formato correcto
                if ":" in line:
                    user, passwd = line.strip().split(":")
                    credentials[user] = passwd
    else:
        st.error("No se encontró el archivo de credenciales.")
    
    return credentials

# Cargar las credenciales desde el archivo users.txt
credentials = load_credentials(CREDENTIALS_FILE)

# **Login logic**
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Mostrar el formulario de inicio de sesión si no está logueado
if not st.session_state["logged_in"]:
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        # Verificar si el usuario existe y la contraseña es correcta
        if username in credentials:
            if credentials[username] == password:
                st.session_state["logged_in"] = True
                st.success("Logged in successfully!")
            else:
                st.sidebar.error("Invalid password")
        else:
            st.sidebar.error("Invalid username")

# Si está logueado, mostrar las opciones
if st.session_state["logged_in"]:
    # Barra lateral con opciones de navegación
    st.sidebar.header("¿Qué Análisis Requieres?")
    tabs = {
        "Inicio": "inicio",
        "Contabilización Masiva": "procesar_archivos",
        "Verificación de Facturas": "comparar_archivos",
        "Descargas Automáticas": "descargar_archivos",
        "Rellenar formato Sinco": "proceso_sin_descargar"
    }
    
    selected_tab = st.sidebar.selectbox("Seleccione", list(tabs.keys()))
    
    # Mostrar información de los autores en la barra lateral
    st.sidebar.markdown("""
        <div style="margin-top: 20px;">
            <h4>By</h4>
            <ul>
                <li>American Lighting Group</li>
                <li>JC-ML-MG-YP-DV</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # Botón para cerrar sesión (estilo rojizo y posicionado al final)
    st.sidebar.markdown("""
        <style>
        .logout-button {
            background-color: #FF4B4B;
            color: white;
            padding: 10px;
            width: 100%;
            border: none;
            border-radius: 5px;
            margin-top: 20px;
        }
        .logout-button:hover {
            background-color: #ff1a1a;
        }
        </style>
        """, unsafe_allow_html=True)

    if st.sidebar.button("Cerrar Sesión", key="logout", help="Cerrar la sesión actual", on_click=lambda: st.session_state.update({"logged_in": False})):
        st.sidebar.success("Sesión cerrada correctamente.")
    
    # Importar y ejecutar el código correspondiente a la pestaña seleccionada
    module = __import__(f"tabs.{tabs[selected_tab]}", fromlist=[None])
    module.run(subfolder)
else:
    # Si no está logueado, mostrar solo la pestaña de Inicio
    st.sidebar.header("Bienvenido")
    st.write("Por favor, inicie sesión para acceder al resto de las funcionalidades.")


# Para ejecutar la aplicación usa: streamlit run app.py



