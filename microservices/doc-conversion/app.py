from flask import Flask, request, jsonify, send_file
import os
import tempfile
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor
import subprocess
app = Flask(__name__)


def convert_docx_to_pdf(input_path):
    output_path = input_path.replace('.docx', '.pdf')
    try:
        subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(input_path), input_path], check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Conversion failed: {e}")


@app.route('/convert', methods=['POST'])
def convert():
    file = request.files.get('file')
    if not file or file.filename.split('.')[-1].lower() != 'docx':
        return jsonify({"error": "Invalid file format"}), 400

    try:
        filename = secure_filename(file.filename)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_input_path = os.path.join(temp_dir, filename)
            file.save(temp_input_path)

            with ThreadPoolExecutor() as executor:
                temp_output_path = executor.submit(convert_docx_to_pdf, temp_input_path).result()

            return send_file(temp_output_path, as_attachment=True, download_name='converted.pdf')

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5000')