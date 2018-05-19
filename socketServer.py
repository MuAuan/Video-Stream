# -*- coding:utf-8 -*-
#!/usr/bin/python

import SocketServer  
import cv2
import numpy  
import socket  
import sys  
  
class TCPHandler(SocketServer.BaseRequestHandler):  
    capture=''  
    #リクエストを受け取るたびに呼ばれる関数
    def handle(self):  
        #HELLOを受け取ったらJPEG圧縮したカメラ画像を文字列にして送信
        self.data = self.request.recv(1024).strip()
        ret, frame=capture.read()
        jpegstring=cv2.cv.EncodeImage('.jpeg',cv2.cv.fromarray(frame)).tostring()  
        self.request.send(jpegstring)  
  
  
#環境に応じて変更
HOST = '192.168.0.15'
PORT = 8080  

#カメラの設定
capture=cv2.VideoCapture(0)
capture.set(3,640)   #width=640
capture.set(4,480)   #height=480
if not capture:  
    print "Could not open camera"  
    sys.exit()

SocketServer.TCPServer.allow_reuse_address = True
server = SocketServer.TCPServer((HOST, PORT), TCPHandler)  
server.capture=capture  
#^Cを押したときにソケットを閉じる
try:
    server.serve_forever()  
except KeyboardInterrupt:
    pass
server.shutdown()
sys.exit()
