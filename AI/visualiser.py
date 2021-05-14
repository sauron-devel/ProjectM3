import cv2
import numpy as np
from random import randrange as rand

def visualise_detections_only(image, detections, labels):
    for i in detections:
        image = cv2.rectangle(image, (i[0],i[1]), (i[2],i[3]), (255,80,80), 1)
        image = cv2.rectangle(image, (i[0],i[1]-12), (i[2],i[1]+4), (200,129,123), -1)
        text = labels[i[4]].upper()
        image = cv2.putText(image, text, (i[0]+1,i[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (70,70,70), 1, cv2.LINE_AA)
    return image 

def visualise_trackers_only(image, tracked_dets, labels):
    for i in tracked_dets:
        image = cv2.rectangle(image, (i[0],i[1]), (i[2],i[3]), (20,20,170), 2)
        image = cv2.rectangle(image, (i[0]-1,i[1]-12), (i[2]+1,i[1]+4), (rand(90,100),rand(90,100),rand(235,255)), -1)
        text = labels[i[4]].upper() + " | ID:" + str(i[5]) #check if right order
        image = cv2.putText(image, text, (i[0]+1,i[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, cv2.LINE_AA)
    return image

def visualise_counter_only(image, threshold, counter):
    frame = cv2.line(image, (threshold, 0),(threshold,int(image.shape[0])),(0,0,255),5)
    font = cv2.FONT_HERSHEY_SIMPLEX
    frame = cv2.putText(frame,
        "COUNTER: " + str(counter), 
        (5,35), 
        font, 
        0.5,
        (230,102,30),
        2)
    return image

def show(image, data, labels, fps, frame_count, threshold, counter, SHOW="ALL"):
    o_dets = data[0]
    t_dets = data[1]

    #Visualise FPS first
    image = cv2.putText(image, "FPS: "+fps, (5,14), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (140, 30, 245), 1, cv2.LINE_AA)

    if SHOW != "ALL":
        if SHOW == "DETECTED_ONLY":
            image = visualise_detections_only(image, o_dets, labels)
            return image
        if SHOW == "TRACKED_ONLY":
            image = visualise_trackers_only(image, t_dets, labels)
            return image
        if SHOW == "COUNTER_ONLY":
            image = visualise_counter_only(image, threshold, counter)            
        if SHOW == "" or SHOW == "NONE":
            return image
    else:
        image = visualise_detections_only(image, o_dets, labels)
        # if frame_count % 5 == 0: #image saving debug
        #     cv2.imwrite("tests/exampledet_{}.jpg".format(str(frame_count)), image)
        
        image = visualise_trackers_only(image, t_dets, labels)
        # if frame_count % 5 == 0: #image saving debug
        #     cv2.imwrite("tests/exampletrack_{}.jpg".format(str(frame_count)), image)
        
        image = visualise_counter_only(image,threshold, counter)
        # if frame_count % 5 == 0: #image saving debug
        #     cv2.imwrite("tests/exampletrack_{}.jpg".format(str(frame_count)), image)

        return image



        
