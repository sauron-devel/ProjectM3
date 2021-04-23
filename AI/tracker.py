import numpy as np
from trackingfilter import PredictionFilter, TRACKER_LIMIT
from scipy.optimize import linear_sum_assignment

#~Tracker globals
TRACKER_OBJECTS = {}
TRACK_SUCCESS_THRES = 4
TRACK_FAIL_THRES = 1
IOU_THRES = 0.6

#~ID update global
CURR_MAX_ID = None

#~For detection vs tracking comparison of bounding boxes (intersection over union)
def IoU(box_a,box_b):
    box_a_area = (box_a[2] - box_a[0]+1)*(box_a[3] - box_a[1]+1)
    box_b_area = (box_b[2] - box_b[0]+1)*(box_b[3] - box_b[1]+1)
    
    xA = max(box_a[0], box_b[0])
    yA = max(box_a[1], box_b[1])
    xB = max(box_a[2], box_b[2])
    yB = max(box_a[3], box_b[3])

    intersection_area = max(0, xB-xA+1) * max(0, yB-yA+1)
    
    return intersection_area / float(box_a_area + box_b_area - intersection_area)

#~ Using sklearn's implementation of linear assignment to match detections to trackers
#~ This uses the Hungarian linear assignment algorithm.
def IoU_assign(iou_map):
    map_max = np.max(iou_map)
    inverted_iou_map = map_max - iou_map

    match_idx = linear_sum_assignment(inverted_iou_map)
    match_idx = np.transpose(np.asarray(match_idx))
    return match_idx

#~ Convert tracker state vectors back to bounding boxes
def convert_tvec_to_bbox(vect):
    bbox = vect.T[0].tolist()

    bbox = bbox[:4]
    return bbox


#~ Filter trackers at end of each frame, remove trackers which exceed defined thresholds
def active_trackers():

    trackers_to_record = []
    trackers_to_discard = []

    for ID in TRACKER_OBJECTS:
        if TRACKER_OBJECTS[ID].OK <= TRACK_SUCCESS_THRES and TRACKER_OBJECTS[ID].EMPTY >= TRACK_FAIL_THRES:
            trackers_to_discard.append(ID)
        else:
            trackers_to_record.append(TRACKER_OBJECTS[ID].COORDS + [TRACKER_OBJECTS[ID].CLASS_ID] + [ID])
            

    for ID in trackers_to_discard:
        TRACKER_OBJECTS.pop(ID, "[MESSAGE] Tracker object already removed.")
    
    return trackers_to_record

#~ Main tracking pipeline, filtering incoming data for existing, new and missing trackers
#~ by linear assignment of bounding boxes to update filter measurements, and assigning new
#~ tracking IDs to the system, and use the filter to update.
def tracking_handler(curr_detections):
    global CURR_MAX_ID

    curr_trackers = []
    new_detection_idx = []
    empty_trackers_idx = []
    match_idx = []
    
    ignore_new_detections = True if len(TRACKER_OBJECTS) == TRACKER_LIMIT else False
    
    if len(TRACKER_OBJECTS) > 0:
        if CURR_MAX_ID <= max(TRACKER_OBJECTS.keys()):
            CURR_MAX_ID = max(TRACKER_OBJECTS.keys())
    elif CURR_MAX_ID == None:
        CURR_MAX_ID = 0

    for tobj in TRACKER_OBJECTS:
        curr_trackers.append([TRACKER_OBJECTS[tobj].COORDS, TRACKER_OBJECTS[tobj].ID])

    curr_trackers = np.array(curr_trackers)
    
    if len(curr_trackers) != 0 and len(curr_detections) != 0:
        iou_map = np.zeros([len(curr_trackers), len(curr_detections)])
        for t in range(len(curr_trackers)):
            for d in range(len(curr_detections)):
                iou_map[t,d] = IoU(curr_trackers[t,0],curr_detections[d,:4])

        match_idx = IoU_assign(iou_map)
        
        for m in match_idx:
            if (iou_map[m[0],m[1]]) < IOU_THRES:
                empty_trackers_idx.append(m[0])
                new_detection_idx.append(m[1])
    else:
        if len(curr_detections) > 0:
            for d in range(len(curr_detections)):
                new_detection_idx.append(d)

        if len(curr_trackers) > 0:
            for t in range(len(curr_trackers)):
                empty_trackers_idx.append(t)
          
    if len(match_idx) > 0:
        for match in match_idx:
            local_track_idx = match[0]
            det_idx = match[1]

            detection_coords = curr_detections[det_idx,:4]
            tracker_coords = curr_trackers[local_track_idx,0]
            tracker_id = curr_trackers[local_track_idx,1]

            tracker_obj = TRACKER_OBJECTS[tracker_id]

            tracker_obj.initialise_meas_vector_Z(detection_coords)
            tracker_obj.KF_predict_and_track()
            tracker_obj.COORDS = convert_tvec_to_bbox(tracker_obj.X)
            tracker_obj.OK += 1
            tracker_obj.EMPTY = 0

    if len(new_detection_idx) > 0 and ignore_new_detections == False:
        for idxD in new_detection_idx:
            detection_coords = curr_detections[idxD,:4]

            new_tracker_obj = PredictionFilter()
            new_id, CURR_MAX_ID = new_tracker_obj.update_id(CURR_MAX_ID, TRACKER_OBJECTS)
            
            if new_id == None:
                ignore_new_detections == True
                del new_tracker_obj
                break

            new_tracker_obj.CLASS_ID = curr_detections[idxD,4]
            
            new_tracker_obj.initialise_state_vector_X(detection_coords)
            new_tracker_obj.KF_predict()
            new_tracker_obj.COORDS = convert_tvec_to_bbox(new_tracker_obj.X)

            TRACKER_OBJECTS[new_id] = new_tracker_obj
    
    if len(empty_trackers_idx) > 0:
        for idxT in empty_trackers_idx:
            local_track_idx = idxT
            tracker_coords = curr_trackers[local_track_idx,0]
            tracker_id = curr_trackers[local_track_idx,1]

            tracker_obj = TRACKER_OBJECTS[tracker_id]
            tracker_obj.EMPTY += 1
            tracker_obj.OK = 0

            tracker_obj.KF_predict()
            tracker_obj.COORDS = convert_tvec_to_bbox(tracker_obj.X)

    return active_trackers()
    