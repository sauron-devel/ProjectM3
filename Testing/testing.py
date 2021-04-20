import json

data={}
data['tally'] = []
data['battery']=[]
data['diagRequest']=[]

data['tally'].append({
    'incr': str(0),
    'decr': str(0)
})
data['battery'].append({
    'powerFlag': str(1),
    'percentIncr': str(0),
    'percentDecr': str(0),
})
data['diagRequest'].append({
    'camera': str(1),
    'imagStor': str(0),
    'other': str(0),
})

with open('dataflow.txt', 'w') as outfile:
    json.dump(data, outfile)


with open('dataflow.txt') as json_file:
    data = json.load(json_file)
    for i in data['tally']:
        print('Increment Value: ' + i['incr'])
        print('Decrement Value: ' + i['decr'])
        print('')

