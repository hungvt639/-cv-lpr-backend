
from rest_framework import generics, status, permissions, parsers
from rest_framework.response import Response
from ..utils.predict_plate import lp_recognition_image
import cv2
import numpy as np
from keras import backend as K


class CVView(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = (parsers.MultiPartParser, parsers.JSONParser, parsers.FileUploadParser,)

    def post(self, request, *args, **kwargs):
        
        try:   
            K.clear_session()    
            f = request.FILES["img"].read()
            nps = np.fromstring(f, np.uint8)
            img = cv2.imdecode(nps, cv2.IMREAD_UNCHANGED)
            predict_plate = lp_recognition_image(img)
            if(not predict_plate):
                return Response({"message":"Không tìm thấy biển số"}, status=status.HTTP_400_BAD_REQUEST)
            data = {"text":predict_plate}
            K.clear_session()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            raise e
            return Response({"message":"Đã sảy ra lỗi, bạn vui lòng nhập lại"}, status=status.HTTP_400_BAD_REQUEST)