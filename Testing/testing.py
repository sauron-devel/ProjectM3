import json

#INITAL SETUP OF JSON FILE

data={}
data['tally'] = []
data['battery']=[]
data['diagRequest']=[]

data['tally'].append({
    'incr': 0,
    'decr': 0
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

with open('dataflow.txt', 'w') as jsonFile:
    json.dump(data, jsonFile)

jsonFile.close()

#CONTINOUS READING OF JSON FILE AND TESTING
while 1:
    with open('dataflow.txt') as jsonFile:
        data = json.load(jsonFile)
        

    for i in data['tally']:
        tempIncr = i['incr']
        tempDecr = i['decr']

    test = isinstance(tempIncr, str)
    print('String? ' + str(test))

    jsonFile.close()




