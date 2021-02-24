from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

def getHTML(link):
    source = requests.get(link).text
    soup = BeautifulSoup(source,'lxml')
    return soup

def getTable(soup):
    table = soup.find('table', class_='wikitable sortable')
    return table

def getMPs(table):
    rows = table.find_all('tr')
    rows.pop(0)
    mps = []
    for row in rows:
        columns = row.find_all('td')
        if len(columns) == 7:
            #print(columns[3].text, columns[5].text)
            if columns[5].text.rstrip() == "Conservative":
                mps.append([columns[3].text.strip(),"Conservative"])
            elif columns[5].text.rstrip() == "Labour" or columns[-2].text.rstrip() == "Labour Co-operative":
                mps.append([columns[3].text.strip(),"Labour"])
            elif columns[5].text.rstrip() == "Liberal Democrats":
                mps.append([columns[3].text.strip(),"Lib Dem"])
            elif columns[5].text.rstrip() == "Green":
                mps.append([columns[3].text.strip(),"Green"])
    print(mps)

source = getHTML("https://en.wikipedia.org/wiki/List_of_MPs_elected_in_the_2019_United_Kingdom_general_election")
table = getTable(source)
getMPs(table)