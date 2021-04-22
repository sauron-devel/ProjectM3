import json
import time
import logging

dataList = [0 for i in range(4)]
dataInt = [0 for i in range(8)]
dataStr = [0 for i in range(4)]
dataBool = [0 for i in range(7)]
errorFound = False
logging.basicConfig(filename = 'log.txt', filemode = 'a', format = '%(asctime)s - %(levelname)s - %(message)s')

def errorCreate(val, place, errorCode):
    place = placeOfError(place, errorCode)
    if errorCode == 1:
        logging.error("'%s' in %s value, should be a <class 'int'>, is actually %s", val, place, str(type(val)))
        return
    if errorCode == 2:
        logging.error("'%s' in %s value, should be a <class 'bool'>, is actually %s", val, place, str(type(val)))
        return

def placeOfError(place, errorCode):
    if errorCode == 1:    
        if place == 0:
            return 'startVal'
        elif place == 1:
            return 'cameras'
        elif place == 2:
            return 'sensors'
        elif place == 3:
            return 'deviceCheckID'
        elif place == 4:
            return 'timeSaved'
        elif place == 5:
            return 'Incr'
        elif place == 6:
            return 'Decr'
        elif place == 7:
            return 'Percentage'


#CONTINOUS READING OF JSON FILE AND TESTING
while 1:
    jsonFile1 = open('config.json')
    jsonFile2 = open('FrontToBack.json')
    jsonFile3 = open('BackToFront.json')
    rawData1 = json.load(jsonFile1)
    rawData2 = json.load(jsonFile2) 
    rawData3 = json.load(jsonFile3)
    errorFound = False

    #Loading data into variables

    for i in rawData1['camSetup']:
        dataList[0] = i['lineP1']
        dataList[1] = i['lineP2']
        dataList[2] = i['ignoreP1']
        dataList[3] = i['ignoreP2']

    for i in rawData1['system']:
        dataInt[0] = i['startVal']
        dataStr[0] = i['imgPath']

    for i in rawData1['devices']:
        dataInt[1] = i['cameras']
        dataInt[2] = i['sensors']
        dataDict = i['deviceInfo']

    dataBool[0] = rawData2['errorFlag']
    dataBool[1] = rawData2['programStop']
    dataBool[2] = rawData2['configChanged']

    for i in rawData2['diagnostics']:
        dataInt[3] = i['deviceCheckID']
        dataStr[1] = i['requestedAt']
        dataBool[3] = i['responseRecv']

    for i in rawData2['saveData']:
        dataBool[4] = i['enable']
        dataInt[4] = i['timeSaved']

    dataBool[5] = rawData3['errorFlag']

    for i in rawData3['tally']:
        dataInt[5] = i['incr']
        dataInt[6] = i['decr']

    for i in rawData3['diagnostics']:
        dataBool[5] = i['checkRecv']
        dataStr[2] = i['response']
        dataStr[3] = i['respondedAt']

    for i in rawData3['powerSys']:
        dataBool[6] = i['battery']
        dataInt[7] = i['percentage']


    #Testing
    
    listIncr = 0
    for i in dataInt: 
        if not type(i) == int:
            errorCreate(i, listIncr, 1)
            errorFound = True
        listIncr += 1

    listIncr = 0
    for i in dataBool:
        if not type(i) == bool:
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

