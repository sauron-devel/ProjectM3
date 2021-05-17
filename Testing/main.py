import os
import json
import time
import logging
from logEntryCreate import logEntryCreate
import base64
from errorDetection import crcCheck
from errorDetection import crcRemainder

dataInt = [0 for i in range(8)]
dataStr = [0 for i in range(4)]
dataBool = [0 for i in range(8)]
logLevel = 0
logging.basicConfig(filename = 'log.txt', filemode = 'a', format = '%(asctime)s - %(levelname)s - %(message)s')

#CONTINOUS READING OF JSON FILE AND TESTING
while 1:    
    errorFound = 0
    try:
        jsonFile1 = open('config.json')
    except:
        logEntryCreate('config.json', 0, 0)
        errorFound = 1

    try:
        jsonFile2 = open('FrontToBack.json')
    except:
        logEntryCreate('FrontToBack.json', 0, 0)
        errorFound = 1 

    try:
        jsonFile3 = open('BackToFront.json')
    except:
        logEntryCreate('BackToFront.json', 0, 0)
        errorFound = 1 
    
    try:
        jsonFile4 = open("LoRatoBack.json")
    except:
        logEntryCreate('LoRatoBack.json', 0, 0)
        errorFound = 1
    #
    try:
        rawData1 = json.load(jsonFile1)
    except:
        logEntryCreate('config.json', 0, 1)
        errorFound = 1
        
    try:
        rawData2 = json.load(jsonFile2)
    except:
        logEntryCreate('FrontToBack.json', 0, 1)
        errorFound = 1 

    try:
        rawData3 = json.load(jsonFile3)
    except:
        logEntryCreate('BackToFront.json', 0, 1)
        errorFound = 1 
    
    try:
        rawData4 = json.load(jsonFile4)
    except:
        logEntryCreate('LoRatoBack.json', 0, 1)
        errorFound = 1 



    #Loading data into variables

    dataList = []
    for i in rawData1['camSetup']:
        dataList.append(rawData1['camSetup'][i])
    
    dataInt[0] = rawData1['system']['startVal']
    dataStr[0] = rawData1['system']['imgPath']

    dataInt[1] = rawData1['devices']['cameras']
    dataInt[2] = rawData1['devices']['sensors']
    dataDict = rawData1['devices']['deviceInfo']

    dataBool[0] = rawData2['errorFlag']
    dataBool[1] = rawData2['programStop']
    dataBool[2] = rawData2['configChanged']

    dataInt[3] = rawData2['diagnostics']['deviceCheckID']
    dataStr[1] = rawData2['diagnostics']['requestedAt']
    dataBool[3] = rawData2['diagnostics']['responseRecv']

    dataBool[4] = rawData2['saveData']['enable']
    dataInt[4] = rawData2['saveData']['timeSaved']

    dataBool[5] = rawData3['errorFlag']

    dataInt[5] = rawData3['tally']['incr']
    dataInt[6] = rawData3['tally']['decr']

    dataBool[6] = rawData3['diagnostics']['checkRecv']
    dataStr[2] = rawData3['diagnostics']['response']
    dataStr[3] = rawData3['diagnostics']['respondedAt']

    dataBool[7] = rawData3['powerSys']['battery']
    dataInt[7] = rawData3['powerSys']['percentage']

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

    if os.path.exists(dataStr[0]) == False:
        logEntryCreate(dataStr[0], 0, 8)
        logLevel = 1

    # LORA ERROR DETECTION
    divisor = []
    divisorStr = ""
    rawDataStr = ""

    base64Message = rawData4["payload_raw"]
    base64Bytes = base64Message.encode('utf-8')
    rawDataBytes = base64.decodebytes(base64Bytes)
    rawData = list("".join(["{:08b}".format(x) for x in rawDataBytes]))

    if rawData4["metadata"]["coding_rate"] == "4/5":
        ammountOfRedun = int(len(rawData)/5)
        startOfDiv = len(rawData) - ammountOfRedun 
        for i in range(startOfDiv, len(rawData)):
            divisor.append(rawData[i])

    for i in range(0, startOfDiv):
        rawDataStr += rawData[i]

    for i in divisor:
        divisorStr += i

    if crcCheck(rawDataStr, divisorStr, '0') == False:
        logEntryCreate(crcRemainder(rawDataStr, divisorStr, '0'), 0, 9)

    jsonFile1.close()
    jsonFile2.close()
    jsonFile3.close()
    jsonFile4.close()
    time.sleep(0.5) 

    #Refresh and clean the log file
    if not logLevel == 0:
        with open("log.txt", "w") as logFile:
            logFile.truncate(0)