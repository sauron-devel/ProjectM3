import numpy as np
from trackingfilter import PredictionFilter, TRACKER_LIMIT
from scipy.optimize import linear_sum_assignment
from sklearn.utils.linear_assignment_ import linear_assignment
from math import exp

#~Tracker globals
TRACKER_OBJECTS = {}
TRACK_SUCCESS_THRES = 4
TRACK_FAIL_THRES = 2
IOU_THRES = 0.3

#~For detection vs tracking comparison of bounding boxes (intersection over union)
def IoU(box_a,box_b):
    box_a_area = (box_a[2] - box_a[0]+1)*(box_a[3] - box_a[1]+1)
    box_b_area = (box_b[2] - box_b[0]+1)*(box_b[3] - box_b[1]+1)
    
    xA = max(box_a[0], box_b[0])
    yA = max(box_a[1], box_b[1])
    xB = min(box_a[2], box_b[2])
    yB = min(box_a[3], box_b[3])

    intersection_area = max(0, xB-xA+1) * max(0, yB-yA+1)
    
    return intersection_area / float(box_a_area + box_b_area - intersection_area)

#~ Using sklearn's implementation of linear assignment to match detections to trackers
#~ This uses the Hungarian linear assignment algorithm.
def IoU_assign(iou_map):
    map_max = np.max(iou_map)
    inverted_iou_map = map_max - iou_map

    match_idx = linear_assignment(inverted_iou_map)
    #match_idx = np.transpose(np.asarray(match_idx))
    return match_idx

def update_measurement_noise(curr_det, other_dets, frame_size):

    x = (curr_det[2] - curr_det[0]) * (curr_det[3] - curr_det[1])
    x = (x/(frame_size[0]*frame_size[1])) * 100
    meas_noise = float(0.110099+3.529703659*(10**(-43))*exp(0.980789**x))
    
    base_point = (int((curr_det[2] - curr_det[0])/2), curr_det[3])
    box_width = curr_det[2] - curr_det[0]
    print("after calc", meas_noise, base_point, box_width)
    small_ovr = 1
    big_ovr = 1
    for i in other_dets:
        if curr_det != i:
            oth_base_point = (int((i[2] - i[0])/2), i[3])
            oth_box_width = curr_det[2] - curr_det[0]

            if abs(base_point[0] - oth_base_point[0]) < box_width:
                print("basepoint diff", base_point[0]- oth_base_point[0])
                dist = (abs(base_point[0]-oth_base_point[0])**2 + abs(base_point[1] - oth_base_point[1])**2)**(0.5)
                print("dist", dist)
                if dist <= box_width/1.5:
                    big_ovr += 1
                elif dist <= box_width:
                    small_ovr += 1
    
    meas_noise *= (small_ovr * 2)
    meas_noise *= (big_ovr * 10)

    print(float(meas_noise))
    return meas_noise

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

#~ Assign trackers to detections when there are both previous trackers and current detections
def assign_trackers(curr_trackers, curr_detections):
        new_detection_idx = []
        empty_trackers_idx = []
        match_idx = []
        match_idx_to_remove = []

        # Assign all trackers to detections based on IOU between bboxes
        iou_map = np.zeros([len(curr_trackers), len(curr_detections)])
        for t in range(len(curr_trackers)):
            for d in range(len(curr_detections)):
                iou_map[t,d] = IoU(curr_trackers[t,0], curr_detections[d,:4])

        match_idx = IoU_assign(iou_map)

        # Check all assignments, if some assignments fall under IOU threshold, remove them
        # and add to empty trackers/new detections
        for idx, match in enumerate(match_idx):
            print("idx,match in enumerate match", idx, match)
            if (iou_map[match[0],match[1]]) < IOU_THRES:
                match_idx_to_remove.append(idx)
                empty_trackers_idx.append(match[0])
                new_detection_idx.append(match[1])
        
        # Check for all unassigned indexes, and add to empty trackers/new detections
        track_col = match_idx[:,0]
        det_col = match_idx[:,1]

        for d in range(len(curr_detections)):
            if d not in det_col:
                new_detection_idx.append(d)

        for t in range(len(curr_trackers)):
            if t not in track_col:
                empty_trackers_idx.append(t)

        #Delete all unused matches that were under the IOU threshold
        if len(match_idx_to_remove) > 0:
            np.delete(match_idx, match_idx_to_remove, axis=0)

        return match_idx, new_detection_idx, empty_trackers_idx

def assign_unmatched(curr_trackers, curr_detections):
    new_detection_idx = []
    empty_trackers_idx = []
    
    for d in range(len(curr_detections)):
        new_detection_idx.append(d)

    for t in range(len(curr_trackers)):
        empty_trackers_idx.append(t)

    return new_detection_idx, empty_trackers_idx


def create_tracker(det_idx, curr_detections, frame_size):
    print("initialising new detection")
    detection_coords = curr_detections[det_idx,:4]

    new_tracker_obj = PredictionFilter()
    
    new_id = new_tracker_obj.update_id(TRACKER_OBJECTS) #!!!!
    print("NEW ID: ", new_id)

    #In the case that all available IDs are full:
    if new_id == None:
        del new_tracker_obj
        return False

    new_tracker_obj.meas_noise = update_measurement_noise(detection_coords,curr_detections,frame_size)

    new_tracker_obj.CLASS_ID = curr_detections[det_idx,4]
    
    new_tracker_obj.initialise_state_vector_X(detection_coords)
    new_tracker_obj.KF_predict()
    new_tracker_obj.COORDS = convert_tvec_to_bbox(new_tracker_obj.X)

    TRACKER_OBJECTS[new_id] = new_tracker_obj
    return True

def update_tracker(match, curr_detections, curr_trackers, frame_size):        
    print("checking matches")
    print("match:", match)
    local_track_idx = match[0]
    det_idx = match[1]

    detection_coords = curr_detections[det_idx,:4]
    tracker_id = curr_trackers[local_track_idx,1]

    tracker_obj = TRACKER_OBJECTS[tracker_id]
    tracker_obj.meas_noise = update_measurement_noise(detection_coords,curr_detections, frame_size)

    tracker_obj.initialise_meas_vector_Z(detection_coords)
    tracker_obj.KF_predict_and_track()
    tracker_obj.COORDS = convert_tvec_to_bbox(tracker_obj.X)
    tracker_obj.OK += 1
    tracker_obj.EMPTY = 0


def manage_empty_tracker(track_idx, curr_trackers):
    print("dealing with empty tracker")
    local_track_idx = track_idx
    tracker_id = curr_trackers[local_track_idx,1]

    tracker_obj = TRACKER_OBJECTS[tracker_id]
    tracker_obj.EMPTY += 1
    tracker_obj.OK = 0

    tracker_obj.KF_predict()
    tracker_obj.COORDS = convert_tvec_to_bbox(tracker_obj.X)

#~ Main tracking pipeline, filtering incoming data for existing, new and missing trackers
#~ by linear assignment of bounding boxes to update filter measurements, and assigning new
#~ tracking IDs to the system, and use the filter to update.
def tracking_handler(curr_detections, frame_size):
    #Initialise essential variables

    curr_trackers = []
    new_detection_idx = []
    empty_trackers_idx = []
    match_idx = []

    for tobj in TRACKER_OBJECTS:
        curr_trackers.append([TRACKER_OBJECTS[tobj].COORDS, TRACKER_OBJECTS[tobj].ID])

    curr_trackers = np.array(curr_trackers)
    
    ignore_new_detections = True if len(TRACKER_OBJECTS) == TRACKER_LIMIT else False

    if len(curr_trackers) > 0 and len(curr_detections) > 0:
        match_idx, new_detection_idx, empty_trackers_idx = assign_trackers(curr_trackers, curr_detections)
        print("new detections", new_detection_idx)
        print("matched", match_idx)
        print("empty trackers", empty_trackers_idx)
    else:
        new_detection_idx, empty_trackers_idx = assign_unmatched(curr_trackers, curr_detections)
        print("new detections", new_detection_idx)
        print("empty trackers", empty_trackers_idx)

    for match in match_idx:
        update_tracker(match, curr_detections, curr_trackers, frame_size)

    if ignore_new_detections == False:
        for idxD in new_detection_idx:
            success = create_tracker(idxD, curr_detections, frame_size)
            if success == False: break

    for idxT in empty_trackers_idx:
        manage_empty_tracker(idxT, curr_trackers)

    print(TRACKER_OBJECTS)
    return active_trackers()
    