import numpy as np
import tensorflow.compat.v1 as tf

DET_SCORE_THRES = 0.2

class InitModel:
    def __init__(self, INF_GRAPH, LABELMAP):
        #~ GPU configuration for inference; attempting to emulate 4 thread (2 core) device
        self.config = tf.ConfigProto()
        self.config.gpu_options.allow_growth = True
        #self.config.log_device_placement = True
        #~ Store inference graph and labelmap paths for loading graph and label dictionary
        self.INF_GRAPH = INF_GRAPH
        self.LABELMAP = LABELMAP


    #~ Parse the labelmap file and convert to a dict {key: (int)class_ID; content: (string)label}
    def load_labels(self):
        labels = {}
        with open(self.LABELMAP, "r") as fp:
            for line in fp:
                    if 'id' in line:
                        class_id = int(line.replace("id: ","").replace("\n","").strip(" "))
                    if 'display_name' in line:
                        displayname = "TYPE:" + str(line.replace("display_name: ","").replace("\n","").strip(" "))
                        labels[class_id] = displayname

        return labels

    #~ Import the graph by serialising the binary .pb file with tensorflow functions
    def graph_import(self):
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(self.INF_GRAPH, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.sess = tf.Session(graph=detection_graph, config=self.config)
        return self.sess, detection_graph




def model_inference(sess, image_np, graph, labels):
    image_np_expanded = np.expand_dims(image_np, axis=0)

    image_tensor = graph.get_tensor_by_name('image_tensor:0')
    boxes = graph.get_tensor_by_name('detection_boxes:0')
    scores = graph.get_tensor_by_name('detection_scores:0')
    classes = graph.get_tensor_by_name('detection_classes:0')
    num_detections = graph.get_tensor_by_name('num_detections:0')
    (boxes, scores, classes, num_detections) = sess.run([boxes, scores, classes, num_detections],feed_dict={image_tensor: image_np_expanded})

    detections = []
    for i in range(len(classes[0])):
        if scores[0][i] > DET_SCORE_THRES:
            if classes[0][i].astype(int) == 1:
                #~ Load label string for the detection
                label = str(labels[classes[0][i].astype(int)])
                #~ Un-normalising box coordinates to map to correct frame pixel dims
                box_ux = int(boxes[0][i][1]*image_np.shape[1])
                box_uy = int(boxes[0][i][0]*image_np.shape[0])
                box_bx = int(boxes[0][i][3]*image_np.shape[1])
                box_by = int(boxes[0][i][2]*image_np.shape[0])
                
                coords = [box_ux,box_uy,box_bx,box_by,classes[0][i].astype(int)]

                try: detections.append(coords) 
                except: pass

    return np.array(detections).astype(int)


