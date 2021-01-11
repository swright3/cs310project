from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

def getHTML(link):
    source = requests.get(link).text
    soup = BeautifulSoup(source,'lxml')
    return soup

def getTables(soup,limit):
    tables = soup.find_all('table', class_='wikitable sortable')
    tables = tables[:limit]
    for table in range(len(tables)):
        tables[table] = tables[table].tbody
    return tables

def tableToDf(table,df,first):
    rows = table.find_all('tr')
    array = []
    headers = rows[0].find_all('th')

    for header in range(len(headers)):
        headers[header] = headers[header].text.replace('\n', '')
    rows.pop(0)

    for row in rows:
        data = row.find_all('td')
        if len(data) == len(headers):
            for datum in range(len(data)):
                data[datum] = data[datum].text.replace('\n', '')
            array.append(data)

    if first == True:
        df = pd.DataFrame(array,columns=headers)
        first = False
    else:
        df.append(array)
    return df

source = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_next_United_Kingdom_general_election#2021"
soup = getHTML(source)
tables = getTables(soup,2)
df = pd.DataFrame()
first = True
for table in tables:
    df = tableToDf(table,df,first)
    first = False
print(df)
#df.to_csv("pollresults.csv")
