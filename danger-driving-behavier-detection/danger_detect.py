import numpy as np
import cv2
from matplotlib.path import Path

# 讀取圖片
img = cv2.imread('test.png')

# 設定多邊形頂點座標
pts0 = np.array([[162, 267], [215, 160], [227, 71], [212, 53], [
                192, 36], [208, 36], [507, 238], [504, 278]], np.int32)
# 將座標轉為 (頂點數量, 1, 2) 的陣列
pts = pts0.reshape((-1, 1, 2))
# 繪製多邊形
cv2.polylines(img, [pts], True, (255, 255, 0), 4)


# detect into area
text = 'car into warning area'
vehicle_pos = list(pts0)
p = Path(vehicle_pos)
xx = p.contains_points([(361.0, 199.0)])
if xx:
    cv2.putText(img, text, (100, 40), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 0, 255), 3)


cv2.imshow('Detect result', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
