from flask import Flask, render_template, request, redirect, url_for
import glob
import os
import shutil
import time
import numpy as np
import cv2

app = Flask(__name__)
start_time=time.time()

@app.route("/")
def index():

    # 画像ファイルパスを取得
    img_path = glob.glob("static/sample/*.jpg")
    # 分類するフォルダ名を取得
    category_path = [os.path.basename(path) for path in glob.glob("static/labeled/*")]    
    return render_template('index2.html', img=img_path[len(img_path)-1], category_list=category_path) 

@app.route("/sampling", methods=['POST'])
def sampling():
    # 分類するフォルダパスを取得
    category_path = os.path.join("static", os.path.join("labeled", request.form['category']))
    # ファイルの移動
    shutil.move(request.form['img_path'], category_path)

    cap = cv2.VideoCapture(0)
    FRAME_RATE=1
    ret, frame = cap.read()

    # ウィンドウの準備
    #cv2.namedWindow('frame')
    i=0
    while ret == True:
        ret, frame = cap.read()
        i+=1
        #time.sleep(1)
        #cv2.imshow('frame',frame)
        cv2.imwrite("static/sample/gazo"+str(int(10*(time.time()-start_time)))+".jpg",frame)
        #なんかKey押せば止まる
        if cv2.waitKey(1000*FRAME_RATE) >= 0:  
            break
        elif i>=1:
            #cv2.imwrite("static/sample/gazou.jpg",frame)
            break
        #i+=1    
        ret, frame = cap.read()

    cap.release()
    cv2.destroyAllWindows()

    return redirect("/")

if __name__ == "__main__":
    app.debug = True
    app.run()

