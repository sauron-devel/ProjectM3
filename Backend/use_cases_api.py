import json

def read_data_from_AI():
    #Creating a dictionary to store people data
    people = {}

    loi = 350
    counter = 0
    frameData = []
    #Format of data: YYYY-MM-DD HH:MM:SS.000000>> [[x1, y1, x2, y2, class ID, tracking ID]]

    # while(True):
    #     with open("ai-out", "r") as FIFO_IN:
    #         for i in range(5):
    #             string.append(FIFO_IN.read())

    line =0
    with open('sampleoutput.txt', 'r') as test:
        for r in test:
            frameData.append(r)
    
    for p in frameData:
        line+=1
        print("This is line number: "+ str(line))
        listPeople = json.loads(p[29:])
    #Updating the data for the people currently on the frame

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


        for x in people:
            print(x)
            print(people[x])
    print(counter)

if __name__ =='__main__':
    read_data_from_AI()
