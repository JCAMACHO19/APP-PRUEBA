import pandas as pd
import os
import logging
import openpyxl
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

UPLOAD_FOLDER = os.path.abspath("")

# Función para leer los CUFEs desde un archivo Excel
def leer_cufes_desde_excel(archivo_excel):
    try:
        libro = openpyxl.load_workbook(archivo_excel)
        hoja = libro.active
        cufes = []
        for fila in hoja.iter_rows(min_row=2, values_only=True):  # Asumiendo que la primera fila es el encabezado
            cufe = fila[1]  # Índice CUFE está en la segunda columna
            estado = fila[13]  # Estado Factura
            if estado not in ['Contabilizado', 'Anulado', 'Anulada', 'No procesado']:
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
        return

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
    except Exception as e:
        if isinstance(e, EC.TimeoutException):
            logging.error(f'Error de TimeoutException para CUFE {cufe}. Reiniciando pestaña...')
            reiniciar_navegador(driver, carpeta_descargas)
            buscar_y_descargar_factura(driver, cufe, carpeta_descargas)
        else:
            logging.error(f'Error al intentar descargar la factura para CUFE {cufe}: {e}')
            reiniciar_navegador(driver, carpeta_descargas)

# Función para reiniciar el navegador en caso de error
def reiniciar_navegador(driver, carpeta_descargas):
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

# Obtener la lista de subcarpetas dentro de "archivos_usuarios"
subcarpetas = [os.path.join(UPLOAD_FOLDER, "archivos_usuarios", d) for d in os.listdir(os.path.join(UPLOAD_FOLDER, "archivos_usuarios")) if os.path.isdir(os.path.join(UPLOAD_FOLDER, "archivos_usuarios", d))]

# Asegurarse de que hay subcarpetas disponibles
if not subcarpetas:
    raise ValueError("No se encontraron subcarpetas dentro de la carpeta 'archivos_usuarios'.")

# Iterar sobre cada subcarpeta para procesar los archivos dentro de ella
for subcarpeta in subcarpetas:
    # Ruta del archivo de entrada en la subcarpeta
    archivo_excel = os.path.join(subcarpeta, "archivo final.xlsx")
    carpeta_descargas = subcarpeta  # Usar la misma subcarpeta para las descargas

    # Leer los CUFEs desde el archivo Excel
    cufes = leer_cufes_desde_excel(archivo_excel)

    # Configurar tres instancias del navegador
    drivers = [configurar_descargas(carpeta_descargas) for _ in range(3)]

    # Ejecutar la búsqueda y descarga en paralelo
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for cufe in cufes:
            futures.append(executor.submit(buscar_y_descargar_factura, drivers[len(futures) % 3], cufe, carpeta_descargas))

    # Esperar a que todas las tareas se completen
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            logging.error(f'Error en la tarea: {e}')

    # Cerrar todos los navegadores al finalizar
    for driver in drivers:
        if driver:
            driver.quit()

logging.info('Proceso de descarga completado.')
