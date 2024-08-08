import pandas as pd
import os

UPLOAD_FOLDER = os.path.abspath("")

# Ruta del archivo de entrada
ruta_archivo = os.path.join(UPLOAD_FOLDER, "archivos_usuarios", "archivo final.xlsx")

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
