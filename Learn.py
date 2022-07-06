import time
import winsound

import cv2 as cv
import numpy as np

import Person
from tkinter import *
from tkinter.filedialog import askopenfile

def detect(fName):
    duration = 2000  # milliseconds
    freq = 1000  # Hz

    try:
        log = open('log.txt', "w")
    except:
        print("can't open log file")


    cnt_up = 0
    cnt_down = 0
    cnt_left = 0
    cnt_right = 0


    # cap = cv.VideoCapture(0)
    cap = cv.VideoCapture(fName)
    # camera = PiCamera()
    ##camera.resolution = (160,120)
    ##camera.framerate = 5
    ##rawCapture = PiRGBArray(camera, size=(160,120))
    ##time.sleep(0.1)

    ##cap.set(3,160) #Width
    ##cap.set(4,120) #Height

    for i in range(19):
        print(i, cap.get(i))

    h = 480
    w = 770

    frameArea = h * w
    areaTH = frameArea / 250
    print('Area Threshold', areaTH)

    line_up = int(40)
    line_down = int(340)
    line_left = int(570)
    line_right = int(570)

    up_limit = int(1 * (h / 5))
    down_limit = int(4 * (h / 5))
    left_limit = int(1 * (w / 5))
    right_limit = int(4 * (w / 5))

    print("Blue line y:", str(line_down))
    print("Blue line y:", str(line_up))
    print("Left line Y:", str(line_left))

    line_down_color = (255, 0, 0)
    line_up_color = (255, 0, 0)
    line_left_color = (255, 0, 0)

    pt1 = [0, line_down];
    pt2 = [w, line_down];
    pts_L1 = np.array([pt1, pt2], np.int32)
    pts_L1 = pts_L1.reshape((-1, 1, 2))

    pt3 = [0, line_up];
    pt4 = [w, line_up];
    pts_L2 = np.array([pt3, pt4], np.int32)
    pts_L2 = pts_L2.reshape((-1, 1, 2))

    pt9 = [50, 0];
    pt10 = [50, line_left];
    pts_L5 = np.array([pt9, pt10], np.int32)
    pts_L5 = pts_L5.reshape((-1, 1, 2))

    pt11 = [700, 0];
    pt12 = [700, line_right];
    pts_L6 = np.array([pt11, pt12], np.int32)
    pts_L6 = pts_L6.reshape((-1, 1, 2))

    fgbg = cv.createBackgroundSubtractorMOG2(detectShadows=True)

    kernelOp = np.ones((3, 3), np.uint8)
    kernelOp2 = np.ones((5, 5), np.uint8)
    kernelCl = np.ones((11, 11), np.uint8)

    # Variables
    font = cv.FONT_HERSHEY_SIMPLEX
    persons = []
    max_p_age = 5
    pid = 1

    while (cap.isOpened()):
        ##for image in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        ret, frame = cap.read()
        ##    frame = image.array

        for i in persons:
            i.age_one()  # age every person one frame

        fgmask = fgbg.apply(frame)
        fgmask2 = fgbg.apply(frame)

        try:
            ret, imBin = cv.threshold(fgmask, 200, 255, cv.THRESH_BINARY)
            ret, imBin2 = cv.threshold(fgmask2, 200, 255, cv.THRESH_BINARY)
            mask = cv.morphologyEx(imBin, cv.MORPH_OPEN, kernelOp)
            mask2 = cv.morphologyEx(imBin2, cv.MORPH_OPEN, kernelOp)
            mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernelCl)
            mask2 = cv.morphologyEx(mask2, cv.MORPH_CLOSE, kernelCl)
        except:
            print('EOF')
            print('OUT:', cnt_up)
            print('IT:', cnt_down)
            print('LEFT:', cnt_left)
            print('RIGHT:', cnt_right)
            print('INSIDE:', (cnt_down - cnt_up))
            break
        #################
        #   CONTORNOS   #
        #################

        contours0, hierarchy = cv.findContours(mask2, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours0:
            area = cv.contourArea(cnt)
            if area > areaTH:
                #################
                #   TRACKING    #
                #################


                M = cv.moments(cnt)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                x, y, w, h = cv.boundingRect(cnt)

                new = True
                if cy in range(up_limit, down_limit) or cx in range(left_limit, right_limit):
                    for i in persons:
                        if abs(x - i.getX()) <= w and abs(y - i.getY()) <= h:
                            # the object is close to one that was detected before
                            new = False
                            i.updateCoords(cx, cy)  # updates coordinates on the object and resets age
                            if i.going_UP(line_down, line_up) == True:
                                cnt_up += 1;
                                print("ID:", i.getId(), 'going out at', time.strftime("%c"))
                                log.write("ID: " + str(i.getId()) + 'going out at ' + time.strftime("%c") + '\n')
                            elif i.going_DOWN(line_down, line_up) == True:
                                cnt_down += 1;
                                print("ID:", i.getId(), 'going in at', time.strftime("%c"))
                                log.write("ID: " + str(i.getId()) + 'going in at ' + time.strftime("%c") + '\n')
                            elif i.going_LEFT(line_left, line_right) == True:
                                winsound.Beep(freq, duration)
                                cnt_left += 1;
                                print("ID:", i.getId(), 'going left at', time.strftime("%c"))
                                log.write("ID: " + str(i.getId()) + 'going left at ' + time.strftime("%c") + '\n')
                            elif i.going_RIGHT(line_left, line_right) == True:
                                cnt_right += 1;
                                print("ID:", i.getId(), 'going right at', time.strftime("%c"))
                                log.write("ID: " + str(i.getId()) + 'going right at ' + time.strftime("%c") + '\n')
                            break
                        if i.getState() == '1':
                            if i.getDir() == 'in' and i.getY() > down_limit:
                                i.setDone()
                            elif i.getDir() == 'out' and i.getY() < up_limit:
                                i.setDone()
                        if i.getState() == '1':
                            if i.getDir() == 'left' and i.getY() > left_limit:
                                i.setDone()
                            elif i.getDir() == 'right' and i.getY() < right_limit:
                                i.setDone()
                        if i.timedOut():
                            index = persons.index(i)
                            persons.pop(index)
                            del i
                    if new == True:
                        p = Person.MyPerson(pid, cx, cy, max_p_age)
                        persons.append(p)
                        pid += 1
                        #################
                #   DIBUJOS     #
                #################
                cv.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                img = cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # cv.drawContours(frame, cnt, -1, (0,255,0), 3)

        # END for cnt in contours0

        for i in persons:
            cv.putText(frame, str(i.getId()), (i.getX(), i.getY()), font, 0.3, i.getRGB(), 1, cv.LINE_AA)

        str_up = 'OUT: ' + str(cnt_up)
        str_down = 'IN: ' + str(cnt_down)
        str_inside = 'INSIDE: ' + str(cnt_down - cnt_up)
        frame = cv.polylines(frame, [pts_L1], False, line_down_color, thickness=2)
        frame = cv.polylines(frame, [pts_L2], False, (0, 0, 255), thickness=2)
        # frame = cv.polylines(frame, [pts_L3], False, (255, 255, 255), thickness=1)
        # frame = cv.polylines(frame, [pts_L4], False, (255, 255, 255), thickness=1)
        frame = cv.polylines(frame, [pts_L5], False, (0, 0, 255), thickness=2)
        frame = cv.polylines(frame, [pts_L6], False, (0, 0, 255), thickness=2)
        cv.putText(frame, str_up, (10, 60), font, 0.5, (255, 255, 255), 2, cv.LINE_AA)
        cv.putText(frame, str_up, (10, 60), font, 0.5, (0, 0, 255), 1, cv.LINE_AA)
        cv.putText(frame, str_down, (10, 90), font, 0.5, (255, 255, 255), 2, cv.LINE_AA)
        cv.putText(frame, str_down, (10, 90), font, 0.5, (0, 255, 0), 1, cv.LINE_AA)
        cv.putText(frame, str_inside, (10, 120), font, 0.5, (255, 255, 255), 2, cv.LINE_AA)
        cv.putText(frame, str_inside, (10, 120), font, 0.5, (255, 0, 0), 1, cv.LINE_AA)

        cv.imshow('Frame', frame)
        cv.imshow('Mask', mask)

        k = cv.waitKey(30) & 0xff
        if k == 27:
            break

    log.flush()
    log.close()
    cap.release()
    cv.destroyAllWindows()

root = Tk()
root.geometry('900x600')

# This function will be used to open
# file in read mode and only Python files
# will be opened
def open_file():
    file = askopenfile(mode ='r', filetypes =[('All Files', '*')])
    print(file.name)
    fileName=file.name
    detect(fileName)

def web_cam():
    detect(0)
# Create label
text = Label(root, text="Enter your video here 👇 ", font=('Times', 24),bg='black',fg='white')
text.place(x=280,y=50)
btn1 = Button(root, text ='INPUT', command = lambda:open_file(),height=5, width=30,font=('Times', 15),background='green',foreground='white')
btn2 = Button(root, text ='WEB CAM', command = lambda:web_cam(),height=5, width=30,font=('Times', 15),background='green',foreground='white')
btn1.pack(side = TOP, pady = 120)
btn2.pack(side = TOP)


mainloop()



