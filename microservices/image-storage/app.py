#app.py
from flask import Flask, flash, request, redirect, url_for, render_template
#import urllib.request
import os
from werkzeug.utils import secure_filename
import sys

import boto3
 
app = Flask(__name__)
 
UPLOAD_FOLDER = 'static/uploads/'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file_to_s3(file, bucket_name, object_name=None):
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_fileobj(file, bucket_name, object_name or file.filename)
    except Exception as e:
        print(f"Error uploading file: {e}", file=sys.stderr)
        return False
    return True


def create_presigned_url(bucket_name, object_name, expiration=3600):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name, 'Key': object_name},
                                                    ExpiresIn=expiration)
    except Exception as e:
        print(f"Error generating pre-signed URL: {e}")
        return None
    return response


@app.route('/')
def home():
    return render_template('index.html')
 
@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        #print('upload_image filename: ' + filename)
        if upload_file_to_s3(file, os.environ['BUCKET_NAME'], filename):
            flash('Image successfully uploaded and displayed below')
            presigned_url = create_presigned_url(os.environ['BUCKET_NAME'], filename)
            return render_template('index.html', filename=filename, image_url=presigned_url)
        else:
            flash('An error occurred when uploading the image')
            return redirect(request.url)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)

"""
@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    #upload_file_to_s3(f'static/uploads/{filename}', filename)
    #s3_url = f"https://{os.environ['BUCKET_NAME']}.s3.{os.environ['AWS_DEFAULT_REGION']}.amazonaws.com/{filename}"
    #return redirect(s3_url, code=301)
    #return redirect(url_for('static', filename='uploads/' + filename), code=301)
    presigned_url = create_presigned_url(os.environ['BUCKET_NAME'], filename)
    if presigned_url:
        return redirect(presigned_url, code=301)
    else:
        flash('Error generating pre-signed URL')
        return redirect(url_for('home'))
    #return filename
"""

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5000')