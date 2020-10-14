# 國道車輛偵測
擷取國道公開的CCTV監視器畫面，進行車輛資訊分析彙整。

***

## 環境需求
* Python = `3.6`

## 下載模型權重檔
1. 下載Yolo v3預訓練好的模型權重檔，[Yolo v3權重檔下載](https://pjreddie.com/media/files/yolov3.weights)。
2. 將`yolov3.weights`放到`model/`資料夾底下。

## 相依套件安裝
```
pip3 install -r requirements.txt
```

## 程式執行
```
python3 main.py
```

## 監視器參數設定
請參考`freeway.json`內的`id`更改。

## 分析結果
### 監視器畫面
存於`cctv_images/`資料夾底下，資料夾名稱為`YYYYmmDD-HHMMSS`。
### 輸出檔案
存於`predict_result/`資料夾底下，資料夾名稱為`YYYYmmDD-HHMMSS`，內容包含：

  * `camera_data.csv`：監視器資訊與車輛總資訊。
  * `car_detail.csv`：每台車輛的資訊。
  * `input_image.jpg`：原始圖像。
  * `output_image.jpg`：預測結果圖像（包含標記框）。
  * `[num]_[color].jpg`：每台車輛的剪取圖像（數個）。

## 參考
* [pjreddie/yolo](https://pjreddie.com/darknet/yolo)
* [qqwweee/keras-yolo3](https://github.com/qqwweee/keras-yolo3)
* [guptavasu1213/Yolo-Vehicle-Counter](https://github.com/guptavasu1213/Yolo-Vehicle-Counter)

