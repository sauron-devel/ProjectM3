#INITAL SETUP OF JSON FILE

#The dictionary setup
data = {}
data['tally'] = []
data['battery'] = []
data['diagRequest'] = []

data['tally'].append({
    'incr': 0,
    'decr': 0,
})

data['battery'].append({
    'powerFlag': 1,
    'percentIncr': 0,
    'percentDecr': 0,
})

data['diagRequest'].append({
    'camera': 1,
    'imagStor': 0,
    'other': 0,
})

#Sending the dictionary to the json file
with open('dataflow.json', 'w') as jsonFile:
    json.dump(data, jsonFile)

jsonFile.close()