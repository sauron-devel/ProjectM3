#INITAL SETUP OF JSON FILE
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

with open('dataflow.json', 'w') as jsonFile:
    json.dump(data, jsonFile)

jsonFile.close()