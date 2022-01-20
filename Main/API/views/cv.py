
from rest_framework import generics, status, permissions, parsers
from rest_framework.response import Response
from ..utils.predict_plate import lp_recognition_image
import cv2
import numpy as np
from keras import backend as K
from django.conf import settings
import time

class CVView(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.JSONParser, parsers.FileUploadParser,)
    def post(self, request, *args, **kwargs):
        print("val", settings.VAL)
        while settings.VAL:
            time.sleep(5)
        settings.VAL = 1
        K.clear_session()
        try:   
            f = request.FILES["img"].read()
            nps = np.fromstring(f, np.uint8)
            img = cv2.imdecode(nps, cv2.IMREAD_UNCHANGED)
            predict_plate = lp_recognition_image(img)
            if(not predict_plate):
                return Response({"message":"Không tìm thấy biển số"}, status=status.HTTP_400_BAD_REQUEST)
            data = {"text":predict_plate}
            K.clear_session()
            settings.VAL = 0
            return Response(data, status=status.HTTP_200_OK)
        except:
            settings.VAL = 0
            K.clear_session()
            return Response({"message":"Đã sảy ra lỗi, bạn vui lòng nhập lại"}, status=status.HTTP_400_BAD_REQUEST)