import pandas as pd
import os

UPLOAD_FOLDER = os.path.abspath("")

# Obtener la lista de subcarpetas dentro de "archivos_usuarios"
subcarpetas = [os.path.join(UPLOAD_FOLDER, "archivos_usuarios", d) for d in os.listdir(os.path.join(UPLOAD_FOLDER, "archivos_usuarios")) if os.path.isdir(os.path.join(UPLOAD_FOLDER, "archivos_usuarios", d))]

# Asegurarse de que hay subcarpetas disponibles
if not subcarpetas:
    raise ValueError("No se encontraron subcarpetas dentro de la carpeta 'archivos_usuarios'.")

# Iterar sobre cada subcarpeta para procesar los archivos dentro de ella
for subcarpeta in subcarpetas:
    # Ruta del archivo de entrada en la subcarpeta
    ruta_archivo = os.path.join(subcarpeta, "archivo final.xlsx")

    # Cargar el archivo Excel
    df = pd.read_excel(ruta_archivo)

    # Modificar el archivo según la primera condición
    df.loc[df['Tipo de documento'] == 'Application response', 'Estado de Factura'] = 'Anulada'

    # Nueva lógica: si 'Tipo de documento' es diferente a 'Factura electrónica' y 'Nota de crédito electrónica' 
    # y 'Estado de Factura' es 'Revisar', cambiar 'Estado de Factura' a 'No procesado'
    condicion = (df['Tipo de documento'] != 'Factura electrónica') & \
                (df['Tipo de documento'] != 'Nota de crédito electrónica') & \
                (df['Estado de Factura'] == 'Revisar')
    df.loc[condicion, 'Estado de Factura'] = 'No procesado'

    # Guardar el archivo modificado en la misma ruta con el mismo nombre
    df.to_excel(ruta_archivo, index=False)

print("Código ejecutado exitosamente")
