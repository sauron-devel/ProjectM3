import json
import cv2
import numpy as np

def main():

    people = {}
    loi = 360
    counter = 0
    frameData = []


    cap = cv2.VideoCapture(0)



    with open("ai-out", "r") as FIFO_IN:

        #MAYBE MAKE THIS TO BE EQUAL TO write_data(tracked_detections) FROM YOUR MAIN
        line = FIFO_IN.read()
        listPeople = json.loads(line[29:])

    #Calculates the count of people who passed the line
        num = []
        for person in listPeople:
            ID = person[5]
            num.append(ID)
            if ID not in people.keys():
                people[ID] = {
                    'initCounter':1,
                    'disCounter':0,
                    'currentInitCounter':1,
                    'currentDisCounter':1
                }
            else:
                people[ID]['initCounter']+=1
                people[ID]['currentInitCounter']+=1

            x = (person[2]+person[0])/2
            y = (person[3]+person[1])/2
            people[ID]['x'] = x
            people[ID]['y'] = y
            
        for p in list(people):

                if people[p]['initCounter']>=3:

                    if people[p]['initCounter']==3:
                        if people[p]['x']-loi<0:
                            people[p]['initialPos'] = False #Left
                        else:
                            people[p]['initialPos'] = True #Right

                    if (people[p]['x']-loi)<0:
                        people[p]['right'] = False #Left
                    else:
                        people[p]['right'] = True #Right

                    
                        
                    if p in num:
                        people[p]['disCounter']=0

                    if p not in num and people[p]['disCounter']==0:
                        people[p]['disCounter']+=1
                        people[p]['currentDisCounter'] = people[p]['initCounter']

                    elif p not in num and people[p]['currentDisCounter']==people[p]['initCounter']:
                        people[p]['disCounter']+=1
                        people[p]['currentDistCounter'] = people[p]['initCounter']

                elif p not in num:
                    print(people[p]['currentInitCounter'])
                    people[p]['currentInitCounter']-=1

                if people[p]['initCounter'] != people[p]['currentInitCounter']:
                    del(people[p])
                elif people[p]['disCounter']>=4:
                    if not people[p]['initialPos'] and people[p]['right']:
                        counter+=1
                    elif people[p]['initialPos'] and not people[p]['right']:
                        counter-=1
                    del(people[p])


        #The part of the code that adds the line and the counter on the frame
        ret, frame = cap.read()
        width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        cv2.line(frame, (loi, 0),(loi,int(height)),(0,0,255),5)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame,str(counter), 
            (30,30), 
            font, 
            1,
            (255,255,255),
            1)
        cv2.imshow('frame', frame)


if __name__ =='__main__':
    main()
