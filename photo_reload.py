#photo_reload.py
 
from flask import Flask, render_template
import glob
from time import time
import numpy as np
import cv2

app = Flask(__name__)
start_time=time()

@app.route("/")
def index():
    video_capture() 
    # 画像ファイルパスを取得
    #img_path = glob.glob("static/nonlabel/*.jpg")
    #i=int(np.random.rand()*(len(img_path))-1)+1
    return render_template('index.html', img="static/nonlabel/gazo1000.jpg")  #img_path[])

def video_capture():
    cap = cv2.VideoCapture(0)
    FRAME_RATE=1
    ret, frame = cap.read()

    # ウィンドウの準備
    #cv2.namedWindow('frame')
    i=0
    #cv2.waitKey(1000)
    while ret == True:
        #cv2.imshow('frame',frame)
        cv2.imwrite("static/nonlabel/gazo"+str(i)+".jpg",frame)
        #なんかKey押せば止まる
        if cv2.waitKey(1000*FRAME_RATE) >= 0:  
            break
        elif i>=1:
            cv2.imwrite("static/nonlabel/gazo"+str(1000)+".jpg",frame)
            break
        i+=1    
        ret, frame = cap.read()

    cap.release()
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    app.debug = True
    app.run(host= '0.0.0.0')

