"""
Phân đoạn ký tự

Phân tách hình ảnh biển số đã phát hiện được thành hình ảnh các ký tự riêng lẻ.
Từ đó đưa các ký tự vào bộ nhận dạng.
"""

import numpy as np
import cv2

"""
Hàm tách các ký tự từ ảnh biển số

* Từ ảnh đầu vào, thao tác ảnh để đưa về ảnh nhị phân (giúp nhận dạng ký tự dễ hơn vì các cạnh sẽ 
rõ ràng hơn trong ảnh nhị phân):
- Thay đổi kích thước ảnh về 333x75 (4.4:1) để các ký tự trong ảnh khác biệt và rõ ràng hơn.
- Chuyển ảnh về ảnh xám GRAY
- Chuyển về ảnh nhị phân bằng hàm ngưỡng cv2.threshold với ngưỡng là 200. Mỗi pixel trong ảnh:
    + có giá trị mới là 0 nếu giá trị < 200
    + có giá trị mới là 1 nếu giá trị > 200
- Ảnh sau nhị phân được cho qua quá trình erode (xói mòn). Eroding là một quá trình đơn giản 
được sử dụng để loại bỏ các pixel không mong muốn khỏi ranh giới của đối tượng nghĩa là các 
pixel đáng lẽ phải có giá trị 0 nhưng có giá trị là 1. 
- Sau đó, hình ảnh đã sạch và không có nhiễu ranh giới. Tiếp theo cần dùng dilate (giãn hình ảnh), tức là
lấp đầy các pixel vắng mặt nghĩa là các pixel đáng lẽ phải có giá trị 1 nhưng có giá trị 0. 
- Bước tiếp theo bây giờ là làm cho các ranh giới của hình ảnh có màu trắng. Điều này là để loại bỏ
bất kỳ pixel nào ra khỏi khung hình trong trường hợp nó có mặt.
- Xác định khoảng giá trị có thể nhận của các ký tự để so sánh khi lọc ký tự.

-> từ ảnh vào, thông qua các quá trình, tạo ra ảnh nhị phân sạch và chuyển sang find_characters() để tìm
ra các ký tự.

* Tìm các ký tự từ hình ảnh đã qua xử lý
- Tìm tất cả các đường viền trong ảnh đã qua xử lý bằng cv2.findContours, trả về tất cả các đường
bao mà nó tìm thấy trong ảnh.
- Từ các đường bao đã tìm, tính kích thước hình chữ nhật của đường bao tương ứng. Coi hình chữ nhật
bao quanh là hình chữ nhật nhỏ nhất có thể chứa đường viền. Tiếp theo là thực hiện một số điều chỉnh 
tham số và lọc ra hình chữ nhật cần thiết có chứa các ký tự bắt buộc bằng một số so sánh kích thước để
chỉ chấp nhận những hình chữ nhật có: 
    + chiều rộng hình chữ nhật trong khoảng 0 -> (length của ảnh)/số ký tự
    + chiều dài hình chữ nhật trong khoảng (width của ảnh)/2 -> (width của ảnh)*4/5

-> kết quả là danh sách cách ký tự tìm được
"""
def segment_characters(image):
    # Tiền xử lý ảnh biển số đã cắt
    # resize hình ảnh về kích thước [333,75]
    img_lp = cv2.resize(image, (333, 75))
    # chuyển ảnh sang ảnh xám
    img_gray_lp = cv2.cvtColor(img_lp, cv2.COLOR_BGR2GRAY)
    # chuyển về ảnh nhị phân bằng cách dùng ngưỡng (200)
    _, img_binary_lp = cv2.threshold(img_gray_lp, 200, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # lọc nhiễu ranh giới bằng loại bỏ các pixel không mong muốn bằng erode (xói mòn)
    img_binary_lp = cv2.erode(img_binary_lp, (3, 3))
    # giãn hình ảnh bằng dilate
    img_binary_lp = cv2.dilate(img_binary_lp, (3, 3))
    # tạo boder của hình ảnh có màu trắng
    img_binary_lp[0:3, :] = 255
    img_binary_lp[:, 0:3] = 255
    img_binary_lp[72:75, :] = 255
    img_binary_lp[:, 330:333] = 255
    # ước tính kích thước của các ký tự từ ảnh ảnh biển số đã cắt
    LP_WIDTH = img_binary_lp.shape[0]
    LP_HEIGHT = img_binary_lp.shape[1]
    dimensions = [LP_WIDTH/6, LP_WIDTH/2, LP_HEIGHT/10, 2*LP_HEIGHT/3]

    # Xác định các ký tự từ ảnh biển số đã cắt
    # tìm tất cả các viền có trong ảnh
    contours, _ = cv2.findContours(img_binary_lp.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # lấy ra các kích thước có thể của ký tự
    lower_width = dimensions[0]
    upper_width = dimensions[1]
    lower_height = dimensions[2]
    upper_height = dimensions[3]
    # kiểm tra 5 tới 15 đường viền lớn nhất (có khả năng là ký tự)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]
    x_contour_list = []  # mảng lưu tọa độ 1 đỉnh của đường bao là ký tự
    char_list = []  # mảng lưu các ký tự
    # duyệt các đường viền
    for contour in contours:
        # phát hiện đường bao trong hình ảnh nhị phân và trả về tọa độ của hình chữ nhật bao quanh nó
        intX, intY, intWidth, intHeight = cv2.boundingRect(contour)
        # kiểm tra kích thước của đường viền để lọc ra các ký tự
        if intWidth > lower_width and intWidth < upper_width and intHeight > lower_height and intHeight < upper_height:
            # lưu trữ tọa độ x của đường viền của ký tự, để sử dụng sau này để lập chỉ mục các đường bao
            x_contour_list.append(intX)
            # tạo biến để lưu giá trị ký tự
            char_copy = np.zeros((44, 24))
            # trích xuất từng ký tự bằng cách sử dụng tọa độ của hình chữ nhật bao quanh
            char = img_binary_lp[intY:intY+intHeight, intX:intX+intWidth]
            char = cv2.resize(char, (20, 40))
            # định dạng ảnh ký tự để đưa vào phân loại: đảo ngược màu sắc
            char = cv2.subtract(255, char)
            # chỉnh kích thước ảnh ký tự sang 24x44 với border màu đen
            char_copy[2:42, 2:22] = char
            char_copy[0:2, :] = 0
            char_copy[:, 0:2] = 0
            char_copy[42:44, :] = 0
            char_copy[:, 22:24] = 0
            # lưu lại ảnh nhị phân của các ký tự vào đầu ra (chưa được sắp xếp)
            char_list.append(char_copy)

    # sắp xếp lại kết quả trả về các ký tự theo thứ tự tăng dần đối với tọa độ x (ký tự ngoài cùng bên trái trước)
    # arbitrary function that stores sorted list of character indeces
    indices = sorted(range(len(x_contour_list)), key=lambda k: x_contour_list[k])
    char_list_copy = []
    for idx in indices:
        char_list_copy.append(char_list[idx])
    char_list = np.array(char_list_copy)

    return char_list
