import logging
import os
from logging import Formatter, FileHandler
from flask import Flask, render_template, request, jsonify
from flask_uploads import UploadSet, configure_uploads, IMAGES

from ocr import process_image

_VERSION = 1 # API version


app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

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

@app.route('/upload', methods=['GET', 'POST'])
def upload():
  # if POST, user has uploaded a photo
  if request.method == 'POST' and 'photo' in request.files:
    filename = photos.save(request.files['photo'])
    return filename
  # otherwise, serve the webpage
  return render_template('upload.html')

@app.route('/v{}/ocr'.format(_VERSION), methods=["POST"])
def ocr():
  try:
    url = request.json['image_url']
    if 'jpg' in url:
      output = process_image(url)
      return jsonify({"output": output})
    else:
      return jsonify({"error": "only .jpg files, please"})
  except:
    return jsonify({"error": "Did you mean to send: {'image_url': 'some_jpeg_url'}"})


if not app.debug:
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
    app.run(host='0.0.0.0', port=port)
