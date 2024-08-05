import os
import zipfile
import xlrd
import xlwt
from xlutils.copy import copy
import fitz  # PyMuPDF

# Ruta de la carpeta donde se encuentran los archivos
folder_path = r'C:\Users\jcamacho\Desktop\PRUEBA IMPORTE DE DOCUMENTOS'

# Ruta del archivo zip que se va a crear
zip_file_path = os.path.join(folder_path, 'archivos_comprimidos.zip')

# Función para buscar variables en el texto extraído del documento PDF
def buscar_variables(documento):
    variables = {
        "Número de Factura:": None,
        "Fecha de Emisión:": None,
        "Razón Social:": None
    }

    for page_num in range(documento.page_count):
        page = documento.load_page(page_num)
        texto = page.get_text()

        for variable in variables:
            if variable in texto:
                index = texto.find(variable)
                if index != -1:
                    start_index = index + len(variable)
                    end_index = texto.find('\n', start_index)
                    if end_index == -1:
                        end_index = None
                    variables[variable] = texto[start_index:end_index].strip()

    return variables

# Crear un archivo zip y renombrar los PDFs dentro del zip
with zipfile.ZipFile(zip_file_path, 'w') as zipf:
    # Añadir todos los archivos PDF al archivo zip y renombrarlos
    for foldername, subfolders, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith('.pdf'):
                file_path = os.path.join(foldername, filename)
                
                # Abrir el archivo PDF
                documento = fitz.open(file_path)

                # Buscar las variables en el documento
                variables_encontradas = buscar_variables(documento)

                # Cerrar el documento PDF
                documento.close()

                # Construir el nuevo nombre de archivo
                nuevo_nombre = f"{variables_encontradas['Número de Factura:']}_{variables_encontradas['Razón Social:']}.pdf"
                nuevo_nombre = nuevo_nombre.replace("/", "-")  # Reemplazar '/' por '-' para evitar problemas en el nombre del archivo

                # Añadir el archivo PDF al zip con el nuevo nombre
                zipf.write(file_path, nuevo_nombre)
                os.remove(file_path)

    # Añadir una copia exacta del archivo "doc_importar.xls"
    doc_importar_path = os.path.join(folder_path, 'doc_importar.xls')
    if os.path.exists(doc_importar_path):
        zipf.write(doc_importar_path, os.path.relpath(doc_importar_path, folder_path))

    # Añadir el archivo "archivo final" y eliminarlo de la carpeta
    archivo_final_path = os.path.join(folder_path, 'archivo final.xlsx')
    if os.path.exists(archivo_final_path):
        zipf.write(archivo_final_path, os.path.relpath(archivo_final_path, folder_path))
        os.remove(archivo_final_path)

    # Eliminar todos los archivos .xlsx en la carpeta (excepto "doc_importar.xls")
    for foldername, subfolders, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith('.xlsx') and filename != 'doc_importar.xls':
                file_path = os.path.join(foldername, filename)
                os.remove(file_path)

# Eliminar datos de todas las filas excepto la primera en "doc_importar.xls"
rb = xlrd.open_workbook(doc_importar_path, formatting_info=True)
wb = copy(rb)
ws = wb.get_sheet(0)

# Obtener el número de filas
nrows = rb.sheet_by_index(0).nrows

# Borrar todas las filas excepto la primera
for row in range(1, nrows):
    for col in range(rb.sheet_by_index(0).ncols):
        ws.write(row, col, '')

# Guardar los cambios en el mismo archivo
wb.save(doc_importar_path)

print(f'Archivo zip creado en: {zip_file_path}')
print(f'Archivo "doc_importar.xls" actualizado: solo se mantiene la primera fila de datos.')
