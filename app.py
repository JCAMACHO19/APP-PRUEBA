from flask import Flask, render_template, request, redirect, url_for, flash
import shutil
import os
import subprocess
import sys

app = Flask(__name__)
app.secret_key = 'secret_key'

UPLOAD_FOLDER = 'C:/Users/jcamacho/Desktop/PRUEBA IMPORTE DE DOCUMENTOS'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'dian_file' not in request.files or 'sinco_file' not in request.files or 'cuentas_file' not in request.files:
        flash('Todos los archivos deben ser seleccionados', 'error')
        return redirect(url_for('index'))

    dian_file = request.files['dian_file']
    sinco_file = request.files['sinco_file']
    cuentas_file = request.files['cuentas_file']

    if dian_file and sinco_file and cuentas_file:
        dian_path = os.path.join(UPLOAD_FOLDER, 'DIAN.xlsx')
        sinco_path = os.path.join(UPLOAD_FOLDER, 'SINCO.xlsx')
        cuentas_path = os.path.join(UPLOAD_FOLDER, 'MovDocCuenta_CSV.csv')

        dian_file.save(dian_path)
        sinco_file.save(sinco_path)
        cuentas_file.save(cuentas_path)

        try:
            result = subprocess.run([sys.executable, os.path.join(UPLOAD_FOLDER, 'ejecutar.py'), dian_path, sinco_path, cuentas_path], check=True, capture_output=True, text=True)
            flash('El script se ejecutó con éxito', 'success')
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            flash(f'Error al ejecutar el script: {e.stderr}', 'error')
            print(e.stderr)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)