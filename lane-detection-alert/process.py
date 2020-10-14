import cv2
import numpy as np
from math import isinf

def detect_cars(img):
    
    cascade = cv2.CascadeClassifier('cars.xml')
    img = img[3*int(img.shape[0]/10):9*int(img.shape[0]/10),:]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    
    cars = cascade.detectMultiScale(gray,
                                     # detector options
                                     1.1,2, minSize=(100,100))
    return cars
    
def find_interest_region(edges, vertices):
    mask = np.zeros_like(edges)
    cv2.fillPoly(mask, vertices, 255)
    masked_img = cv2.bitwise_and(edges, mask)

    return (masked_img)

def get_slope(x1, y1, x2, y2):
    return 0 if x2-x1 == 0 else (y2 - y1) / (x2 - x1)

def find_line(img, lines, frameindex, found):
    
    global cache
    alpha = 0.2
    y_max = img.shape[0]
    y_min = img.shape[0] / 2 + img.shape[0] / 6

    left_lane, right_lane = [], []
    left_slope, right_slope = [], []
    proper_slope = 0.4

    # Preset output as [0,0,0,0] for two lines if no lane was detected
    leftFinal = np.zeros(4)
    rightFinal = np.zeros(4)

    
    # Find Line in result of HoughTranform and add into list if it exist
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                slope = get_slope(x1, y1, x2, y2)
                if slope > proper_slope:
                    right_lane.append(line)
                    right_slope.append(slope)
                elif slope < -proper_slope:
                    left_lane.append(line)
                    left_slope.append(slope)

            # y_global_min = min(y1,y2,y_global_min) 
    
    # If one lane is not detected then return empty
    if((len(left_lane) == 0) or (len(right_lane) == 0)):
        return (leftFinal, rightFinal)

    # Get average of slopes and every x,y values
    left_lane_mean = np.mean(left_lane, axis=0)
    right_lane_mean = np.mean(right_lane, axis=0)
    left_slope_mean = np.mean(left_slope, axis=0)
    right_slope_mean = np.mean(right_slope, axis=0)

    # Return empty list if slope is 0 to prevent deviding by 0
    if ((right_slope_mean == 0) or (left_slope_mean == 0 )):
        return (leftFinal,rightFinal)

    # Get b of lane function
    # y = mx + b
    # b = y - mx
    left_b = left_lane_mean[0][1] - (left_slope_mean * left_lane_mean[0][0])
    right_b = right_lane_mean[0][1] - (right_slope_mean * right_lane_mean[0][0])

    # Get x values from each left and right lane function
    l_x1 = int((y_min - left_b)/left_slope_mean) 
    l_x2 = int((y_max - left_b)/left_slope_mean)   
    r_x1 = int((y_min - right_b)/right_slope_mean)
    r_x2 = int((y_max - right_b)/right_slope_mean)

    
    # Smooth Processing
    # Record all points in current frame
    current_frame = np.array([l_x1,y_min,l_x2,y_max,r_x1,y_min,r_x2,y_max],dtype ="float32")
    
    if frameindex == 1:
        next_frame = current_frame
        cache = current_frame
        frameindex = 0     
    elif found == False:
        next_frame = current_frame
        cache = current_frame
    else :
        prev_frame = cache
        next_frame = (1-alpha)*prev_frame+(alpha)*current_frame

    cache = next_frame

    leftFinal = np.array([next_frame[0], next_frame[1], next_frame[2], next_frame[3]])
    rightFinal = np.array([next_frame[4], next_frame[5], next_frame[6], next_frame[7]])

    return (leftFinal,rightFinal)

def function(img, frameindex, found):
    # filte color and tranfer to gaussian (make it smooth)

    # new_gray_img = filte_color(img)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.GaussianBlur(gray_img, (5, 5), 0)

    # Canny edge detection
    new_edges = cv2.Canny(gray_img, 50, 150)

    # trapezoid doesn't include the front of the car
    img_shape = img.shape
    down_left = [img_shape[1] / 9, img_shape[0]]
    down_right = [img_shape[1] - img_shape[1] / 9, img_shape[0]]
    top_left = [img_shape[1] / 2 - img_shape[1] /
                8, img_shape[0] / 2 + img_shape[0] / 10]
    top_right = [img_shape[1] / 2 + img_shape[1] /
                 8, img_shape[0] / 2 + img_shape[0] / 10]
    vertices = [
        np.array([down_left, top_left, top_right, down_right ], dtype=np.int32)]

    car_center = (down_left[0] + down_right[0]) / 2

    # extract the trapezoid region
    new_img = (find_interest_region(new_edges, vertices))
    
    # hough transform key point at this project
    lines = cv2.HoughLinesP(new_img, 2, np.pi / 60, 50, np.array([]), 50, 200)

    lines_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)

    left_final_line, right_final_line = find_line(img, lines, frameindex, found)

    return (left_final_line, right_final_line, car_center)
