import streamlit as st

def run(subfolder):
    st.markdown("## Bienvenido a Numetrix")
    st.markdown("Selecciona una de las opciones disponibles para ejecutar:")
    st.markdown("1. **Procesar Archivos**: Verifica y procesa facturas para integrarlas en tu sistema contable.")
    st.markdown("2. **Comparar Archivos**: Compara diferentes reportes para verificar inconsistencias.")
    st.markdown("3. **Descargar Archivos**: Descarga reportes procesados.")
    st.markdown("4. **Rellenar formato SINCO**: Extrae informacion de FE formato Dian y contabilzar masivamente.")
