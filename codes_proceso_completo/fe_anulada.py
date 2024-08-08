import pandas as pd
import os

UPLOAD_FOLDER =  os.path.abspath("")

# Ruta del archivo de entrada
ruta_archivo = os.path.join(UPLOAD_FOLDER,"archivos_usuarios", "archivo final.xlsx")

# Cargar el archivo Excel
df = pd.read_excel(ruta_archivo)

# Modificar el archivo según la condición
df.loc[df['Tipo de documento'] == 'Application response', 'Estado de Factura'] = 'Anulada'

# Guardar el archivo modificado en la misma ruta con el mismo nombre
df.to_excel(ruta_archivo, index=False)
