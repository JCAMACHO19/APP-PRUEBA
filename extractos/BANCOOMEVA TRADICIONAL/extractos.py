import os
from PyPDF2 import PdfReader

def pdf_to_text(pdf_path, txt_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PdfReader(pdf_file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)

def convert_pdfs_in_directory(directory):
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            txt_filename = os.path.splitext(filename)[0] + '.txt'
            txt_path = os.path.join(directory, txt_filename)
            pdf_to_text(pdf_path, txt_path)
            print(f"Converted {pdf_path} to {txt_path}")

UPLOAD_FOLDER = os.path.abspath("")            

if __name__ == "__main__":
    directory = os.path.join(UPLOAD_FOLDER, "BANCOOMEVA TRADICIONAL")
    convert_pdfs_in_directory(directory)
