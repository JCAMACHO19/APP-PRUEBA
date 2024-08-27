import os
import zipfile
import fitz  # PyMuPDF
import shutil

UPLOAD_FOLDER = os.path.abspath("")

# Ruta de la carpeta principal donde se encuentran las subcarpetas
folder_path = os.path.join(UPLOAD_FOLDER, "archivos_usuarios")

# Lista de archivos a excluir
excluir_archivos = [
    'Cuenta_contable.xlsx',
    'MovDocCuenta_tratado.xlsx',
    'SINCO.xlsx',
    'DIAN.xlsx',
    'MovDocCuenta_Excel.xlsx'
]

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

# Recorrer todas las subcarpetas en "archivos_usuarios"
for subfolder in os.listdir(folder_path):
    subfolder_path = os.path.join(folder_path, subfolder)
    
    # Verificar que sea una subcarpeta
    if os.path.isdir(subfolder_path):
        # Ruta del archivo zip que se va a crear con el mismo nombre de la subcarpeta
        zip_file_path = os.path.join(folder_path, f'{subfolder}.zip')
        
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            # Recopilar y ordenar los archivos (.xls, .xlsx, luego .pdf)
            archivos_xls = []
            archivos_xlsx = []
            archivos_pdf = []

            for foldername, subfolders, filenames in os.walk(subfolder_path):
                for filename in filenames:
                    if filename in excluir_archivos:
                        continue  # Omitir los archivos que están en la lista de exclusión

                    file_path = os.path.join(foldername, filename)
                    if filename.endswith('.xls'):
                        archivos_xls.append((file_path, os.path.relpath(file_path, subfolder_path)))
                    elif filename.endswith('.xlsx'):
                        archivos_xlsx.append((file_path, os.path.relpath(file_path, subfolder_path)))
                    elif filename.endswith('.pdf'):
                        archivos_pdf.append((file_path, os.path.relpath(file_path, subfolder_path)))

            # Añadir los archivos .xls primero
            for file_path, arcname in archivos_xls:
                zipf.write(file_path, arcname)

            # Añadir los archivos .xlsx luego
            for file_path, arcname in archivos_xlsx:
                zipf.write(file_path, arcname)

            # Añadir los archivos PDF renombrados
            for file_path, arcname in archivos_pdf:
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
                zipf.write(file_path, os.path.join(os.path.dirname(arcname), nuevo_nombre))

        # Eliminar la subcarpeta original
        shutil.rmtree(subfolder_path)

print(f'Se han creado archivos zip para todas las subcarpetas en: {folder_path}, y las subcarpetas originales han sido eliminadas.')
