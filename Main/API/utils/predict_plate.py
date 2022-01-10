"""
Phát hiện biển số xe từ một ảnh đầu vào
"""
from .lp_detection import lp_detect_using_contour, lp_detect_using_yolo
from .character_segmentation import segment_characters
from .lp_recognition import lp_recognize

import cv2
import numpy as np
from keras.models import load_model
from django.conf import settings
import os

"""
Hàm nhận đầu vào là ảnh upload từ server

cần convert sang cv2
"""




def lp_recognition_image(img):
    # đọc từ request sẽ như thế này
    
    # truyền vào thì sẽ thế này
    # img = cv2.imdecode(np.fromstring(image, np.uint8), cv2.IMREAD_UNCHANGED)
    confThreshold = 0.5 # ngưỡng tin cậy
    nmsThreshold = 0.4  # Ngưỡng ngăn chặn không tối đa

    inputWidth = 416 # width của ảnh đầu vào mạng YOLO
    inputHeight = 416 # height của ảnh đầu vào mạng YOLO

    # tải các tên của classes và nối thành một list
    # classesFile = os.path.join(settings.MEDIA_ROOT, 'yolo_utils', "classes.names")
    # classes = None
    # with open(classesFile, 'rt') as f:
    #     classes = f.read().rstrip('\n').split('\n')

    # cung cấp các tệp cấu hình của mạng YOLO
    modelConfiguration = os.path.join(settings.MEDIA_ROOT, 'yolo_utils', "darknet-yolov3.cfg")
    modelWeights = os.path.join(settings.MEDIA_ROOT, 'yolo_utils', "lapi.weights")
    net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    # đọc model CNN
    file_path = os.path.join(settings.MEDIA_ROOT, 'weights', "dkt_model.h5")
    loaded_model = load_model(file_path)
    # biến kết quả
    predict_plate = ""

   # phát hiện vùng chứa biển số
    img_plate = lp_detect_using_yolo(net=net, frame=img, confThreshold=confThreshold, nmsThreshold=nmsThreshold, inputWidth=inputWidth, inputHeight=inputHeight)

    # nếu không tìm được biển
    if img_plate is None:
        # phát hiện vùng chứa biển số
        img_plate = lp_detect_using_contour(image=img)
        # nếu không tìm được biển
        if img_plate is None:
            return predict_plate
    
    # nếu tìm đc biển
    # phân đoạn ký tự
    char_list = segment_characters(image=img_plate)

    # nếu không phân tách được ký tự
    if len(char_list) == 0:
        return predict_plate

    # nhận dạng ký tự
    predict_plate = lp_recognize(model=loaded_model, char_list=char_list)


    return predict_plate