
from rest_framework import generics, status, permissions, parsers
from rest_framework.response import Response
from ..utils.predict_plate import lp_recognition_image
# from ..utils.lp_detection import lp_detect_using_contour
# from ..utils.character_segmentation import segment_characters
# from ..utils.lp_recognition import lp_recognize

import cv2
import numpy as np
from keras.models import load_model
from django.conf import settings
import os
# def lp_recognition_image(request):
#     # đọc từ request sẽ như thế này
#     f = request.FILES["img"].read()
#     nps = np.fromstring(f, np.uint8)

#     img = cv2.imdecode(nps, cv2.IMREAD_UNCHANGED)
#     # truyền vào thì sẽ thế này
#     # img = cv2.imdecode(np.fromstring(image, np.uint8), cv2.IMREAD_UNCHANGED)

#     # đọc model CNN
#     # file_path = os.path.join(settings.MEDIA_ROOT, 'weights', "dkt_model.h5")
#     # file_path = os.path.join("weights", "dkt_model.h5")
#     # file_path = "weights/dkt_model.h5"
#     # file = open(file_path)
#     file_path = "dkt_model.h5"
#     loaded_model = load_model(file_path)
#     predict_plate = ""
#     img_plate = lp_detect_using_contour(image=img)
#     if img_plate is not None:
#         char_list = segment_characters(image=img_plate)
#         if len(char_list) == 0:
#             return predict_plate
#         predict_plate = lp_recognize(model=loaded_model, char_list=char_list)

#     return predict_plate



class CVView(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.JSONParser, parsers.FileUploadParser,)

    def post(self, request, *args, **kwargs):
        try:       
            f = request.FILES["img"].read()
            nps = np.fromstring(f, np.uint8)
            img = cv2.imdecode(nps, cv2.IMREAD_UNCHANGED)
            predict_plate = lp_recognition_image(img)
            if(not predict_plate):
                return Response({"message":"Không tìm thấy biển số"}, status=status.HTTP_400_BAD_REQUEST)
            data = {"text":predict_plate}
            return Response(data, status=status.HTTP_200_OK)
        except:
            return Response({"message":"Đã sảy ra lỗi, bạn vui lòng nhập lại"}, status=status.HTTP_400_BAD_REQUEST)