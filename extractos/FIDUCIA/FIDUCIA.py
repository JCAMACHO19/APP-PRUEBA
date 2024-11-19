import os
import re
from PyPDF2 import PdfReader

def pdf_to_text(pdf_path, txt_path):
    """
    Convierte un archivo PDF a texto y filtra/modifica las líneas según patrones y palabras clave.
    """
    with open(pdf_path, 'rb') as pdf_file:
        reader = PdfReader(pdf_file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()

    # Filtrar las líneas según el patrón y las palabras clave
    lines = text.splitlines()
    filtered_lines = []

    # Definir los patrones
    patron_fecha_valor = r"\d{2} \w{3} \d{2} .+ \$ [\d,.]+ [-]?[\d,.]+"
    patron_rendimientos = r"RENDIMIENTOS \$ [\d,.]+"

    for linea in lines:
        linea = linea.strip()  # Eliminar espacios en blanco extra

        # Filtrar las líneas que contienen 'INGRESOS', 'EGRESOS' o coinciden con los patrones
        if ('INGRESOS' in linea or
            'EGRESOS' in linea or
            re.match(patron_rendimientos, linea) or
            re.match(patron_fecha_valor, linea)):

            # Modificar las líneas que coinciden con los patrones
            if re.match(patron_rendimientos, linea):
                # Modificar líneas que coinciden con el patrón de rendimientos
                linea_modificada = re.sub(r"(RENDIMIENTOS)( \$ [\d,.]+)", r"\1 ;\2", linea)
            elif re.match(patron_fecha_valor, linea):
                # Modificar líneas que coinciden con el patrón de fecha, valor y número decimal
                linea_modificada = re.sub(
                    r"(\d{2} \w{3} \d{2} .+)( \$ [\d,.]+) [-]?([\d,.]+)",
                    r"\1; \2; \3",
                    linea
                )
            else:
                # Conservar la línea tal cual si no requiere modificación
                linea_modificada = linea

            filtered_lines.append(linea_modificada)

    # Guardar solo las líneas filtradas en el archivo de texto
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write('\n'.join(filtered_lines))

def convert_pdfs_in_directory(base_directory):
    """
    Recorre un directorio y sus subdirectorios, convierte archivos PDF a texto y filtra el contenido.
    """
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                txt_filename = os.path.splitext(file)[0] + '.txt'
                txt_path = os.path.join(root, txt_filename)
                pdf_to_text(pdf_path, txt_path)
                print(f"Converted {pdf_path} to {txt_path}")

if __name__ == "__main__":
    # Define el directorio base donde están los PDF
    base_directory = os.path.abspath(os.path.join("extractos", "FIDUCIA"))
    convert_pdfs_in_directory(base_directory)

