# -*- coding: utf-8 -*-
""" A class for testing a SSD model on a video file or webcam """
import time
from base_camera import BaseCamera

import cv2
import keras
from keras.applications.imagenet_utils import preprocess_input
from keras.backend.tensorflow_backend import set_session
from keras.models import Model
from keras.preprocessing import image 
import pickle
import numpy as np
from random import shuffle
from scipy.misc import imread, imresize
from timeit import default_timer as timer

import sys
sys.path.append("..")
from ssd_utils import BBoxUtility
from ssd_v2 import SSD300v2 as SSD

def cv_fourcc(c1, c2, c3, c4):
        return (ord(c1) & 255) + ((ord(c2) & 255) << 8) + \
            ((ord(c3) & 255) << 16) + ((ord(c4) & 255) << 24)

class Camera(BaseCamera):
    video_source = 0

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source
    """
    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')
        vid_test = Camera
        while True:
            # read current frame
            #_, img = camera.read()
            img = vid_test.run(0)
            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
    """   
        
#class VideoTest(object):

    
    @staticmethod
    def frames():
        video_path = 0 
        start_frame = 0 
        conf_thresh = 0.6
        input_shape = (300,300,3)
        class_names = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
        NUM_CLASSES = len(class_names)
        num_classes=NUM_CLASSES
        class_colors = []
        for i in range(0, num_classes):
            hue = 255*i/num_classes
            col = np.zeros((1,1,3)).astype("uint8")
            col[0][0][0] = hue
            col[0][0][1] = 128 # Saturation
            col[0][0][2] = 255 # Value
            cvcol = cv2.cvtColor(col, cv2.COLOR_HSV2BGR)
            col = (int(cvcol[0][0][0]), int(cvcol[0][0][1]), int(cvcol[0][0][2]))
            class_colors.append(col) 
        bbox_util = BBoxUtility(num_classes)
        model = SSD(input_shape, num_classes=NUM_CLASSES)
        model.load_weights('weights_SSD300.hdf5') 

        INTERVAL= 33     # 待ち時間
        FRAME_RATE = 20  # fps
        ORG_WINDOW_NAME = "org"
        #GRAY_WINDOW_NAME = "gray"
        #OUT_FILE_NAME = "real_SSD_result.mp4"
        
        vid = cv2.VideoCapture(0)
        width, height = input_shape[0], input_shape[1]  #input_shape
        """
        out = cv2.VideoWriter(OUT_FILE_NAME, \
                      cv_fourcc('M', 'P', '4', 'V'), \
                      FRAME_RATE, \
                      (width, height), \
                      True)
        """
        if not vid.isOpened():
            raise IOError(("Couldn't open video file or webcam. If you're "
            "trying to open a webcam, make sure you video_path is an integer!"))
        
        vidw = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        vidh = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        vidar = vidw/vidh
        """
        if start_frame > 0:
            vid.set(cv2.CAP_PROP_POS_MSEC, start_frame)
        """    
        accum_time = 0
        curr_fps = 0
        fps = "FPS: ??"
        prev_time = timer()
        start_time=prev_time
        cv2.namedWindow(ORG_WINDOW_NAME)
        
        while True:
            retval, orig_image = vid.read()
            if not retval:
                print("Done!")
                return
                
            im_size = (input_shape[1], input_shape[0])  
            resized = cv2.resize(orig_image, im_size)
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
           
            to_draw = cv2.resize(resized, (int(input_shape[1]*vidar), input_shape[0]))
            
            inputs = [image.img_to_array(rgb)]  #rgb
            tmp_inp = np.array(inputs)
            x = preprocess_input(tmp_inp)
            y = model.predict(x)
            
            results = bbox_util.detection_out(y)
            
            if len(results) > 0 and len(results[0]) > 0:
                det_label = results[0][:, 0]
                det_conf = results[0][:, 1]
                det_xmin = results[0][:, 2]
                det_ymin = results[0][:, 3]
                det_xmax = results[0][:, 4]
                det_ymax = results[0][:, 5]

                top_indices = [i for i, conf in enumerate(det_conf) if conf >= conf_thresh]

                top_conf = det_conf[top_indices]
                top_label_indices = det_label[top_indices].tolist()
                top_xmin = det_xmin[top_indices]
                top_ymin = det_ymin[top_indices]
                top_xmax = det_xmax[top_indices]
                top_ymax = det_ymax[top_indices]

                for i in range(top_conf.shape[0]):
                    xmin = int(round(top_xmin[i] * to_draw.shape[1]))
                    ymin = int(round(top_ymin[i] * to_draw.shape[0]))
                    xmax = int(round(top_xmax[i] * to_draw.shape[1]))
                    ymax = int(round(top_ymax[i] * to_draw.shape[0]))

                    class_num = int(top_label_indices[i])
                    cv2.rectangle(to_draw, (xmin, ymin), (xmax, ymax), 
                              class_colors[class_num], 2)   #to_draw
                    text = class_names[class_num] + " " + ('%.2f' % top_conf[i])

                    text_top = (xmin, ymin-10)
                    text_bot = (xmin + 80, ymin + 5)
                    text_pos = (xmin + 5, ymin)
                    cv2.rectangle(to_draw, text_top, text_bot, class_colors[class_num], -1)  #to_draw
                    cv2.putText(to_draw, text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0,0,0), 1)  #to_draw
                    print(text," ")
            curr_time = timer()
            exec_time = curr_time - prev_time
            prev_time = curr_time
            accum_time = accum_time + exec_time
            curr_fps = curr_fps + 1
            if accum_time > 1:
                accum_time = accum_time - 1
                fps = "FPS: " + str(curr_fps)
                curr_fps = 0
            
            cv2.rectangle(to_draw, (0,0), (50, 17), (255,255,255), -1)  #to_draw
            cv2.putText(to_draw, fps, (3,10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0,0,0), 1) #to_draw
        
            to_draw = cv2.resize(to_draw, (int(input_shape[0]*1), input_shape[1]))
            #cv2.imshow(ORG_WINDOW_NAME, to_draw)  #to_draw
            #out.write(to_draw)  #add to_draw
            
            if cv2.waitKey(INTERVAL)>= 0:   # & 0xFF == ord('q'):
                break
            elif curr_time-start_time>=60:
                break
            yield cv2.imencode('.jpg', to_draw)[1].tobytes()
        vid.release()   #add
        #out.release()   #add
        cv2.destroyAllWindows() #add
        
        