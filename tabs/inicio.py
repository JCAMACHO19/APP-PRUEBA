import streamlit as st
import os

# Función para ejecutar la pestaña de inicio
def run(subfolder):
    # Usar HTML y CSS para replicar el estilo de título con Roboto Condensed
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700&display=swap');
        .title-container {
            text-align: center; 
            font-family: 'Roboto Condensed', sans-serif;
        }
        .subtitle {
            font-size: 100px; 
            font-weight: 900; 
            color: #D7D6D2;
        }
        .title-part1, .title-part2 {
            font-size: 120px; 
            font-weight: 900; 
            color: #271080;
        }
        .title-part3 {
            font-size: 120px; 
            font-weight: 900; 
            color: #545454;
        }
        /* Estilo para las cajas */
        .box-title {
            font-size: 24px;
            font-weight: bold;
            color: #271080;
            margin-bottom: 10px;
            cursor: pointer;
            text-decoration: underline;
        }
        .box-text {
            font-size: 18px;
            margin-top: 10px;
        }
    </style>
    <div class="title-container">
        <span class="subtitle">BIENVENIDO A </span>
        <span class="title-part1">BI</span>
        <span class="title-part2">LL</span>
        <span class="title-part3">IT</span>
    </div>
    """, unsafe_allow_html=True)

    # Crear la ruta del directorio de las imágenes
    UPLOAD_FOLDER = "imagen"  # Carpeta donde están las imágenes
    subfolder = os.path.join(UPLOAD_FOLDER)
    os.makedirs(subfolder, exist_ok=True)

    # Rutas de las imágenes de las cajas 2 y 4
    image_paths = {
        "caja1": os.path.join(subfolder, "caja1.gif"),
        "caja2": os.path.join(subfolder, "caja4.gif"),
    }

    # Verificar que ambas imágenes existen
    for caja, path in image_paths.items():
        if not os.path.exists(path):
            st.error(f"No se encontró la imagen para {caja} en la ruta: {path}")
            return

    # Caja 1: Verificación de Facturas (Imagen a la izquierda)
    col1, col2 = st.columns([1, 3])  # Ajuste de tamaño para la imagen y la descripción
    with col1:
        st.image(image_paths["caja1"], use_column_width=True)
    with col2:
        st.markdown(f'<div class="box-title"><a href="#comparar_archivos" target="_self">Verificación de Facturas</a></div>', unsafe_allow_html=True)
        st.markdown('<p class="box-text">Compara diferentes reportes para verificar inconsistencias en facturas.</p>', unsafe_allow_html=True)

    st.markdown("---")  # Línea de separación entre las cajas

    # Caja 2: Rellenar formato SINCO (Imagen a la derecha)
    col3, col4 = st.columns([3, 1])  # Intercambio de posición
    with col4:
        st.image(image_paths["caja2"], use_column_width=True)
    with col3:
        st.markdown(f'<div class="box-title"><a href="#proceso_sin_descargar" target="_self">Rellenar formato Sinco</a></div>', unsafe_allow_html=True)
        st.markdown('<p class="box-text">Extrae información de FE formato Dian y contabiliza masivamente en el formato SINCO.</p>', unsafe_allow_html=True)

    # Descripción o bienvenida adicional
    st.markdown("""
    ### ¡Gracias por usar nuestra aplicación!
    Esta plataforma está diseñada para brindarte la mejor experiencia al manejar tus datos.
    Puedes empezar seleccionando alguna de las opciones anteriores para continuar.
    """)

    # Agregar alguna funcionalidad adicional si es necesario
    st.markdown("""
    - Para más información, consulta la [documentación](#).
    - Si tienes alguna duda, contáctanos en soporte@example.com.
    """)


