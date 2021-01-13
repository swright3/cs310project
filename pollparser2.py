from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

def getHTML(link):
    source = requests.get(link).text
    soup = BeautifulSoup(source,'lxml')
    return soup

def getTable(soup):
    table = soup.find('div', class_='polltable').find('table')
    return table

def tableToArray(table):
    rows = table.find_all('tr')
    headers = rows[0].find_all('td')
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

def pollsToCSV(source):
    soup = getHTML(source)
    table = getTable(soup)
    tableArray = []
    headers, data = tableToArray(table)
    df = pd.DataFrame(data,columns=headers)
    df.to_csv("pastresults.csv")
