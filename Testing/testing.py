import json
import time
import logging

data = [0 for i in range(8)]
errorFound = False
logging.basicConfig(filename = 'log.txt', filemode = 'a', format = '%(asctime)s - %(levelname)s - %(message)s')

def errorCreate(val, place, errorCode):
    place = placeOfError(place)
    if errorCode == 1:
        logging.error("Invalid '%s' in %s value - Error with %s", val, place, str(type(val)))
        return
    if errorCode == 2:
        logging.error("Invalid Boolean Expression at the %s value", place)
        return

def placeOfError(place):
    if place == 0:
        return 'Increment Tally'
    elif place == 1:
        return 'Decrement Tally'
    elif place == 2:
        return 'Power Flag'
    elif place == 3:
        return 'Increment Power Percentage'
    elif place == 4:
        return 'Decrement Power Percentage'
    elif place == 5:
        return 'Camera Request'
    elif place == 6:
        return 'Image Storage Request'
    elif place == 7:
        return 'Other Request'


#CONTINOUS READING OF JSON FILE AND TESTING
while 1:
    jsonFile1 = open('output.json')
    jsonFile2 = open('config.json')
    jsonFile3 = open('input.json')
    rawData1 = json.load(jsonFile1)
    rawData2 = json.load(jsonFile2) 
    rawData3 = json.load(jsonFile3)
    errorFound = False
    #Loading data into variable

    for i in rawData1['tally']:
        data[0] = i['incr']
        data[1] = i['decr']

    for i in rawData1['battery']:
        data[2] = i['powerFlag']
        data[3] = i['percentIncr']
        data[4] = i['percentDecr']

    for i in rawData1['diagRequest']:
        data[5] = i['camera']
        data[6] = i['imagStor']
        data[7] = i['other']

    #Testing
    listIncr = 0
    for i in data: 
        if not type(i) == int:
            errorCreate(i, listIncr, 1)
            errorFound = True

        if not ((i == 1) or (i == 0)):
            errorCreate(i, listIncr, 2)
            errorFound = True
        listIncr += 1

    jsonFile1.close()
    jsonFile2.close()
    jsonFile3.close()
    time.sleep(0.5) 

    #Refresh and clean the log file
    if errorFound == True:
        with open("log.txt", "w") as logFile:
            logFile.truncate(0)

