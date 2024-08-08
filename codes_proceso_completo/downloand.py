from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import openpyxl
import os
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Función para leer los CUFEs desde un archivo Excel
def leer_cufes_desde_excel(archivo_excel):
    try:
        libro = openpyxl.load_workbook(archivo_excel)
        hoja = libro.active
        cufes = []
        for fila in hoja.iter_rows(min_row=2, values_only=True):  # Asumiendo que la primera fila es el encabezado
            cufe = fila[1]  # Índice CUFE está en la segunda columna
            estado = fila[13]  # Estado Factura
            if estado not in ['Contabilizado', 'Anulado', 'Anulada', 'COSTO MUNICIPIO LA GLORIA', 'COSTO MUNICIPIO SAN CAYETANO', 'COSTO MUNICIPIO SAN JOSE DE CUCUTA']:
                cufes.append(cufe)
        return cufes
    except Exception as e:
        logging.error(f'Error al leer el archivo Excel: {e}')
        return []

# Función para buscar y descargar una factura usando el CUFE
def buscar_y_descargar_factura(driver, cufe, carpeta_descargas):
    nombre_archivo = os.path.join(carpeta_descargas, f'{cufe}.pdf')
    if os.path.exists(nombre_archivo):
        logging.info(f'La factura para el CUFE {cufe} ya existe. No se descargará nuevamente.')
        return True  # Retorna True si la factura ya fue descargada

    try:
        driver.get('https://catalogo-vpfe.dian.gov.co/User/SearchDocument')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'DocumentKey')))

        campo_cufe = driver.find_element(By.ID, 'DocumentKey')
        campo_cufe.clear()  # Asegurarse de que el campo esté vacío antes de ingresar el CUFE
        campo_cufe.send_keys(cufe)
        time.sleep(1)  # Asegurarse de que el CUFE se ingrese completamente
        campo_cufe.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="html-gdoc"]/div[3]/div/div[1]/div[3]/p/a')))
        enlace_descarga = driver.find_element(By.XPATH, '//*[@id="html-gdoc"]/div[3]/div/div[1]/div[3]/p/a')
        enlace_descarga.click()

        time.sleep(5)  # Ajusta según sea necesario
        logging.info(f'Intentando descargar la factura para CUFE {cufe}.')
        return True
    except EC.TimeoutException:
        logging.error(f'Tiempo de espera agotado para la carga de elementos en la página.')
        reiniciar_navegador(driver)
        return False
    except Exception as e:
        logging.error(f'Error al intentar descargar la factura para CUFE {cufe}: {e}')
        reiniciar_navegador(driver)
        return False

# Función para reiniciar el navegador en caso de error
def reiniciar_navegador(driver):
    try:
        driver.quit()
        logging.info('Reiniciando el navegador...')
        time.sleep(3)
        driver = configurar_descargas(carpeta_descargas)
        if driver:
            logging.info('Navegador reiniciado correctamente. Continuando con la descarga.')
        else:
            logging.error('No se pudo reiniciar el navegador. Abortando descarga.')
    except Exception as e:
        logging.error(f'Error al reiniciar el navegador: {e}')

# Función para configurar la carpeta de descargas del navegador
def configurar_descargas(carpeta_descargas):
    if not os.path.exists(carpeta_descargas):
        os.makedirs(carpeta_descargas)

    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": carpeta_descargas,
        "download.prompt_for_download": False,
        "directory_upgrade": True
    }
    options.add_experimental_option("prefs", prefs)
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        logging.error(f'Error al configurar el navegador: {e}')
        return None

# Función para descargar facturas en paralelo
def descargar_facturas_en_paralelo(cufes, carpeta_descargas):
    def tarea(cufe):
        driver = configurar_descargas(carpeta_descargas)
        if driver:
            resultado = buscar_y_descargar_factura(driver, cufe, carpeta_descargas)
            driver.quit()
            return cufe, resultado
        return cufe, False

    with ThreadPoolExecutor(max_workers=3) as executor:
        resultados = list(executor.map(tarea, cufes))

    return resultados

UPLOAD_FOLDER =  os.path.abspath("")

# Ejemplo de uso
archivo_excel = os.path.join(UPLOAD_FOLDER, "archivos_usuarios", "archivo final.xlsx")
carpeta_descargas = os.path.join(UPLOAD_FOLDER, "archivos_usuarios")

# Leer los CUFEs desde el archivo Excel
cufes = leer_cufes_desde_excel(archivo_excel)

# Descargar facturas en paralelo
resultados = descargar_facturas_en_paralelo(cufes, carpeta_descargas)

# Verificar resultados y realizar un segundo pase si es necesario
cufes_faltantes = [cufe for cufe, descargado in resultados if not descargado]
if cufes_faltantes:
    logging.info(f'Las siguientes facturas no se descargaron en el primer pase: {cufes_faltantes}')
    logging.info('Intentando descargar las facturas faltantes...')
    resultados_segundo_pase = descargar_facturas_en_paralelo(cufes_faltantes, carpeta_descargas)
    # Aquí puedes agregar lógica adicional para manejar los resultados del segundo pase si es necesario

logging.info('Proceso de descarga completado.')