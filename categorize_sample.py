# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for
import glob
import os
import shutil
import time
import numpy as np
import cv2

import keras
from keras.models import Model, Input
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
from keras.preprocessing import image
import numpy as np
import sys

app = Flask(__name__)
start_time=time.time()

@app.route("/")
def index():
    img_path, category_path=yomikomi()
    return render_template('index2.html', img=img_path[len(img_path)-1], category=category_path) 

def yomikomi():
    batch_size = 32
    num_classes = 1000
    img_rows, img_cols=224,224
    input_tensor = Input((img_rows, img_cols, 3))
    # 画像ファイルパスを取得
    img_path =  glob.glob("static/sample/*.jpg")
    # 学習済みのVGG16をロード
    # 構造とともに学習済みの重みも読み込まれる
    
    vgg16 = VGG16(include_top=False, weights='imagenet', input_tensor=input_tensor)
    # FC層を構築
    top_model = Sequential()
    top_model.add(Flatten(input_shape=vgg16.output_shape[1:])) 
    top_model.add(Dense(256, activation='relu'))
    top_model.add(Dropout(0.5))
    top_model.add(Dense(num_classes, activation='softmax'))
    
    # VGG16とFCを接続
    model = Model(input=vgg16.input, output=top_model(vgg16.output))
    # Fine-tuningのときはSGDの方がよい⇒adamがよかった
    lr = 0.00001 #0.00001
    opt = keras.optimizers.Adam(lr, beta_1=0.5, beta_2=0.999, epsilon=1e-08, decay=1e-6) #1e-6
    #opt = keras.optimizers.SGD(lr=1e-4, momentum=0.9)
    model.compile(loss='categorical_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])
    model.summary()
    
    # 引数で指定した画像ファイルを読み込む
    # サイズはVGG16のデフォルトである224x224にリサイズされる
    #x=img_path[len(img_path)-1]
    x = image.load_img(img_path[len(img_path)-1], target_size=(224, 224))
    # 読み込んだPIL形式の画像をarrayに変換
    x = image.img_to_array(x)
    x = np.expand_dims(x, axis=0)
    preds = model.predict(preprocess_input(x))
    results = decode_predictions(preds, top=5)[0]
    for result in results:
        print(result)
    #preds ="〇"
    if preds =="x":
        preds= "./x"
    elif preds =="〇":
        preds="./〇"
    elif preds =="△":
        preds="./△"
    else:
        preds="./"+str(results[0][1])+str(int(100*results[0][2]))+".jpg"
       
    # 分類するフォルダ名を取得
    category_path = preds
    return img_path, category_path
    

@app.route("/sampling", methods=['POST'])
def sampling():
    # 分類するフォルダパスを取得
    category_path = os.path.join("static", os.path.join("labeled", request.form['category']))
    # ファイルの移動
    shutil.move(request.form['img_path'], category_path)

    cap = cv2.VideoCapture(0)
    FRAME_RATE=1
    ret, frame = cap.read()
    i=0
    while ret == True:
        ret, frame = cap.read()
        i+=1
        cv2.imwrite("static/sample/gazo"+str(int(time.time()-start_time))+ ".jpg",frame)
        #なんかKey押せば止まる
        if cv2.waitKey(1000*FRAME_RATE) >= 0:  
            break
        elif i>=1:
            break
        ret, frame = cap.read()
    cap.release()
    cv2.destroyAllWindows()
    return redirect("/")

if __name__ == "__main__":
    app.debug = True
    app.run()

