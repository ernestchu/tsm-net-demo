import os, sys, subprocess
sys.path.append('tsm-net')
from tsmnet import Stretcher
import torch
import torchaudio
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '.tmp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# ALLOWED_EXTENSIONS = {'wav', 'mp3'}

stretcher = Stretcher('tsm-net/weights')
app = Flask(__name__)
CORS(app)
app.secret_key = b'g chen is fucking handsome'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def stretch(dirs, filename, rate):
    x, sr = torchaudio.load(os.path.join(dirs, filename))
    x = torchaudio.transforms.Resample(orig_freq=sr, new_freq=22050)(x)
    sr = 22050
    filename = filename.split('.')
    filename[-1] = 'mp3'
    filename = '.'.join(filename)
    torchaudio.save(os.path.join(dirs, filename), torch.from_numpy(stretcher(x, rate)), sr)
    return filename

def convert_to_wav(dirs, filename):
    new_filename = filename.split('.')
    if new_filename[-1] == 'wav':
        return filename, 0
    new_filename[-1] = 'wav'
    new_filename = '.'.join(new_filename)
    return new_filename, subprocess.run(
        f'ffmpeg -y -i {os.path.join(dirs, filename)} {os.path.join(dirs, new_filename)}',
        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode

@app.route('/', methods=['GET', 'POST'])
def demo():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # YT version
            if 'ytlink' not in request.form:
                flash('No file part or YouTube link')
                return redirect(request.url)
            ytlink = request.form['ytlink']
            filename = ytlink[-5:] + '.webm'
            filename = secure_filename(filename)
            status = subprocess.run(
                f'youtube-dl -f worstaudio {ytlink} -o {os.path.join(app.config["UPLOAD_FOLDER"], filename)}',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
            if status != 0:
                flash('Cannot download the YouTube video')
                return redirect(request.url)

            filename, status = convert_to_wav(app.config['UPLOAD_FOLDER'], filename)
            if status != 0:
                flash('Download fail corrupted')
                return redirect(request.url)
            filename = stretch(
                app.config['UPLOAD_FOLDER'], filename,
                float(request.form['rate'])
            )
            return redirect(url_for('download_file', name=filename))

        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if '.' not in file.filename or '.' == file.filename[-1]:
            flash('No file extension')
            return redirect(request.url)
        if file: # and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if '.' not in filename: # when filename contains only Chinese
                filename = 'audio.' + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filename, status = convert_to_wav(app.config['UPLOAD_FOLDER'], filename)
            if status != 0:
                flash('Not an audio file')
                return redirect(request.url)
            filename = stretch(
                app.config['UPLOAD_FOLDER'], filename,
                float(request.form['rate'])
            )
            return redirect(url_for('download_file', name=filename))
    return render_template_string('''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <label for="rate">rate</label>
      <input id="rate" name="rate" type="range" step="0.01" min="0.01" max="2" value="0.75"
       oninput="this.nextElementSibling.value = this.value"
       style="width: 400px;">
      <output>0.75</output>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    <h1>From YouTube</h1>
    <form method=post>
      <label for="rate">rate</label>
      <input id="rate" name="rate" type="range" step="0.01" min="0.01" max="2" value="0.75"
       oninput="this.nextElementSibling.value = this.value"
       style="width: 400px;">
      <output>0.75</output>
      <label for="ytlink">YouTube Link</label>
      <input id="ytlink" name="ytlink">
      <input type=submit value=submit>
    </form>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <script>
        {% for message in messages %}
            alert('{{ message }}')
        {% endfor %}
        </script>
      {% endif %}
    {% endwith %}
    ''')

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
