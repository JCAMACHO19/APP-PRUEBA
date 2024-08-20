import PyPDF2
import re
import pandas as pd
from io import StringIO
import os

def pdf_to_text(pdf_path):
    # Abre el archivo PDF
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        number_of_pages = len(reader.pages)
        text = ''

        # Extrae el texto de cada página
        for page_number in range(number_of_pages):
            page = reader.pages[page_number]
            text += page.extract_text()
    
    return text

UPLOAD_FOLDER = os.path.abspath("")

# Ruta base donde se buscarán las subcarpetas
base_path = os.path.join(UPLOAD_FOLDER, "extractos", "COLPATRIA")

# Buscar el archivo PDF en cualquier subcarpeta
pdf_path = None
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.lower().endswith('.pdf'):
            pdf_path = os.path.join(root, file)
            break
    if pdf_path:
        break

if not pdf_path:
    raise FileNotFoundError("No se encontró un archivo PDF en las subcarpetas de '{}'.".format(base_path))

# Extrae el texto del PDF
texto_pdf = pdf_to_text(pdf_path)

# Usa StringIO para simular un archivo en memoria
archivo_en_memoria = StringIO(texto_pdf)

# Lista de codificaciones a probar
codificaciones = ['latin-1']

# Expresión regular para coincidir con la estructura de las líneas de interés
pattern = re.compile(r"^(\d{1,2}/\d{1,2}/\d{4})\s+([^;]+)\s*([^;]*)\s+([^;]+)\s+([\d.,-]+)\s+([\d.,-]+)\s*$")

# Intentar leer el archivo con diferentes codificaciones
for codificacion in codificaciones:
    try:
        archivo_en_memoria.seek(0)  # Resetea el puntero del archivo en memoria
        lineas = archivo_en_memoria.readlines()
        break
    except Exception as e:
        print(f"No se pudo leer el archivo con la codificación {codificacion}: {e}")
else:
    raise ValueError("No se pudo leer el archivo con las codificaciones proporcionadas.")

# Filtrar las líneas que coinciden con el patrón o tienen la estructura deseada
data = []
for linea in lineas:
    # Verificar si la línea contiene el patrón deseado o la estructura específica
    if pattern.match(linea) or "IMP/TRANS FINANC/ACUM MES" in linea:
        match = pattern.match(linea)
        if match:
            data.append(match.groups())
        else:
            # Procesar la línea "IMP/TRANS FINANC/ACUM MES"
            partes = linea.strip().split()
            fecha = ""
            oficina = ""
            no_docum = ""
            descripcion = " ".join(partes[:-2])
            monto = partes[-2]
            saldo = partes[-1]
            data.append((fecha, oficina, no_docum, descripcion, monto, saldo))

# Crear un DataFrame de pandas con los datos filtrados
df = pd.DataFrame(data, columns=["Fecha", "OFICINA", "No DOCUM", "DESCRIPCION", "MONTO", "SALDO"])

# Crear la nueva columna "Descripcion" combinando "OFICINA" y "DESCRIPCION"
df["Descripcion"] = df["OFICINA"] + " " + df["DESCRIPCION"]

# Convertir las columnas de MONTO y SALDO a numérico (eliminar puntos y comas)
df["MONTO"] = df["MONTO"].str.replace('.', '').str.replace(',', '.').astype(float)
df["SALDO"] = df["SALDO"].str.replace('.', '').str.replace(',', '.').astype(float)

# Calcular la moda de la columna "Fecha"
fecha_moda = df.loc[df["Fecha"] != "", "Fecha"].mode()[0]

# Rellenar los valores vacíos en la columna "Fecha" con la moda
df["Fecha"] = df["Fecha"].replace("", fecha_moda)

# Crear las columnas de Créditos y Débitos
df["Creditos"] = df["MONTO"].apply(lambda x: -x if x < 0 else None)
df["Debitos"] = df["MONTO"].apply(lambda x: x if x > 0 else None)

# Reordenar las columnas y eliminar las columnas no deseadas
df = df[["Fecha", "No DOCUM", "Descripcion", "Creditos", "Debitos"]]

# Renombrar las columnas según los requisitos
df.columns = ["Fecha", "No_Operacion", "Descripcion", "Creditos", "Debitos"]

# Crear la ruta del archivo Excel de salida en la misma subcarpeta donde se encontró el PDF
output_folder = os.path.dirname(pdf_path)
output_excel_path = os.path.join(output_folder, "COLPATRIA.xlsx")

# Guardar el DataFrame resultante en un archivo Excel
df.to_excel(output_excel_path, index=False)

print(f"Las líneas filtradas se han guardado en '{output_excel_path}'")
