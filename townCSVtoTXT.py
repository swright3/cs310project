import pandas as pd

#ONE TIME USE SCRIPT TO CONVERT THE UK PLACES CSV INTO A FORMATTED TEXT FILE

df = pd.read_csv('Towns_List.csv')
places = []
for place in df.itertuples(index=False):
    places.append(place.Town.replace('?','').replace("'","").replace(',',''))
    places.append(place.County.replace('?','').replace("'","").replace(',',''))
    places.append(place.Country.replace('?','').replace("'","").replace(',',''))

df = pd.read_csv('territory-names.csv')
for place in df.itertuples(index=False):
    places.append(place.Name.replace('?','').replace("'","").replace(',',''))
    places.append(place.OfficialName.replace('?','').replace("'","").replace(',',''))

places.append('united kingdom')
places.append('britain')
places.append('none')
places.append('deleted')
places = list(set(places))
placesString = ''
for place in places:
    placesString += place.lower() + ' OR '
with open('formattedPlaces.txt','w') as f:
    f.write(placesString[:-4])