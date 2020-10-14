from Model import YoloModel
from Crawler import CCTVImageCrawler, FreewayData
import cv2
import numpy as np
import csv
import os

def save_predict_result(prediction_save_dir, request_time, result_boxes, vehicle_count):

    # prediction_save_dir = 'predict_result/' + predict_time
    

    with open(prediction_save_dir + 'car_detail.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(['vehicle_type', 'color', 'x_min', 'y_min', 'x_max', 'y_max', 'score'])

        for result_box in result_boxes:
            writer.writerow(result_box)

    with open(prediction_save_dir + 'camera_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        camera_location = camera_info['stakenumber']
        time = request_time
        longitude = camera_info['gisx']
        latitude = camera_info['gisy']
        vehicle_num = 0
        for vehicle in vehicle_count:
            vehicle_num += vehicle_count[vehicle]

        writer.writerow(['camera_location', 'time', 'longitude', 'latitude', 'count'])
        writer.writerow([camera_location, time, longitude, latitude, vehicle_num])

if __name__ == "__main__":

    url = 'http://cctvn01.freeway.gov.tw/vStream.php?pm=160,A40,13'

    '''
    取得監視器資訊總表
    '''
    freewayData = FreewayData() # 建立一個FreewayData物件
    camera_data = freewayData.get_data() # 取得監視器的Dict資訊

    camera_info = freewayData.get_info(url) # 檢查這個網址有沒有在檔案中

    '''
    取得監視器畫面影像
    '''
    cctvImageCrawler = CCTVImageCrawler() # 建立一個CCTVImageCrawler物件
    cctvImageCrawler.set_cctv_url(url) # 設定CCTV路徑
    cctv_images = cctvImageCrawler.get_cctv_images()
    cctvImageCrawler.save_cctv_images() # 存檔
    request_time = cctvImageCrawler.get_request_time().strftime('%Y%m%d_%H%M%S')
    first_image_dir = cctvImageCrawler.get_first_image_dir()


    '''
    辨識畫面
    '''
    image = cv2.imread(first_image_dir) # 讀取圖片

    model = YoloModel() # 建立一個Yolo模型物件
    model.recognize(image) # 辨識圖片
    recognized_image = model.get_result_image() # 取得辨識完圖片(含標記框)

    result_boxes = model.get_bounded_boxes() # 取得詳細結果陣列
    vehicle_count = model.get_vehicle_count() # 取得車輛種類計數資料

    
    prediction_save_dir = os.path.join('predict_result/', request_time + '/')
    if not os.path.exists(prediction_save_dir):
        os.makedirs(prediction_save_dir)
    
    save_predict_result(prediction_save_dir, request_time, result_boxes, vehicle_count)

    cv2.imwrite(prediction_save_dir + 'input_image.jpg', image)
    cv2.imwrite(prediction_save_dir + 'output_image.jpg', recognized_image)
    
    for i, box in enumerate(result_boxes):
        
        x_min = box[2]
        y_min = box[3]
        x_max = box[4]
        y_max = box[5]
        box_image = image[y_min:y_max, x_min:x_max]

        box_image_filename = '%s_%s.jpg'%(str(i), box[1])
        cv2.imwrite(prediction_save_dir + box_image_filename, box_image)


    

    