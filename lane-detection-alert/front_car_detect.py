import cv2
import tkinter as tk
import copy
import numpy as np
from tkinter import filedialog
from matplotlib import pyplot as plt
from process import function, detect_cars

window = tk.Tk()
window.withdraw()
file_path = filedialog.askopenfilename(
    filetype=[("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("JPG files", "*.jpg")])

if file_path.endswith(".jpg"):
    origin_img = cv2.imread(file_path)
    img = copy.deepcopy(origin_img)

    left_final_line, right_final_line = function(img)
    cv2.line(img, (int(left_final_line[0]), int(left_final_line[1])), (int(left_final_line[2]), int(left_final_line[3])),
             (255, 0, 0), 5, cv2.LINE_AA)
    cv2.line(img, (int(right_final_line[0]), int(right_final_line[1])), (int(right_final_line[2]), int(right_final_line[3])),
             (255, 0, 0), 5, cv2.LINE_AA)

    left_up = [int(left_final_line[0]), int(left_final_line[1])]
    left_down = [int(left_final_line[2]), int(left_final_line[3])]
    right_up = [int(right_final_line[0]), int(right_final_line[1])]
    right_down = [int(right_final_line[2]), int(right_final_line[3])]
    a = np.array([[left_up, left_down, right_down, right_up]], dtype=np.int32)
#     cv2.fillPoly(img, a, 170)
    cars = detect_cars(img)


    for (x, y, w, h) in cars:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)

    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.title('Original Image')
    plt.xticks([]), plt.yticks([])
    plt.imshow(origin_img)

    plt.subplot(1, 2, 2)
    plt.title('Process Image')
    plt.xticks([]), plt.yticks([])
    plt.imshow(img)

    window.destroy()
    plt.show()

elif file_path.endswith((".mp4", ".avi")):
    cap = cv2.VideoCapture(file_path)
    # out = cv2.VideoWriter("process.mp4", cv2.VideoWriter_fourcc('M', 'P', '4', "V"), cap.get(cv2.CAP_PROP_FPS),
    #                      (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    
    # flag for smooth processing
    iframe = 1 # index of frame
    found = False # Found lanes 
    while True:
        ret, frame = cap.read()
        word_count = 0

        
        left_final_line, right_final_line, car_center = function(frame, iframe, found)

        # Detect Cars
        front_car = None
        cars = detect_cars(frame)
        for (x, y, w, h) in cars:
            if x < car_center < x + w:
                if front_car is None:
                    front_car = (x, y, w, h)
                else:
                    if y + h / 2 > front_car[1] + front_car[3] / 2:
                        front_car = (x, y, w, h)

            if frame.shape[1]/3 < x < 2*frame.shape[1]/3:
                cv2.rectangle(frame, (x, y+3*int(frame.shape[0]/10)-20), (x+100, y+3*int(frame.shape[0]/10)), (255, 255, 255), -1)
                cv2.putText(frame, 'Car', (x+40, y+3*int(frame.shape[0]/10)-4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
                cv2.rectangle(frame, (x, y+3*int(frame.shape[0]/10)), (x+w, y+h+3*int(frame.shape[0]/10)), (255, 255, 255), 1)


        if left_final_line.all():
            cv2.line(frame, (int(left_final_line[0]), int(left_final_line[1])), (int(left_final_line[2]), int(left_final_line[3])),
                     (102, 0, 255), 4, cv2.LINE_AA)
        if right_final_line.all():
            cv2.line(frame, (int(right_final_line[0]), int(right_final_line[1])), (int(right_final_line[2]), int(right_final_line[3])),
                     (102, 0, 255), 4, cv2.LINE_AA)

        if right_final_line.all() and right_final_line.all():
            found = True

        if left_final_line.all() and right_final_line.all() and front_car is not None:
            center = np.array([(left_final_line[2] + right_final_line[2]) / 2, (left_final_line[3] + right_final_line[3]) / 2 - 50])
            cv2.line(frame, (int(center[0] - 25), int(center[1])), (int(center[0] + 25), int(center[1])), 
                    (0, 255, 0), 4, cv2.LINE_AA)
            cv2.line(frame, (int(center[0]), int(center[1] - 25)), (int(center[0]), int(center[1] + 25)), 
                    (0, 255, 0), 4, cv2.LINE_AA)

            offset = center[0] - (front_car[0] + front_car[3] / 2)
            if offset < 0:
                remind = "Right %f of center" % (abs(offset))
            else:
                remind = "Left %f of center" % (offset)

            if abs(offset) > 120:
                color = (0, 0, 255)
            else:
                color = (100, 255, 100)

            # Offset text
            cv2.putText(frame, remind, (100, 100),cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

            # Front car text
            print(front_car)
            cv2.rectangle(frame, (front_car[0], front_car[1]+3*int(frame.shape[0]/10)-20), (x+100, y+3*int(frame.shape[0]/10)), color, -1)
            cv2.putText(frame, 'Car', (front_car[0]+40, front_car[1]+3*int(frame.shape[0]/10)-4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            cv2.rectangle(frame, (front_car[0], front_car[1]+3*int(frame.shape[0]/10)), (x+w, y+h+3*int(frame.shape[0]/10)), color , 1)

        
        
                
        cv2.imshow("origin", frame)
        # out.write(frame)

        if cv2.waitKey(20) & 0xFF == ord("q"):
            break

        iframe += 1

    cap.release()
    # out.release()
    cv2.destroyAllWindows()
    window.destroy()
