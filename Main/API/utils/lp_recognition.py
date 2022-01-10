"""
Nhận dạng biển số xe

Nhận dạng ký tự của biển số xe bằng model CNN đã training
và hình ảnh biển xe sau khi tiền xử lý
"""

import numpy as np
import cv2

"""
Hàm chỉnh sửa kích thước ảnh

* Từ ảnh ký tự đầu vào thành hình ảnh 3-channel (3-kênh)
"""
def fix_dimension(img):
    new_img = np.zeros((28, 28, 3))
    for i in range(3):
        new_img[:, :, i] = img
        return new_img


"""
Hàm nhận dạng ký tự
"""
def lp_recognize(model, char_list):
    # tạo label cho kết quả
    dic = {}
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for idx, character in enumerate(characters):
        dic[idx] = character
    # output kết quả
    output = []
    # duyệt các ký tự
    for idx, char_img in enumerate(char_list):
        char_img = cv2.resize(char_img, (28, 28), interpolation=cv2.INTER_AREA)
        img = fix_dimension(char_img)
        # chuẩn bị ảnh cho model
        img = img.reshape(1, 28, 28, 3)
        # dự đoán
        label = model.predict_classes(img)[0]
        char = dic[label]
        output.append(char)
    # nối lại thành chuỗi
    plate_number = ''.join(output)

    return plate_number
