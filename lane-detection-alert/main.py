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
    filetype=[("MP4 files", "*.mp4"), ("AVI files", "*.avi")])

if file_path.endswith((".mp4", ".avi")):
    cap = cv2.VideoCapture(file_path)

    # flag for smooth processing
    iframe = 1  # index of frame
    found = False  # Found lanes
    while True:
        ret, frame = cap.read()
        word_count = 0

        left_final_line, right_final_line, car_center = function(
            frame, iframe, found)

        if left_final_line.all():
            cv2.line(frame, (int(left_final_line[0]), int(left_final_line[1])), (int(left_final_line[2]), int(left_final_line[3])),
                     (102, 0, 255), 4, cv2.LINE_AA)
        if right_final_line.all():
            cv2.line(frame, (int(right_final_line[0]), int(right_final_line[1])), (int(right_final_line[2]), int(right_final_line[3])),
                     (102, 0, 255), 4, cv2.LINE_AA)

        if right_final_line.all() and right_final_line.all():
            found = True

        if left_final_line.all() and right_final_line.all():
            center = np.array([(left_final_line[2] + right_final_line[2]) / 2,
                               (left_final_line[3] + right_final_line[3]) / 2 - 50])
            cv2.line(frame, (int(center[0] - 25), int(center[1])), (int(center[0] + 25), int(center[1])),
                     (0, 255, 0), 4, cv2.LINE_AA)
            cv2.line(frame, (int(center[0]), int(center[1] - 25)), (int(center[0]), int(center[1] + 25)),
                     (0, 255, 0), 4, cv2.LINE_AA)

            offset = center[0] - car_center
            if offset < 0:
                remind = "Right %f of center" % (abs(offset))
            else:
                remind = "Left %f of center" % (offset)

            if abs(offset) > 120:
                color = (0, 0, 255)
            else:
                color = (255, 255, 255)

            cv2.putText(frame, remind, (100, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
        # Detect Cars
        cars = detect_cars(frame)
        for (x, y, w, h) in cars:
            if frame.shape[1]/3 < x < 2*frame.shape[1]/3:
                cv2.rectangle(frame, (x, y+3*int(frame.shape[0]/10)-20), (x+100, y+3*int(
                    frame.shape[0]/10)), (255, 255, 255), -1)
                cv2.putText(frame, 'Car', (x+40, y+3*int(
                    frame.shape[0]/10)-4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.rectangle(
                    frame, (x, y+3*int(frame.shape[0]/10)), (x+w, y+h+3*int(frame.shape[0]/10)), (255, 255, 255), 1)

        cv2.imshow("origin", frame)

        if cv2.waitKey(20) & 0xFF == ord("q"):
            break

        iframe += 1

    cap.release()
    cv2.destroyAllWindows()
    window.destroy()
