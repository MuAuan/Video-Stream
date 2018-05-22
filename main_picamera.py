#!/usr/bin/env python
# main.py

from flask import Flask, render_template, Response
from camera import Camera
import cv2
import glob
from PIL import Image 
import picamera 
import time
     

app = Flask(__name__)

def cv_fourcc(c1, c2, c3, c4):
    return (ord(c1) & 255) + ((ord(c2) & 255) << 8) + \
        ((ord(c3) & 255) << 16) + ((ord(c4) & 255) << 24)

@app.route('/')
def index():
    img_path = glob.glob("static/nonlabel/*")
    return render_template('index_old.html', img=img_path)

@app.route('/photo', methods=['POST'])
def photo():
    take_photo()
    return redirect(url_for('hello'))

def take_photo():
     now = datetime.datetime.now()
     timeString = now.strftime("%Y%m%d%H%M")
     dirname = "/var/flask/static/"
     db_img_file = timeString + ".jpg"
     filename = dirname + db_img_file
     camera = picamera.PiCamera()
     camera.resolution = (512, 389)
     time.sleep(2)
     camera.capture(filename)
     camera.close()

def take_photo2():
     now = time.time()
     #timeString = now.strftime("%Y%m%d%H%M")
     dirname = "static/nolabel/"
     db_img_file = str(int(now)) + ".jpg"
     filename = dirname + db_img_file
     #camera = picamera.PiCamera()
     #camera.resolution = (512, 389)
     cap = cv2.VideoCapture(0)
     FRAME_RATE=1
     ret, frame = cap.read()

# Define the codec and create VideoWriter object
     height, width, channels = frame.shape
     out = cv2.VideoWriter(filename, \
                      cv_fourcc('X', 'V', 'I', 'D'), \
                      FRAME_RATE, \
                      (width, height), \
                      True)  #isColor=True for color

# ウィンドウの準備
     cv2.namedWindow('frame')

     cv2.imshow('frame',frame)
     out.write(frame)     
     time.sleep(2)
     cv2.capture(0)  #filename)
     #camera.close()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/static')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    #app.run(host= '0.0.0.0', debug=True)
    app.run(debug=False)