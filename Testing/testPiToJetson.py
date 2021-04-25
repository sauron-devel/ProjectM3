import json
import time
import logging
from logEntryCreate import logEntryCreate

dataList = [0 for i in range(4)]
dataInt = [0 for i in range(8)]
dataStr = [0 for i in range(4)]
dataBool = [0 for i in range(8)]
logLevel = 0
logging.basicConfig(filename = 'log.txt', filemode = 'a', format = '%(asctime)s - %(levelname)s - %(message)s')

#CONTINOUS READING OF JSON FILE AND TESTING
while 1:
    try:
        jsonFile1 = open('config.json')
    except:
        logEntryCreate('config.json', 0, 0)

    try:
        jsonFile2 = open('FrontToBack.json')
    except:
        logEntryCreate('FrontToBack.json', 0, 0) 

    try:
        jsonFile3 = open('BackToFront.json')
    except:
        logEntryCreate('BackToFront.json', 0, 0) 
    
    try:
        rawData1 = json.load(jsonFile1)
    except:
        logEntryCreate('config.json', 0, 1)
        
    try:
        rawData2 = json.load(jsonFile2)
    except:
        logEntryCreate('FrontToBack.json', 0, 1) 

    try:
        rawData3 = json.load(jsonFile3)
    except:
        logEntryCreate('BackToFront.json', 0, 1) 

    errorFound = 0

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
        dataBool[6] = i['checkRecv']
        dataStr[2] = i['response']
        dataStr[3] = i['respondedAt']

    for i in rawData3['powerSys']:
        dataBool[7] = i['battery']
        dataInt[7] = i['percentage']

    #Testing
    
    listIncr = 0
    for i in dataInt: 
        if not type(i) == int:
            logEntryCreate(i, listIncr, 2)
            logLevel = 1
        listIncr += 1

    listIncr = 0
    for i in dataBool:
        if not type(i) == bool:
            logEntryCreate(i, listIncr, 3)
            logLevel = 1
        listIncr += 1

    listIncr = 0
    for i in dataStr:
        if not type(i) == str:
            logEntryCreate(i, listIncr, 4)
            logLevel = 1
        listIncr += 1

    listIncr = 0
    for i in dataList:
        if not type(i) == list:
            logEntryCreate(i, listIncr, 5)
            logLevel = 1
        if (not len(i) == 2) & (type(i) == list):
            logEntryCreate(i, listIncr, 6)
            logLevel = 1
        if (len(i) == 2):
            for j in i:
                if not type(j) == int:
                    logEntryCreate(j, listIncr, 7)
                    logLevel = 1
        listIncr += 1
    
    jsonFile1.close()
    jsonFile2.close()
    jsonFile3.close()
    time.sleep(0.5) 

    #Refresh and clean the log file
    if not logLevel == 0:
        with open("log.txt", "w") as logFile:
            logFile.truncate(0)

