from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import sqlite3
import enum

def getHTML(link):
    source = requests.get(link).text
    soup = BeautifulSoup(source,'lxml')
    return soup

def getPre2020Table(soup):
    table = soup.find('div', class_='polltable').find('table')
    return table

def parseDate(date,year):
    dateLib = {'Jan':'1','Feb':'2','Mar':'3','Apr':'4','May':'5','Jun':'6','Jul':'7','Aug':'8','Sep':'9','Oct':'10','Nov':'11','Dec':'12'}
    dateString = str(year) + '-' + dateLib[date[-3:]] +'-'
    dateList = date.split(' ')
    if len(dateList[-2]) < 3:
        dateString += dateList[-2]
    elif dateList[-2][-2] == '–':
        dateString += dateList[-2][-1]
    elif dateList[-2][-3] == '–':
        dateString += dateList[-2][-2:]
    return dateString

def pre2020TableToArray(table):
    rows = table.find_all('tr')
    headers = rows[0].find_all('td')
    array = []

    for header in range(len(headers)):
        headers[header] = headers[header].text.replace('\n', '')
    rows.pop(0)

    for row in rows:
        data = row.find_all('td')
        if len(data) == len(headers):
            blank = 0
            for datum in range(len(data)):
                data[datum] = data[datum].text.replace('\n', '')
                if datum in [2,3,4,6] and len(data[datum].strip()) == 0:
                    blank += 1
            if data[1].strip()[:4] != '2020' and  blank == 0:  #updated to not include from 2020 or any where data is missing for a party
                array.append(data)
    return array

def pre2020PollsToDF():
    soup = getHTML('http://ukpollingreport.co.uk/voting-intention-2')
    table = getPre2020Table(soup)
    data = pre2020TableToArray(table)
    df = pd.DataFrame(data,columns=['pollster','date','con','lab','libdem','ukip','green','con lead'])
    df = df.drop(['ukip', 'con lead'],axis=1)
    return df

def getNewTable(soup,index):
    tables = soup.find_all('table', class_='wikitable sortable mw-datatable')
    table = tables[index].tbody()
    return table

def newTableToArray(rows,index):
    headers = rows[0].find_all('th')
    array = []

    for header in range(len(headers)):
        headers[header] = headers[header].text.replace('\n', '')
    rows.pop(0)

    for row in rows:
        data = row.find_all('td')
        if len(data) == len(headers):
            for datum in range(len(data)):
                if datum == 2:
                    data[datum] = parseDate(data[datum].text.replace('\n',''),2021-index)
                else:
                    data[datum] = data[datum].text.replace('\n', '').replace('%','')
            array.append(data)
    return array

def newPollsToDF(index):
    soup = getHTML('https://en.wikipedia.org/wiki/Opinion_polling_for_the_next_United_Kingdom_general_election')
    table = getNewTable(soup,index)
    data = newTableToArray(table,index)
    df = pd.DataFrame(data,columns=['pollster','client','date','area','samplesize','con','lab','libdem','snp','green','others','lead'])
    df = df.drop(['client','area','samplesize','snp','others','lead'],axis=1)
    return df

def pollsToDB(polls):
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    for index, row in polls.iterrows():
        c.execute('INSERT INTO polls (pollster,date,con,lab,libdem,green) VALUES (?,?,?,?,?,?);',(row['pollster'],row['date'],row['con'],row['lab'],row['libdem'],row['green']))
    conn.commit()
    conn.close()

def newPollsToDB():
    newPolls = newPollsToDF(0)
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    earliest2021Id = 2137
    c.execute('SELECT pollster,date,con,lab,libdem,green FROM polls WHERE id > ?',(earliest2021Id,))
    existing = dbToDf(c.fetchall())
    print(existing)
    print(newPolls)
    complement = newPolls.merge(existing, how = 'outer' ,indicator=True).loc[lambda x : x['_merge']=='left_only']
    complement.drop(['_merge'],axis=1)
    pollsToDB(complement.iloc[::-1])

def dbToDf(polls):
    df = pd.DataFrame(polls,columns=['pollster','date','con','lab','libdem','green'])
    return df   

def makePollTable(file):
    conn = sqlite3.connect(file)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS polls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pollster TEXT,
        date TEXT,
        con TEXT,
        lab TEXT,
        libdem TEXT,
        green TEXT,
        positiveTweets TEXT,
        negativeTweets TEXT,
        sentiment TEXT
    )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # pollsPre2020 = pre2020PollsToDF()
    # polls2020 = newPollsToDF(1)
    # polls2021 = newPollsToDF(0)
    # pre2021Polls = polls2020.append(pollsPre2020)
    # allPolls = polls2021.append(pre2021Polls)
    # makePollTable()
    # pollsToDB(allPolls.iloc[::-1])
    newPollsToDB()