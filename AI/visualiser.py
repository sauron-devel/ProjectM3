import cv2
import numpy as np

def visualise_detections_only(image, detections, labels):
    for i in detections:
        image = cv2.rectangle(image, (i[0],i[1]), (i[2],i[3]), (255,80,255), 1)
        image = cv2.rectangle(image, (i[0],i[1]-12), (i[2],i[1]+4), (200,200,255), -1)
        text = labels[i[4]].upper()
        image = cv2.putText(image, text, (i[0]+1,i[1]), cv2.FONT_HERSHEY_PLAIN, 0.6, (10,10,10), 1)

    return image 

def visualise_trackers_only(image, tracked_dets, labels):
    for i in tracked_dets:
        image = cv2.rectangle(image, (i[0],i[1]), (i[2],i[3]), (20,20,170), 2)
        image = cv2.rectangle(image, (i[0],i[1]-12), (i[2],i[1]+4), (10,10,150), -1)
        text = labels[i[4]].upper() + " ID: " + str(i[5]) #check if right order
        image = cv2.putText(image, text, (i[0]+1,i[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    return image

def show(image, data, labels, SHOW="ALL"):
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
        return image



        
