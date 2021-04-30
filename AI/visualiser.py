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

def show(image, data, labels, fps, SHOW="ALL"):
    o_dets = data[0]
    t_dets = data[1]

    if SHOW != "ALL":
        if SHOW == "DETECTED_ONLY":
            image = visualise_detections_only(image, o_dets, labels)
            return image
        if SHOW == "TRACKED_ONLY":
            image = visualise_trackers_only(image, t_dets, labels)
            return image
        if SHOW == "" or SHOW == "NONE":
            return image
    else:
        image = visualise_detections_only(image, o_dets, labels)
        image = visualise_trackers_only(image, t_dets, labels)
        image = cv2.putText(image, "FPS: "+fps, (5,14), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (140, 30, 245), 1, cv2.LINE_AA)
        return image



        
