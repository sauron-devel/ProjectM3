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


#~Camera feed globals
CAMERA_SOURCE = 0
FRAME_INPUT_DIMS = (640,480)

#~Object detection inference globals
INF_GRAPH='ssd_inception_v2_coco_2018_01_28/frozen_inference_graph.pb'
LABELMAP='labelmap.pbtxt'

#~Data transfer pipe 
OUTPUT_FILE_ADDR = 'ai-out'

def write_data(data):
    FIFO = open(OUTPUT_FILE_ADDR, 'w')
    timestamp = str(datetime.now())
    FIFO.write(timestamp + ">> " + str(data) + "\n")
    FIFO.flush()
    FIFO.close()

def main():
    #~ Initialise video stream
    stream = videostream.set_input_feed(CAMERA_SOURCE)
    stream.start()

    #~ Initialise deep learning model to detect objects
    modelinfo = InitModel(INF_GRAPH, LABELMAP)
    labels = modelinfo.load_labels()
    sess,det_graph = modelinfo.graph_import()

    #~ Start main loop for constant detection and tracking
    while(stream.running):
        #~ Get current active frame
        frame = stream.get()
        frame = cv2.resize(frame, (FRAME_INPUT_DIMS[0], FRAME_INPUT_DIMS[1]))

        #~ Get detections off the current frame
        detections = objectdetector.model_inference(sess, frame, det_graph, labels)        
        
        #~ Track these detections
        tracked_detections = tracking_handler(detections)

        #~ Data transfer function
        write_data(tracked_detections)

        #~ Display function for the bounding boxes with labels and person ID
        # To show only detections add optional argument SHOW="DETECTED_ONLY"
        # or for trackers "TRACKED_ONLY", to show nothing add empty string "" or "NONE"
        frame = visualiser.show(frame, [detections,tracked_detections], labels)

        #~ Show frame
        cv2.imshow("debug feed", frame)

        if cv2.waitKey(25) and 0xFF == ord('q'):  #put back
            break

    cv2.destroyAllWindows()
    sess.close()
    exit()

if __name__ == "__main__":
    main()



