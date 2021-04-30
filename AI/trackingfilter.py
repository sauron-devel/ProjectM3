import numpy as np
from filterpy.common import Q_discrete_white_noise
from numpy.testing._private.utils import measure
from scipy import linalg

SUCCESS_THRES_DEFAULT = 5
FAIL_THRES_DEFAULT = 2
TRACKER_LIMIT = 100

class PredictionFilter():
    def __init__(self):
        #~ Tracking ID
        self.ID = None

        #~ Tracked box coordinates
        self.COORDS = []
        
        #~ Information about the tracked box (from detection)
        self.CLASS_ID = 0

        #~ OK: Number of consecutive matched runs, EMPTY: Number of consecutive unmatched runs
        #~ Making the fail and success thres specific to the tracker 
        self.SUCCESS_THRES = SUCCESS_THRES_DEFAULT #how many times the tracker has to succeed to appear 4-6 range
        self.FAIL_THRES = FAIL_THRES_DEFAULT #how many times the tracker can miss without losing 1-3 range

        self.OK = 0
        self.EMPTY = 0

        #~ Kalman filter calculation parameters 
        #  (state = input measurement state, dt = time interval)
        self.X = [] #~ State vector X*
        self.Z = [] #~ Measurement vector Z*

        self.dt = 0.05

        #~ State transition matrix F initialisation
        #  This is used to update covariance and measurement matrices based on 
        #  elapsed time. The time derivative only calculated for position
        # as this is a constant velocity model. (assume negligible acceleration)
        self.F = np.identity(8)
        for i in range(4):
            self.F[i,i+4] = self.dt

        # STATE TRANSITION MATRIX:  --is used during tracking
        # [1,  0,  0,  0,  dt,  0,  0, 0 ]
        # [0,  1,  0,  0,  0,  dt, 0,  0 ]
        # [0,  0,  1,  0,  0,  0,  dt, 0 ]
        # [0,  0,  0,  1,  0,  0,  0,  dt]
        # [0,  0,  0,  0,  1,  0,  0,  0 ]
        # [0,  0,  0,  0,  0,  1,  0,  0 ]
        # [0,  0,  0,  0,  0,  0,  1,  0 ]
        # [0,  0,  0,  0,  0,  0,  0,  1 ]

        #~ Process covariance matrix Q, models the noise behaviour of the system (error)
        #  Note this is a covariance matrix hence symmetric positive-demidefinite
        #  Base assumption: Noise is modeled as a discrete wiener process over time,
        #  Hence, noise is assumed as Gaussian and random, on average constant over time

        # Possible to do live velocity mapping, check accuracy of movement bbox maps
        # Note- is noise in det vs track independent? when more people, need more precision
        self.noise_var1 = 0.01
        self.noise_var2 = 0.1
        self.noise1 = Q_discrete_white_noise(dim=2, dt=self.dt, var=self.noise_var1)
        self.noise2 = Q_discrete_white_noise(dim=2, dt=self.dt, var=self.noise_var2)

        self.Q = linalg.block_diag(self.noise1, self.noise2, 
                                   self.noise2, self.noise1)
        
        #PROCESS NOISE COVARIANCE MATRIX --is manipulated during tracking

        # [0.01 0.01.0.   0.   0.   0.   0.   0.   ]
        # [0.01 0.01.0.   0.   0.   0.   0.   0.   ]
        # [0.   0.   0.01 0.01 0.   0.   0.   0.   ]
        # [0.   0.   0.01 0.01.0.   0.   0.   0.   ]
        # [0.   0.   0.   0.   0.01.0.01.0.   0.   ]
        # [0.   0.   0.   0.   0.01.0.01.0.   0.   ]
        # [0.   0.   0.   0.   0.   0.   0.01.0.01.]
        # [0.   0.   0.   0.   0.   0.   0.01.0.01.]

        #~ Process (uncertainty) state covariance matrix P
        # This is initialised at a relatively small value (e.g. 10) and will grow to variance
        # in state (position) estimations with error measurements of bounding boxes, using the
        # Q matrix.

        self.uncertainty = 10.0
        self.P  = np.diag(self.uncertainty*np.ones(8))

        # PROCESS STATE COVARIANCE MATRIX --is manipulated during tracking
        # [10,  0,  0,  0,  0,  0,  0,  0 ]
        # [0,  10,  0,  0,  0,  0,  0,  0 ]
        # [0,  0,  10,  0,  0,  0,  0,  0 ]
        # [0,  0,  0,  10,  0,  0,  0,  0 ]
        # [0,  0,  0,  0,  10,  0,  0,  0 ]
        # [0,  0,  0,  0,  0,  10,  0,  0 ]
        # [0,  0,  0,  0,  0,  0,  10,  0 ]
        # [0,  0,  0,  0,  0,  0,  0,  10 ]

        #~ Measurement matrix H, helper matrix for matrix calculations
        # This matrix helps transform the format of matrix P such that it can be evaluated
        # for matrix K (later shown), the Kalman gain, and is dependent on our input vector 
        # dimensions, x=8 (cols) and y=4 (rows)

        self.H = np.concatenate([np.identity(4),np.zeros([4,4])], axis=1)
        
        # MEASUREMENT MATRIX --is initialised on measurement
        # [1, 0, 0, 0, 0, 0, 0, 0]
        # [0, 1, 0, 0, 0, 0, 0, 0]
        # [0, 0, 1, 0, 0, 0, 0, 0]
        # [0, 0, 0, 1, 0, 0, 0, 0]

        #~ Measurement noise matrix R, works out the noise from input on measurement
        # This can also be seen as the deviation in a still bounding box over time
        # which can be modelled as measurement noise, we can assume this is closer
        # to about 1 pixel for highly accurate models, up to 10-20 pixels for weaker
        # models with minor detection fluctuations. I'll start with 1.

        self.meas_noise = 1e-3
        self.R = np.diag(self.meas_noise*np.ones(4))

        # MEASUREMENT NOISE MATRIX --can be updated on measurement
        # [1, 0, 0, 0]
        # [0, 1, 0, 0]
        # [0, 0, 1, 0]
        # [0, 0, 0, 1]

        #~ *Measurement vector Z: This is initialised when an object is detected,
        #  and utiises only the measurement coordinates, as velocity is not known
        #  on first pass. 
        
        #  MEASUREMENT VECTOR Z: [cx, cy, w, h]

        #~ *Measurement vector X: This is adjusted at each step, and is synchronised
        #~ with detections.
        #  This is defined as the position and velocity constants at each step, for a
        #  constant velocity vector. Velocities are initialised as 0 each time.
        
        #  MEASUREMENT VECTOR X: [cx, cy, w, h, v1(0), v2(0), v3(0), v4(0)]
        
    #*{...CHECK IF THIS FUNCTION IS DOING THE RIGHT THING}
    def update_id(self, TRACKER_OBJECTS):
        #~ IDs range from 0 to 99, == keys in TRACKER_OBJECTS, assign
        #~ new IDs by free values in this range, prioritising smallest.
        
        # If there is nothing in TRACKER_OBJECTS, this ID will be 0
        if len(TRACKER_OBJECTS) == TRACKER_LIMIT:
            self.ID = None
        if len(TRACKER_OBJECTS) == 0: 
            self.ID = 0 
        else: 
            # then the current ID is the highest ID + 1 (will be unused)
            self.ID = max(TRACKER_OBJECTS.keys()) + 1       

        return self.ID

    def initialise_state_vector_X(self, bbox):
        #~ Assume a constant velocity model and initialise with v=0
        #~ Convert bbox state to Kalman filter state: [x1,y1,x2,y2...

        position_state = [bbox[0], bbox[1], bbox[2], bbox[3]]
        #~ And add the velocity states, initialised as 0, auto-estimated on each step
        velocity_state = [0,0,0,0]
        #~Return as a numpy array for matrix calculations: (column vector format)
        state_vector = np.array(position_state + velocity_state)
        state_vector = np.expand_dims(state_vector, axis = 0)
        state_vector = state_vector.T

        self.X = state_vector

    def initialise_meas_vector_Z(self, bbox):
        #~ The measurement vector has the initial state, this is static and hence
        #~ velocity is not added to the vector.

        #~Return as a numpy array for matrix calculations: (column vector format)
        msr_vector = np.array([bbox[0], bbox[1], bbox[2], bbox[3]])
        msr_vector = np.expand_dims(msr_vector, axis=0)
        msr_vector = msr_vector.T 

        self.Z = msr_vector

    def KF_predict_and_track(self):

        #~ Predict next time step: Deriving state predictions using the state transition matrix

        # X(t) = F.X(t-1)
        X_pred = np.dot(self.F, self.X)

        # P(t) = F.P(t-1).F^T
        P_pred = np.dot(self.F, self.P).dot(self.F.T) + self.Q

        # Update current stage:

        #~ Kalman gain (K): Essentially calculating error in estimate vs error in the
        #~ measurement, putting more weight on the smaller error 
        
        # K = (P(t).H^T) / (H.P.H^T + R)
        K_gain = np.dot(P_pred,self.H.T).dot(linalg.inv(np.dot(self.H,P_pred).dot(self.H.T) + self.R))
        
        #~ Performing X state updating, predicted X value gets filtered by actual measurement
        #~ subtracted with predicted X, and added to existing value to get updated X value.
        #~ And updating process covariance matrix. 

        # X(t) = X(t) + K.(Z(t) - H.X(t))
        self.X = (X_pred + np.dot(K_gain,(self.Z - np.dot(self.H,X_pred)))).astype(int)
        
        # P(t) = (K.H).P(t)
        self.P = -(np.dot(K_gain, self.H)).dot(self.P)

        #Then, X(t-1) = X(t) and P(t-1) = P(t) and the system can be re-evaluated

    def KF_predict(self):
        #~ Predict next time step: Deriving state predictions using the state transition matrix
        # We only run prediction when the previous state is unknown

        X_pred = np.dot(self.F, self.X)
        P_pred = np.dot(self.F, self.P).dot(self.F.T) + self.Q

        self.X = X_pred.astype(int)
        self.P = P_pred










        

