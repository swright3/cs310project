import chardet
with open('training.1600000.processed.noemoticon.csv', 'rb') as rawdata:
    result = chardet.detect(rawdata.read(500000))
print(result)