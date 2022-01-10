"""
Phát hiện biển số sử dụng phương pháp tìm đường viền

Phát hiện biển số xe từ hình ảnh đầu vào.
Từ đó đưa sang bộ phân đoạn ký tự
"""

import numpy as np
import math
import imutils
import cv2

"""
Hàm tính khoảng cách giữa 2 điểm (x1, y1) và (x2, y2)
"""
def calculate_distance(x1, x2, y1, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

"""
Hàm phát hiện vùng chứa biển số sử dụng phương pháp Contour

* Từ hình ảnh đầu vào, tiền xử lý và sau đó phát hiện viền chứa biển số:
- Thay đổi kích thước ảnh: thay đổi width của ảnh sang 500px, để dễ dàng xử lý.
- Chuyển ảnh sang ảnh xám: đầu vào ảnh là RGB, chuyển sang ảnh xám để giảm số lượng màu sắc.
- Lọc nhiễu: nhiễu hình ảnh là sự biến dạng hình ảnh phát sinh do lỗi trong máy ảnh hoặc do khả năng hiển thị 
kém do điều kiện thời tiết thay đổi. Nhiễu cũng là sự thay đổi ngẫu nhiên trong mức cường độ của các pixel. Nhiễu 
có thể thuộc nhiều loại khác nhau như nhiễu Gaussian, nhiễu muối và nhiễu hạt tiêu. Ở đây sử dụng bộ lọc song phương 
lặp đi lặp lại để loại bỏ nhiễu. Nó cung cấp cơ chế giảm nhiễu đồng thời bảo vệ các cạnh hiệu quả hơn bộ lọc trung vị.
- Nhị phân hóa: chuyển ảnh sang ảnh nhị phân (chỉ chứa giá trị pixel trắng và đen). Thực hiện quá trình mã hóa nhị phân 
trước khi nhận dạng và trích xuất biển số xe từ hình ảnh sẽ giúp việc nhận dạng biển số xe dễ dàng hơn vì các cạnh sẽ rõ
ràng hơn trong ảnh nhị phân.
- Sau các bước tiền xử lý ảnh, tìm đường bao bằng cv2.findContours:
    + loại bỏ hết các đường bao có diện tích nhỏ hơn 30
    + một đường bao có dạng hình tứ giác (có 4 cạnh) thì sẽ coi là biển số

* Sau khi phát hiện biển số, xoay ảnh biển số nếu bị nghiêng

"""
def lp_detect_using_contour(image):
    # resize chiều rộng của ảnh về 500px
    image = imutils.resize(image, width=500)
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # chuyển sang ảnh xám
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # lọc nhiễu với bộ lọc song phương lặp đi lặp lại (loại bỏ nhiễu trong khi giữ nguyên các cạnh)
    image_gray = cv2.bilateralFilter(image_gray, 11, 17, 17)
    # tìm các cạnh của ảnh xám
    edged = cv2.Canny(image_gray, 170, 200)
    # tìm đường viền dựa trên các cạnh
    contours = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
    # sắp xếp các đường viền dựa trên diện tích, giữ diện tích bắt buộc tối thiểu là '30' (<30 sẽ bị loại)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
    # đường bao biển số
    number_plate_contour = None
    # lặp các đường bao để tìm ra đường bao có khả năng là biển số nhất
    for contour in contours:
        # tính toán độ dài đường cong hoặc chu vi đường bao khép kín
        peri = cv2.arcLength(contour, True)
        # trực quan hóa đường bao thành hình
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        # chọn đường bao có 4 góc là biển số
        if len(approx) == 4:
            number_plate_contour = approx
            # trả về giá trị của hình chữ nhật bao quanh vùng biển số
            x, y, w, h = cv2.boundingRect(contour)
            # vùng chứa biển số
            ROI = img[y:y+h, x:x+w]
            break
    
    img_result = None
    # nếu phát hiện được biển, xoay nếu bị nghiêng
    if number_plate_contour is not None:
        idx = 0
        m = 0
        # tìm chỉ số của tọa độ với tọa độ y tối đa
        for i in range(4):
            if number_plate_contour[i][0][1] > m:
                idx = i
                m = number_plate_contour[i][0][1]
        # gán chỉ mục cho tọa độ trước đó
        if idx == 0:
            pin = 3
        else:
            pin = idx-1
        # gán chỉ mục cho tọa độ tiếp theo
        if idx == 3:
            nin = 0
        else:
            nin = idx+1
        # tìm khoảng cách giữa tọa độ thu được và tọa độ trước đó và tiếp theo của nó
        p = calculate_distance(number_plate_contour[idx][0][0], number_plate_contour[pin][0][0], number_plate_contour[idx][0][1], number_plate_contour[pin][0][1])
        n = calculate_distance(number_plate_contour[idx][0][0], number_plate_contour[nin][0][0], number_plate_contour[idx][0][1], number_plate_contour[nin][0][1])
        # Tọa độ có nhiều khoảng cách hơn so với tọa độ thu được là tọa độ dưới cùng thứ hai được yêu cầu
        if p > n:
            if number_plate_contour[pin][0][0] < number_plate_contour[idx][0][0]:
                left = pin
                right = idx
            else:
                left = idx
                right = pin
        else:
            if number_plate_contour[nin][0][0] < number_plate_contour[idx][0][0]:
                left = nin
                right = idx
            else:
                left = idx
                right = nin
        left_x = number_plate_contour[left][0][0]
        left_y = number_plate_contour[left][0][1]
        right_x = number_plate_contour[right][0][0]
        right_y = number_plate_contour[right][0][1]
        # tìm góc quay bằng cách tính sin của theta
        opp = right_y-left_y
        hyp = ((left_x-right_x)**2+(left_y-right_y)**2)**0.5
        sin = opp/hyp
        theta = math.asin(sin)*57.2958
        # xoay hình ảnh theo góc quay thu được
        image_center = tuple(np.array(ROI.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, theta, 1.0)
        img_result = cv2.warpAffine(ROI, rot_mat, ROI.shape[1::-1], flags=cv2.INTER_LINEAR)
        # hình ảnh có thể được cắt sau khi xoay (vì hình ảnh được xoay có chiều cao hơn nhiều)
        if opp > 0:
            h = img_result.shape[0]-opp//2
        else:
            h = img_result.shape[0]+opp//2
        # ảnh biển số sau khi được xoay
        img_result = img_result[0:h, :]
    
    return img_result

"""
Hàm phát hiện vùng chứa biển số sử dụng YOLO
"""
def lp_detect_using_yolo(net, frame, confThreshold=0.5, nmsThreshold=0.4, inputWidth=416, inputHeight=416):
     # tạo một 4D blob từ một frame
    blob = cv2.dnn.blobFromImage(frame, 1/255, (inputWidth, inputHeight), [0,0,0], 1, crop=False)
    # đặt đầu vào cho mạng
    net.setInput(blob)

    # lấy các lớp đầU ra của mạng
    # lấy tên của tất cả các lớp đầu ra
    layersNames = net.getLayerNames()
    # lấy tên của các lớp đầu ra, tức là các lớp có đầu ra không được kết nối
    temp = [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    # chạy chuyển tiếp để nhận đầu ra của các lớp đầu ra
    outs = net.forward(temp)

    # loại bỏ các hộp giới hạn có độ tin cậy thấp bằng cách sử dụng phương pháp triệt tiêu không cực đại
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
    # quét qua tất cả các ô giới hạn đầu ra từ mạng và chỉ giữ lại những ô có điểm tin cậy cao. Gán nhãn lớp của hộp là lớp có điểm cao nhất
    classIds = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])
    # thực hiện ngăn chặn không tối đa để loại bỏ các hộp chồng chéo dư thừa với tâm sự thấp hơn
    cropped = None
    indices = cv2.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        # tính phần thừa bên dưới và bên phải
        bottom = top + height
        right = left + width
        # cắt bớt phần thừa
        cropped = frame[top:bottom, left:right].copy()
    
    return cropped
