import logging

def logEntryCreate(val, placeNum, logCode):
    place = placeOfLog(placeNum, logCode)
    if logCode == 0:
        logging.critical("%s file failed to open, may not exist", val)
    if logCode == 1:
        logging.critical("%s file failed to load, not a python dictionary", val)
    if logCode == 2:
        logging.error("'%s' in %s value, should be a <class 'int'> is actually %s", val, place, str(type(val)))
    if logCode == 3:
        logging.error("'%s' in %s value, should be a <class 'bool'> is actually %s", val, place, str(type(val)))
    if logCode == 4:
        logging.error("'%s' in %s value, should be a <class 'str'> is actually %s", val, place, str(type(val)))
    if logCode == 5:
        logging.error("'%s' in %s value, should be a <class 'list'> is actually %s", val, place, str(type(val)))
    if logCode == 6:
        logging.error("'%s' in %s value, isn't a correct (x,y) coordinate", val, place)
    if logCode == 7:
        logging.error("'%s' in %s value, value in the (x,y) corrdinate is not <class 'int'> is actually %s", val, place, str(type(val)))
    if logCode == 8:
        logging.error("File path '%s' does not exist", val)
    if logCode == 9:
        logging.error("Data corrupted from LoRa Board, error value %s", val) 
    return

def placeOfLog(placeNum, logCode):
    if logCode == 2:    
        if placeNum == 0:
            return 'startVal'
        elif placeNum == 1:
            return 'cameras'
        elif placeNum == 2:
            return 'sensors'
        elif placeNum == 3:
            return 'deviceCheckID'
        elif placeNum == 4:
            return 'timeSaved'
        elif placeNum == 5:
            return 'Incr'
        elif placeNum == 6:
            return 'Decr'
        elif placeNum == 7:
            return 'Percentage'
    elif logCode == 3:
        if placeNum == 0:
            return 'errorFlag'
        elif placeNum == 1:
            return 'programStop'
        elif placeNum == 2:
            return 'configChanged'
        elif placeNum == 3:
            return 'responseRecv'
        elif placeNum == 4:
            return 'enable'
        elif placeNum == 5:
            return 'errorFlag'
        elif placeNum == 6:
            return 'checkRecv'
        elif placeNum == 7:
            return 'battery'
    elif logCode == 4:
        if placeNum == 0:
            return 'imgPath'
        elif placeNum == 1:
            return 'requestedAt'
        elif placeNum == 2:
            return 'response'
        elif placeNum == 3:
            return 'respondedAt'
    elif (logCode == 5) or (logCode == 6) or (logCode == 7):
        if placeNum == 0:
            return 'lineP1'
        elif placeNum == 1:
            return 'lineP2'
        elif placeNum == 2:
            return 'ignoreP1'
        elif placeNum == 3:
            return 'ignoreP2'
    else:
        return