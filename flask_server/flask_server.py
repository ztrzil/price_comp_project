import sys
import logging
import os
import time
import random
from logging import Formatter, FileHandler
from flask import Flask, render_template, request, jsonify, flash, url_for, redirect
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.utils import secure_filename

from ocr import process_image

_VERSION = 1 # API version
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])
#UPLOAD_DIR = 'uploads/img'

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

# TODO: Set this key properly
app.secret_key = 'abcd1234'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads/img'
configure_uploads(app, photos)


@app.errorhandler(500)
def internal_error(error):
    print str(error)


@app.errorhandler(404)
def not_found_error(error):
    print str(error)


@app.route('/')
def render_home_page():
  return render_template('index.html')

@app.route('/test')
def render_page():
  return render_template('test.html')

def allowed_files(f):
  return '.' in f and \
    f.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload():
  # if POST, user has uploaded a photo
  if request.method == 'POST' and 'photo' in request.files:
    pic = request.files['photo']
    if pic.filename == '':
      # TODO: handle error 
      flash('No File Selected', 'error') 
      return redirect(request.url)
    if pic and allowed_files(pic.filename):
      f = request.files['photo']
      f.filename = str(time.time()).split('.')[0] + '.' + f.filename.split('.')[-1]
      print('My new file name: ' + f.filename)
      photos.save(f)
      #filename = photos.save(request.files['photo'])
      #TODO: create web page for uploading
      #return pic.filename 
      return "Picture Uploaded"
  # otherwise, serve the webpage
  return render_template('upload.html')


#@app.route('/v{}/ocr'.format(_VERSION), methods=["POST"])
@app.route('/ocr')
def ocr():
  f = 'uploads/img/'
  output = 'Error'
  try:
    f += random.choice(os.listdir('uploads/img/'))
    output = do_ocr(f)
    #return jsonify({"output": output})
  except:
    print('Error')
    return 'Error'
  return json.dumps(output)
  return jsonify({"output": output})

if not app.debug:
    if not os.path.exists('log/'):
        os.makedirs('log/')
    file_handler = FileHandler('log/error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: \
            %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
