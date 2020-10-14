# 載入套件
from urllib.parse import urlparse
from http import client
from datetime import datetime

import requests
import time
import json
import os

class FreewayData():

    def __init__(self):
        self.__camera_data = None
        with open('freeway.json', 'r', encoding='utf-8') as read_file:
            self.__camera_data = json.load(read_file)
    
    def get_data(self):
        return self.__camera_data

    def get_info(self, url):

        camera_info = dict()

        for camera in self.__camera_data:
            source_url = camera['html']
            source = urlparse(source_url)
            target = urlparse(url)

            if source.netloc == target.netloc and source.path == target.path and source.params == target.params and source.query == target.query:
                camera_info = camera
                print('found')
                break

        return camera_info


class CCTVImageCrawler():

    def __init__(self):
        '''
        初始化
        '''
        # 設定HTTP版本
        client.HTTPConnection._http_vsn = 10
        client.HTTPConnection._http_vsn_str = 'HTTP/1.0'

        # 物件變數
        self.URL = '' # CCTV URL
        self.image_save_dir = 'cctv_images/' # 存檔位置
        self.__request_time = None
        self.__request = None # Request物件
        self.__cctv_images = None

    def __send_request(self):
        '''
        發送Request
        '''
        print('Request sent.')
        headers = {'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        self.__request_time = datetime.now() # 設定請求時間
        r = requests.get(self.URL, headers=headers) # 發送GET請求
        if r.status_code == requests.codes.ok: # 判斷Request Code狀態是否正常
            self.__request = r
            print('Request sent successfully.')

        print('Request received.')

    def set_image_save_dir(self, save_dir):
        '''
        設定存檔位置
        '''
        self.image_save_dir = save_dir

    def set_cctv_url(self, URL):
        '''
        設定目標網址
        '''
        self.URL = URL

    def get_request_time(self):
        return self.__request_time
    
    def get_cctv_images(self):
        '''
        取得CCTV影像物件陣列
        '''
        print('Start crawling cctv images.')
        # 清空上一次的物件資訊
        self.__request = None # 重設request物件
        self.__cctv_images = None

        self.__send_request() # 發送請求

        content_list = None

        if self.__request is not None:
            print('Start parsing request contents.')
            content = self.__request.content # 取得Request內容
            jfif_flag = b'\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46' # 圖片起始標記
            content_list = content.split(jfif_flag) # 分割
            content_list = content_list[1:] # 捨棄第一個無意義的物件

            new_content_list = list()
            for i, content in enumerate(content_list):
                content = jfif_flag + content # 補償JFIF開頭標記
                new_content_list.append(content)

            self.__cctv_images = new_content_list

            print('Contents parsing completed, got %d images.'%len(content_list))

        return content_list

    def save_cctv_images(self):
        '''
        存檔
        '''
        print('Checking saving directories exist or not.')
        # 檢查存檔根目錄是否存在
        if not os.path.exists(self.image_save_dir):
            os.mkdir(self.image_save_dir)

        datetime_string = self.__request_time.strftime('%Y%m%d_%H%M%S') # 格式時間字串

        # 檢查本次存檔的資料夾是否存在
        current_save_dir = os.path.join(self.image_save_dir, datetime_string)
        if not os.path.exists(current_save_dir):
            os.mkdir(current_save_dir)

        print('Start saving images.')
        for i, cctv_image in enumerate(self.__cctv_images):
            image_filepath = '%s/%s.jpg' % (current_save_dir, str(i)) # Set new image filename
            
            with open(image_filepath, 'wb') as f:
                f.write(cctv_image)

        print('Saving completed.')


    def get_first_image_dir(self):

        datetime_string = self.__request_time.strftime('%Y%m%d_%H%M%S') # 格式時間字串
        current_save_dir = os.path.join(self.image_save_dir, datetime_string)
        first_image_dir = '%s/0.jpg' % (current_save_dir) # Set new image filename

        return first_image_dir


# 測試程式
if __name__ == "__main__":

    url = 'https://cctvn01.freeway.gov.tw/vStream.php?pm=160,A40,13' # CCTV URL

    '''
    網址資料比對
    '''
    freewayData = FreewayData() # 建立一個freewayData物件
    camera_data = freewayData.get_data() # 取得監視器的Dict資訊


    camera_info = freewayData.get_info(url) # 檢查這個網址有沒有在檔案中
    print(camera_info)
    
    '''
    影像爬蟲
    '''
    cctvImageCrawler = CCTVImageCrawler() # 建立一個CCTVImageCrawler物件
    cctvImageCrawler.set_cctv_url(url) # 設定CCTV路徑
    cctv_images = cctvImageCrawler.get_cctv_images() # 取得CCTV影像 
    cctvImageCrawler.save_cctv_images() # 存檔

