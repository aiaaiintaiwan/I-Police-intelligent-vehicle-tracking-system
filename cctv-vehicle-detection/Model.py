# 載入套件
from config import Config
import recognize_color
import numpy as np
import cv2
import csv

class YoloModel():
    def __init__(self):
        
        '''
        物件初始化
        '''
        # 初始化變數
        self.image = None # 影像numpy陣列
        self.boxes = []
        self.confidences = []
        self.classIDs = []
        self.idxs = None

        # 載入模型參數
        self.config_path = Config.config_path
        self.weight_path = Config.weight_path
        self.label_path = Config.label_path
        self.input_size = Config.input_size
        self.confidence_score = Config.confidence_score
        self.pre_defined_threshold = Config.pre_defined_threshold

        # 視覺化結果參數
        self.labels = open(self.label_path).read().strip().split('\n') 
        np.random.seed(42)
        self.colors = np.random.randint(0, 255, size=(len(self.labels), 3), dtype='uint8')

        # 初始化模型
        self.net = cv2.dnn.readNetFromDarknet(self.config_path, self.weight_path) # 載入模型
        # 使用GPU
        if Config.use_gpu:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        print('Model initialization completed.')

    def recognize(self, image):

        '''
        進行圖像辨識
        '''
        
        # 檢查圖片是否為空
        if image is not None:

            self.image = image
            
            image_height, image_width, channel = self.image.shape # 取得圖片長寬
            blob = cv2.dnn.blobFromImage(self.image, 1 / 255.0, self.input_size, swapRB=True, crop=False) # 圖片前處理(轉換成模型輸入格式)
            self.net.setInput(blob) # 設定輸入層資料
            ln = self.net.getLayerNames()
            ln = [ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
            layerOutputs = self.net.forward(ln) # 前向傳遞

            # loop over each of the layer outputs
            for output in layerOutputs:
                # loop over each of the detections
                for i, detection in enumerate(output):
                    
                    scores = detection[5:]
                    classID = np.argmax(scores) # 取得分數最高的類別index
                    confidence = scores[classID] # 取得這個預測框的準確度

                    # filter out weak predictions by ensuring the detected
                    # probability is greater than the minimum probability
                    if confidence > self.confidence_score:
                        # scale the bounding box coordinates back relative to
                        # the size of the image, keeping in mind that YOLO
                        # actually returns the center (x, y)-coordinates of
                        # the bounding box followed by the boxes' width and
                        # height
                        box = detection[0:4] * np.array([image_width, image_height, image_width, image_height])
                        (centerX, centerY, width, height) = box.astype('int')

                        # use the center (x, y)-coordinates to derive the top
                        # and and left corner of the bounding box
                        x = int(centerX - (width / 2))
                        y = int(centerY - (height / 2))
                                    
                        #Printing the info of the detection
                        # print('\nName:\t', self.labels[classID],
                        #     '\t|\tBOX:\t', x, y)

                        # update our list of bounding box coordinates,
                        # confidences, and class IDs
                        self.boxes.append([x, y, int(width), int(height)])
                        self.confidences.append(float(confidence))
                        self.classIDs.append(classID)


            # apply non-maxima suppression to suppress weak, overlapping
            # bounding boxes
            self.idxs = cv2.dnn.NMSBoxes(self.boxes, self.confidences, self.confidence_score,
                self.pre_defined_threshold)

    def get_bounded_boxes(self):
        
        result_boxes = list()

        for i in range(len(self.boxes)):
            x_min = self.boxes[i][0]
            y_min = self.boxes[i][1]
            x_max = x_min + self.boxes[i][2]
            y_max = y_min + self.boxes[i][3]

            car_image = self.image[y_min:y_max, x_min:x_max]
            car_color = recognize_color.get_color(car_image)

            result_boxes.append([self.labels[self.classIDs[i]], car_color, x_min, y_min, x_max, y_max, self.confidences[i]])
        
        return result_boxes

    def get_result_image(self):

        recognized_image = self.image.copy()

        if len(self.idxs) > 0:
            # loop over the indices we are keeping
            for i in self.idxs.flatten():
                # extract the bounding box coordinates
                (x, y) = (self.boxes[i][0], self.boxes[i][1])
                (w, h) = (self.boxes[i][2], self.boxes[i][3])

                # draw a bounding box rectangle and label on the frame
                color = [int(c) for c in self.colors[self.classIDs[i]]]
                cv2.rectangle(recognized_image, (x, y), (x + w, y + h), color, 2)
                text = '{}: {:.4f}'.format(self.labels[self.classIDs[i]], self.confidences[i])
                cv2.putText(recognized_image, text, (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                #Draw a green dot in the middle of the box
                cv2.circle(recognized_image, (x + (w//2), y+ (h//2)), 2, (0, 0xFF, 0), thickness=2)

        return recognized_image

    def get_vehicle_count(self):

        vehicle_count = dict()

        for class_id in self.classIDs:

            if self.labels[class_id] not in vehicle_count:
                vehicle_count[self.labels[class_id]] = 1
            else:
                vehicle_count[self.labels[class_id]] = vehicle_count[self.labels[class_id]] + 1
        
        return vehicle_count



