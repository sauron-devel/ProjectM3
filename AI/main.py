import os
import sys
import cv2
import time
import numpy as np
from datetime import datetime

import objectdetector
import videostream
import visualiser
from objectdetector import InitModel
from tracker import tracking_handler

from personcounter import backend


#*TEST BLOCK {...} 

#~Camera feed globals
VIDEO_SOURCE = "testvideos/stockvideo6.webm" #0

FRAME_INPUT_DIMS = (720,405)

#~Object detection inference globals
#INF_GRAPH='ssd_inception_v2_coco_2018_01_28/frozen_inference_graph.pb' #*det_thres=0.35, nms_thres=0.8, tracker:0.2,0.7,0.2,5,4, R scalar *100 (much more noise)
INF_GRAPH = 'inceptionv2frcnn/frozen_inference_graph.pb' #*det_thres=0.75, nms_thres=0.75, tracker:0.3,0.6,0.5,5,2

LABELMAP='labelmap.pbtxt'

def write_data(frame, data):
    timestamp = str(datetime.now())
    output_string = timestamp + ">> " + str(data) + "\n"
    return backend(frame,output_string)

def main():
    #~ Initialise deep learning model to detect objects
    modelinfo = InitModel(INF_GRAPH, LABELMAP)
    labels = modelinfo.load_labels()
    sess,det_graph = modelinfo.graph_import()

    #~ Initialise video stream
    frame_count = 0 #debug
    stream = videostream.set_input_feed(VIDEO_SOURCE)
    
    stream.start()

    #~ Start main loop for constant detection and tracking
    while(stream.running):
        #~ Get current active frame
        fps_a = time.time()

        frame = stream.get()
        frame = cv2.resize(frame, (FRAME_INPUT_DIMS[0], int(FRAME_INPUT_DIMS[1])))

        #~ Get detections off the current frame
        detections = objectdetector.model_inference(sess, frame, det_graph, labels)        
        print("Number of initial detections: ", len(detections))

        #~ Track these detections 
        tracked_detections = tracking_handler(detections, FRAME_INPUT_DIMS)
        print("Number of currently tracked detections: ", len(tracked_detections))

        #~ Data transfer function
        frame,threshold,counter = write_data(frame, tracked_detections)

        #~ Calculate FPS
        fps_b = time.time() 
        fps = str(round(1/(fps_b - fps_a),2))

        #~ Display debug function for the bounding boxes with labels and person ID
        # To show only detections add optional argument SHOW="DETECTED_ONLY"
        # or for trackers "TRACKED_ONLY", or for only counter, "COUNTER_ONLY",
        # to show nothing add empty string "" or "NONE"
        frame = visualiser.show(
            frame, 
            [detections,tracked_detections], 
            labels, 
            fps, 
            frame_count,
            threshold,
            counter, 
            SHOW="ALL")

        #~ Show frame
        cv2.imshow("debug feed", frame)

        frame_count += 1 #debug
        
        if cv2.waitKey(25) and 0xFF == ord('q'):  #put back
            break

    cv2.destroyAllWindows()
    sess.close()
    exit()

if __name__ == "__main__":
    main()



