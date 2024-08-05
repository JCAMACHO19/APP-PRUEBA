import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os
import subprocess
import sys

class ArchivoSelector:
    def __init__(self, root):
        self.root = root
        self.ruta_dian = ''
        self.ruta_sinco = ''
        self.ruta_cuentas = ''
        
        self.create_widgets()
        
    def create_widgets(self):
        tk.Label(self.root, text="Seleccionar archivos para el procesamiento").pack(pady=10)
        
        # Botón para seleccionar archivo DIAN
        tk.Button(self.root, text="Seleccionar archivo DIAN", command=self.seleccionar_archivo_dian).pack(pady=5)
        self.label_dian = tk.Label(self.root, text="Archivo DIAN no seleccionado")
        self.label_dian.pack(pady=5)
        
        # Botón para seleccionar archivo SINCO
        tk.Button(self.root, text="Seleccionar archivo SINCO", command=self.seleccionar_archivo_sinco).pack(pady=5)
        self.label_sinco = tk.Label(self.root, text="Archivo SINCO no seleccionado")
        self.label_sinco.pack(pady=5)
        
        # Botón para seleccionar archivo CSV de cuentas contables
        tk.Button(self.root, text="Seleccionar archivo CSV de cuentas contables", command=self.seleccionar_archivo_cuentas).pack(pady=5)
        self.label_cuentas = tk.Label(self.root, text="Archivo CSV de cuentas contables no seleccionado")
        self.label_cuentas.pack(pady=5)
        
        # Botón para iniciar procesamiento
        self.btn_procesar = tk.Button(self.root, text="Iniciar Procesamiento", state=tk.DISABLED, command=self.ejecutar_script_principal)
        self.btn_procesar.pack(pady=20)
        
    def seleccionar_archivo_dian(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de DIAN",
            filetypes=(("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*"))
        )
        if archivo:
            self.ruta_dian = 'C:/Users/jcamacho/Desktop/PRUEBA IMPORTE DE DOCUMENTOS/DIAN.xlsx'
            shutil.copy(archivo, self.ruta_dian)
            self.label_dian.config(text=f"Archivo DIAN seleccionado: {os.path.basename(self.ruta_dian)}")
            self.verificar_archivos()

    def seleccionar_archivo_sinco(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de SINCO",
            filetypes=(("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*"))
        )
        if archivo:
            self.ruta_sinco = 'C:/Users/jcamacho/Desktop/PRUEBA IMPORTE DE DOCUMENTOS/SINCO.xlsx'
            shutil.copy(archivo, self.ruta_sinco)
            self.label_sinco.config(text=f"Archivo SINCO seleccionado: {os.path.basename(self.ruta_sinco)}")
            self.verificar_archivos()

    def seleccionar_archivo_cuentas(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de cuentas contables",
            filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*"))
        )
        if archivo:
            self.ruta_cuentas = 'C:/Users/jcamacho/Desktop/PRUEBA IMPORTE DE DOCUMENTOS/MovDocCuenta_CSV.csv'
            shutil.copy(archivo, self.ruta_cuentas)
            self.label_cuentas.config(text=f"Archivo CSV de cuentas contables seleccionado: {os.path.basename(self.ruta_cuentas)}")
            self.verificar_archivos()
            
    def verificar_archivos(self):
        if self.ruta_dian and self.ruta_sinco and self.ruta_cuentas:
            self.btn_procesar.config(state=tk.NORMAL)

    def ejecutar_script_principal(self):
        try:
            result = subprocess.run([sys.executable, 'ejecutar.py', self.ruta_dian, self.ruta_sinco, self.ruta_cuentas], check=True, capture_output=True, text=True)
            print("Script ejecutar.py ejecutado con éxito")
            print(result.stdout)
            messagebox.showinfo("Éxito", "El script se ejecutó con éxito")
        except subprocess.CalledProcessError as e:
            print("Error al ejecutar el script ejecutar.py")
            print(e.stderr)
            messagebox.showerror("Error", f"Error al ejecutar el script: {e.stderr}")

# Crear la ventana principal
root = tk.Tk()
root.title("Procesador de Archivos")
root.geometry("400x300")

# Crear el selector de archivos
selector = ArchivoSelector(root)

# Ejecutar la aplicación
root.mainloop()
