import streamlit as st
import os

# Función para ejecutar la pestaña de inicio
def run(subfolder):
    # Título de la página
    st.title("Bienvenido")
    
    # Crear la ruta del directorio de las imágenes
    UPLOAD_FOLDER = "imagen"  # Carpeta donde están las imágenes
    subfolder = os.path.join(UPLOAD_FOLDER)
    os.makedirs(subfolder, exist_ok=True)

    # Rutas de las imágenes de cada caja
    image_paths = {
        "caja1": os.path.join(subfolder, "caja1.gif"),
        "caja2": os.path.join(subfolder, "caja2.gif"),
        "caja3": os.path.join(subfolder, "caja3.gif"),
        "caja4": os.path.join(subfolder, "caja4.gif"),
    }

    # Verificar que todas las imágenes existen
    for caja, path in image_paths.items():
        if not os.path.exists(path):
            st.error(f"No se encontró la imagen para {caja} en la ruta: {path}")
            return

    # Crear 4 columnas para los 4 cajones
    col1, col2, col3, col4 = st.columns(4)

    # Cajón 1: Procesar Archivos
    with col1:
        st.image(image_paths["caja1"], use_column_width=True)
        st.markdown("1. **Procesar Archivos**: Verifica y procesa facturas para integrarlas en tu sistema contable.")

    # Cajón 2: Comparar Archivos
    with col2:
        st.image(image_paths["caja2"], use_column_width=True)
        st.markdown("2. **Comparar Archivos**: Compara diferentes reportes para verificar inconsistencias.")

    # Cajón 3: Descargar Archivos
    with col3:
        st.image(image_paths["caja3"], use_column_width=True)
        st.markdown("3. **Descargar Archivos**: Descarga reportes procesados.")

    # Cajón 4: Rellenar formato SINCO
    with col4:
        st.image(image_paths["caja4"], use_column_width=True)
        st.markdown("4. **Rellenar formato SINCO**: Extrae información de FE formato Dian y contabiliza masivamente.")

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



