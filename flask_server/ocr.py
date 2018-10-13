import cv2
import pytesseract
import requests
from PIL import Image
from PIL import ImageFilter
from StringIO import StringIO


def process_image(file_path):
  results = {}
  image = _open_image(file_path)
  #image.filter(ImageFilter.SHARPEN)
  
  # Define config parameters.
  # '-l eng'  for using the English language
  # '--oem 1' for using LSTM OCR Engine
  config = ('-l eng --oem 1 --psm 3')

  img0, img1, img2 = processImage(image)
 
  # Run tesseract OCR on image
  results['method 0'] = pytesseract.image_to_string(img0, config=config)
  results['method 1'] = pytesseract.image_to_string(img1, config=config)
  results['method 2'] = pytesseract.image_to_string(img2, config=config)

  f = file_path.split('/')[-1].split('.')[0]
  with open(f + '.txt', 'w') as fp:
    for key, val in results.items():
      fp.write(key + '\n' + val + '\n')

  return results 
  #return pytesseract.image_to_string(image)


# Read image from disk
def _open_image(path):
  try:
    print('opening ' , path)
    #return Image.open(path)
    return cv2.imread(path, cv2.IMREAD_COLOR)
  except:
    #TODO catch specific exception(s)
    print('Error opening image')


  
def processImage(img):
  x_scale = 10.0
  y_scale = 10.0
  b = 64. # brightness
  c = 0.  # contrast

  img3 = cv2.addWeighted(img, 1. + c/127., img, 0, b-c)
  #-----Converting image to LAB Color model----------------------------------- 
  lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
  #cv2.imshow("lab",lab)

  #-----Splitting the LAB image to different channels-------------------------
  l, a, b = cv2.split(lab)
  #cv2.imshow('l_channel', l)
  #cv2.imshow('a_channel', a)
  #cv2.imshow('b_channel', b)

  #-----Applying CLAHE to L-channel-------------------------------------------
  clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
  cl = clahe.apply(l)
  #cv2.imshow('CLAHE output', cl)

  #img = cv2.imread('highContrast1.jpg', cv2.IMREAD_COLOR)
  #-----Merge the CLAHE enhanced L-channel with the a and b channel-----------
  limg = cv2.merge((cl,a,b))
  #cv2.imshow('limg', limg)

  #-----Converting image from LAB Color model to RGB model--------------------
  final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
  #cv2.imshow('final', final)

  #_____END_____#

  #call addWeighted function, which performs:
  #    dst = src1*alpha + src2*beta + gamma
  # we use beta = 0 to effectively only operate on src1
  final = cv2.resize(final, None, fx=x_scale, fy=y_scale, interpolation = cv2.INTER_CUBIC)
  cl = cv2.resize(cl, None, fx=x_scale, fy=y_scale, interpolation = cv2.INTER_CUBIC)
  img3 = cv2.resize(img3, None, fx=x_scale, fy=y_scale, interpolation = cv2.INTER_CUBIC)
  return cl, img3, final
