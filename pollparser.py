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

def tableToArray(table):
    rows = table.find_all('tr')
    headers = rows[0].find_all('th')
    array = []

    for header in range(len(headers)):
        headers[header] = headers[header].text.replace('\n', '')
    rows.pop(0)

    for row in rows:
        data = row.find_all('td')
        if len(data) == len(headers):
            for datum in range(len(data)):
                data[datum] = data[datum].text.replace('\n', '')
            array.append(data)
    return headers, array

source = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_next_United_Kingdom_general_election#2021"
soup = getHTML(source)
tables = getTables(soup,2)
first = True
tableArray = []
for table in tables:
    headers, data = tableToArray(table)
    tableArray = tableArray + data
df = pd.DataFrame(tableArray,columns=headers)
df.to_csv("pollresults.csv")
