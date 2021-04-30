import time
import cv2

class cv_VideoRead:
    def __init__(self,path):
        self.path = path        #path of camera source
        self.cap=None           #cv2 capture object variable 
        self.ok = False         #bool to check if frame is read
        self.stopped=False      #bool to stop running due to frame read failures
        self.tries = 0          #number of retries to grab frame
        self.running = False    #bool for main script while loop, run while True

    def start(self):
        self.cap = cv2.VideoCapture(self.path)
        self.running = True if self.cap.isOpened() else False

    def stop(self):
        if self.stopped:
            print ("[ERROR] Video device could not be read.")
            self.running = False

    def get(self):
        while(True):
            if self.running:
                self.ok, self.grab = self.cap.read()
                self.tries = 0
                self.ok = False
                return self.grab
            else:
                self.tries += 1
                self.cap = self.start()
                print("[MESSAGE] Frame could not be grabbed. Retrying... ({})".format(str(self.tries)))
                if not self.running:
                    self.stop()
            
            if self.tries > 15:
                self.stopped = True
                self.stop()


def set_input_feed(source):
    stream=cv_VideoRead(source)
    return stream