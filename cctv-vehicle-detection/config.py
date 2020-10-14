class Config():
    # 網路設定
    config_path = 'model/yolov3.cfg' # 網路架構檔
    weight_path = 'model/yolov3.weights' # 網路權重
    label_path = 'model/coco.names' # 標籤名稱
    input_size = (416, 416) # 輸入層影像大小
    confidence_score = 0.5 # 準確率
    pre_defined_threshold = 0.3 # IOU
    use_gpu = False # 是否使用GPU