from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd
import numpy as np

def getHTML(link):
    source = requests.get(link).text
    soup = BeautifulSoup(source,'lxml')
    return soup

def getTables(soup,number)
    tables = soup.find_all('table', class_='wikitable sortable')
    tables = tables[:number]
    for table in len(tables):
        tables[table] = tables[table].tbody
    return tables


rows = table.find_all('tr')

#csvfile = open('pollresults.csv','w',newline='')
#csvwriter = csv.writer(csvfile)

array = []

headers = rows[0].find_all('th')
for header in range(len(headers)):
    headers[header] = headers[header].text.replace('\n', '')
rows.pop(0)
#csvwriter.writerow(headers)

for row in rows:
    data = row.find_all('td')
    print(len(data),len(headers))
    if len(data) == len(headers):
        for datum in range(len(data)):
            data[datum] = data[datum].text.replace('\n', '')
        #csvwriter.writerow(data)
        array.append(data)

df = pd.DataFrame(array,columns=headers)
df.to_csv("pollresults.csv")
#csvfile.close()
