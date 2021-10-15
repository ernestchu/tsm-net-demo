import os, sys
sys.path.append('tsm-net')
from tsmnet import Stretcher
import torchaudio
import soundfile as sf
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '.tmp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

stretcher = Stretcher('tsm-net/weights')
app = Flask(__name__)
app.secret_key = b'g chen is fucking handsome'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def stretch(dirs, filename, rate):
    x, sr = torchaudio.load(os.path.join(dirs, filename))
    x = torchaudio.transforms.Resample(orig_freq=sr, new_freq=22050)(x)
    sr = 22050
    filename = filename.split('.')
    filename[-2] += '-stretched'
    filename = '.'.join(filename)
    sf.write(os.path.join(dirs, filename), stretcher(x, rate).T, sr)
    return filename

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filename = stretch(
                app.config['UPLOAD_FOLDER'], filename,
                float(request.form['rate'])
            )
            return redirect(url_for('download_file', name=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <label for="rate">rate</label>
      <input id="rate" name="rate" type="number" step="any" min="0.01" value="0.75">
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
