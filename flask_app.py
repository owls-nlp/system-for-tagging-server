import os
from flask import Flask, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask import send_from_directory
import sqlite3
import random
import string
import json
from gevent.pywsgi import WSGIServer

UPLOAD_FOLDER = './uploaded_files/'
RESULT_FOLDER = './output/'

ALLOWED_EXTENSIONS = set(['pdf'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER


def check_token_active(token: str) -> bool:
    conn = sqlite3.connect("tagging_system.db")
    cursor = conn.cursor()

    sql = f"SELECT is_active FROM tokens WHERE token='{token}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) > 0:
        if result[0][0] == 1:
            return True
        else:
            return False
    else:
        return False


def save_fileinfo_db(path_to_file: str, request_data:dict, token: str, file_name_original:str) -> int:
    conn = sqlite3.connect("tagging_system.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO files_info ('pdf_path', 'token', 'column_type', 'langs', 'original_filename', 'document_type') VALUES (?, ?, ?, ?, ?, ?);", (path_to_file, token, request_data['column_type'], request_data['langs'], file_name_original, request_data['file_type']))
    conn.commit()

    sql = f"SELECT * FROM files_info WHERE pdf_path='{path_to_file}' and token='{token}'"
    cursor.execute(sql)
    result = cursor.fetchall()

    return result[0][0]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/verifytoken', methods=['POST'])
def verify_token():
    if request.method == 'POST':
        reques_data = dict(request.form)
        if check_token_active(reques_data['token']):
            return 'YES'
        else:
            return 'NO'


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check is token in DB
        if check_token_active(request.environ['HTTP_AUTHORIZATION']):
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return 'no_file'
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return 'no_file'
            if file and allowed_file(file.filename):
                file_name_original = secure_filename(file.filename)
                rand_str = lambda n: ''.join([random.choice(string.ascii_lowercase) for i in range(n)])  
                filename = rand_str(20) + '.pdf'
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                reques_data = dict(request.form)
                file_id = save_fileinfo_db(os.path.join(app.config['UPLOAD_FOLDER'], filename), reques_data, request.environ['HTTP_AUTHORIZATION'], file_name_original)
                return str(file_id)
        else:
            return 'bad_token'
    else:
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>HELLO!</h1>
        '''


@app.route('/isfileready/<fileid>', methods=['POST'])
def is_file_ready(fileid):
    fileid = int(fileid)

    token = request.environ['HTTP_AUTHORIZATION']

    conn = sqlite3.connect("tagging_system.db")
    cursor = conn.cursor()

    sql = f"SELECT * FROM files_info WHERE id='{fileid}' and token='{token}'"
    cursor.execute(sql)
    result = cursor.fetchall()

    if len(result) > 0:
        if result[0][3] is None:
            return 'NO'
        else:
            return 'YES'
    return 'NO'


@app.route('/getfilename/<fileid>', methods=['POST'])
def get_file_name(fileid):
    fileid = int(fileid)

    token = request.environ['HTTP_AUTHORIZATION']

    conn = sqlite3.connect("tagging_system.db")
    cursor = conn.cursor()

    sql = f"SELECT * FROM files_info WHERE id='{fileid}' and token='{token}'"
    cursor.execute(sql)
    result = cursor.fetchall()

    if len(result) > 0:
        if result[0][3] is not None:
            return result[0][3].split('/')[-1]
    return 'ERROR'


@app.route('/download/<fileid>', methods=['POST'])
def download_file(fileid):
    fileid = int(fileid)

    token = request.environ['HTTP_AUTHORIZATION']

    conn = sqlite3.connect("tagging_system.db")
    cursor = conn.cursor()

    sql = f"SELECT * FROM files_info WHERE id='{fileid}' and token='{token}'"
    cursor.execute(sql)
    result = cursor.fetchall()

    if len(result) > 0:
        if result[0][3] is not None:
            filename = result[0][3].split('/')[-1]
            return send_from_directory(app.config['RESULT_FOLDER'],
                               filename)
    return 'ERROR'


if __name__ == '__main__':
    app.secret_key = 'cwq$tdf-er56m(bi&1@-7t74@1i*r-4j4@m@w#isv1ud9r(b4('
    http_server = WSGIServer(('0.0.0.0', 5000), app, keyfile='key.pem', certfile='cert.pem')
    http_server.serve_forever()