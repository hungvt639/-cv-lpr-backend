from .lp_detection import lp_detect_using_contour, lp_detect_using_yolo
from .character_segmentation import segment_characters
from .lp_recognition import lp_recognize
import cv2
from keras.models import load_model
from django.conf import settings
import os


def lp_recognition_image(img):
    predict_plate = ""
    confThreshold = 0.5
    nmsThreshold = 0.4
    inputWidth = 416
    inputHeight = 416
    modelConfiguration = os.path.join(settings.MEDIA_ROOT, 'yolo_utils', "darknet-yolov3.cfg")
    modelWeights = os.path.join(settings.MEDIA_ROOT, 'yolo_utils', "lapi.weights")
    net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    file_path = os.path.join(settings.MEDIA_ROOT, 'weights', "dkt_model.h5")
    loaded_model = load_model(file_path)
    img_plate = lp_detect_using_yolo(net=net, frame=img, confThreshold=confThreshold, nmsThreshold=nmsThreshold, inputWidth=inputWidth, inputHeight=inputHeight)
    if img_plate is None:
        img_plate = lp_detect_using_contour(image=img)
        if img_plate is None:
            return predict_plate
    char_list = segment_characters(image=img_plate)
    if len(char_list) == 0:
        return predict_plate
    predict_plate = lp_recognize(model=loaded_model, char_list=char_list)
    return predict_plate