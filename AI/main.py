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

#*TEST BLOCK {...} 

#~Camera feed globals
VIDEO_SOURCE = "testvideos/stockvideo6.webm" #0

FRAME_INPUT_DIMS = (1280,720)

#~Object detection inference globals
#INF_GRAPH='faster_rcnn_resnet50_coco_2018_01_28/frozen_inference_graph.pb'
#INF_GRAPH='faster_rcnn_inception_resnet_v2_atrous_oid_2018_01_28/frozen_inference_graph.pb' too slow
#INF_GRAPH='ssd_mobilenet_v3_large_coco_2020_01_14/frozen_inference_graph.pb' doesnt work
#INF_GRAPH='ssd_mobilenet_v2_quantized_300x300_coco_2019_01_03/frozen_inference_graph.pb' doesnt work
#INF_GRAPH='ssd_mobilenet_v2_coco_2018_03_29/frozen_inference_graph.pb'
#INF_GRAPH='ssd_mobilenet_v1_fpn_shared_box_predictor_640x640_coco14_sync_2018_07_03/frozen_inference_graph.pb'
#INF_GRAPH='ssd_inception_v2_coco_2018_01_28/frozen_inference_graph.pb'
#INF_GRAPH = 'faster_rcnn_nas_coco_2018_01_28/frozen_inference_graph.pb'
#INF_GRAPH = 'ssd_resnet101_v1_fpn_shared_box_predictor_oid_512x512_sync_2019_01_20/frozen_inference_graph.pb'
#INF_GRAPH = 'faster_rcnn_inception_resnet_v2_atrous_oid_v4_2018_12_12/frozen_inference_graph.pb'
#INF_GRAPH = 'ssd_mobilenet_v2_oid_v4_2018_12_12/frozen_inference_graph.pb'
INF_GRAPH = 'inceptionv2frcnn/frozen_inference_graph.pb'
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
    #~ Initialise deep learning model to detect objects
    modelinfo = InitModel(INF_GRAPH, LABELMAP)
    labels = modelinfo.load_labels()
    sess,det_graph = modelinfo.graph_import()

    #~ Initialise video stream
    frame_count = 0
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
        
        #~ Track these detections 
        tracked_detections = tracking_handler(detections, FRAME_INPUT_DIMS)

        #~ Data transfer function
        write_data(tracked_detections)

        #~ Display function for the bounding boxes with labels and person ID
        # To show only detections add optional argument SHOW="DETECTED_ONLY"
        # or for trackers "TRACKED_ONLY", to show nothing add empty string "" or "NONE"
        
        fps_b = time.time() 
        fps = str(round(1/(fps_b - fps_a),2))
        
        frame = visualiser.show(frame, [detections,tracked_detections], labels, fps, SHOW="ALL")

        #~ Show frame
        cv2.imshow("debug feed", frame)

        frame_count += 1
        if cv2.waitKey(25) and 0xFF == ord('q'):  #put back
            break

    cv2.destroyAllWindows()
    sess.close()
    exit()

if __name__ == "__main__":
    main()



