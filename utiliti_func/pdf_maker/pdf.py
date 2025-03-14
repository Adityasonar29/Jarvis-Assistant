import os
from flask import Flask, request, send_file, render_template_string
from werkzeug.utils import secure_filename
import tempfile
from PIL import Image
import img2pdf
import docx2pdf
from PyPDF2 import PdfMerger
import pandas as pd
import markdown
import pdfkit
import zipfile
import io

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'docx', 'xlsx', 'txt', 'md', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_pdf(file_path):
    """Convert different file types to PDF"""
    file_ext = os.path.splitext(file_path)[1].lower().replace('.', '')
    output_path = os.path.splitext(file_path)[0] + '.pdf'
    
    # Image files
    if file_ext in ['png', 'jpg', 'jpeg', 'gif']:
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(file_path))
    
    # Word documents
    elif file_ext == 'docx':
        docx2pdf.convert(file_path, output_path)
    
    # Excel files
    elif file_ext == 'xlsx':
        df = pd.read_excel(file_path)
        html = df.to_html()
        pdfkit.from_string(html, output_path)
    
    # Text files
    elif file_ext == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        html = f"<pre>{text}</pre>"
        pdfkit.from_string(html, output_path)
    
    # Markdown files
    elif file_ext == 'md':
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        html = markdown.markdown(text)
        pdfkit.from_string(html, output_path)
    
    # If already PDF, return the original path
    elif file_ext == 'pdf':
        return file_path
    
    return output_path

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>File to PDF Converter</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            .form-container { border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
            .upload-btn { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; 
                          border-radius: 4px; cursor: pointer; margin-top: 10px; }
            .upload-btn:hover { background-color: #45a049; }
        </style>
    </head>
    <body>
        <h1>File to PDF Converter</h1>
        <div class="form-container">
            <form action="/convert" method="post" enctype="multipart/form-data">
                <p>Select file(s) to convert to PDF:</p>
                <input type="file" name="files" multiple>
                <br>
                <input type="submit" value="Convert to PDF" class="upload-btn">
            </form>
        </div>
    </body>
    </html>
    ''')

@app.route('/convert', methods=['POST'])
def convert_files():
    if 'files' not in request.files:
        return 'No file part', 400
    
    files = request.files.getlist('files')
    
    if not files or files[0].filename == '':
        return 'No files selected', 400
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    pdf_paths = []
    
    # Process each file
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            
            # Handle zip files
            if filename.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_dir = os.path.join(temp_dir, 'extracted_' + os.path.splitext(filename)[0])
                    os.makedirs(zip_dir, exist_ok=True)
                    zip_ref.extractall(zip_dir)
                    
                    # Convert each file in the zip
                    for root, _, files in os.walk(zip_dir):
                        for extracted_file in files:
                            if allowed_file(extracted_file):
                                extracted_path = os.path.join(root, extracted_file)
                                pdf_path = convert_to_pdf(extracted_path)
                                if pdf_path:
                                    pdf_paths.append(pdf_path)
            else:
                # Convert individual file
                pdf_path = convert_to_pdf(file_path)
                if pdf_path:
                    pdf_paths.append(pdf_path)
    
    # If we have PDFs to merge
    if pdf_paths:
        if len(pdf_paths) == 1:
            # If only one PDF, return it directly
            return send_file(pdf_paths[0], as_attachment=True, download_name="converted.pdf")
        else:
            # Merge multiple PDFs
            merger = PdfMerger()
            for pdf in pdf_paths:
                merger.append(pdf)
            
            merged_pdf = os.path.join(temp_dir, "merged.pdf")
            merger.write(merged_pdf)
            merger.close()
            
            return send_file(merged_pdf, as_attachment=True, download_name="merged.pdf")
    
    return 'No files were converted successfully', 400

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8080, debug=True)