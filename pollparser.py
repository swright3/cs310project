from bs4 import BeautifulSoup
import requests
import csv

source = requests.get('https://en.wikipedia.org/wiki/Opinion_polling_for_the_next_United_Kingdom_general_election#2021').text
soup = BeautifulSoup(source,'lxml')

table = soup.find('table', class_='wikitable sortable').tbody

rows = table.find_all('tr')

csvfile = open('pollresults.csv','w',newline='')
csvwriter = csv.writer(csvfile)

headers = rows[0].find_all('th')
for header in range(len(headers)):
    headers[header] = headers[header].text.replace('\n', '')
rows.pop(0)
csvwriter.writerow(headers)

for row in rows:
    data = row.find_all('td')
    print(len(data),len(headers))
    if len(data) == len(headers):
        for datum in range(len(data)):
            data[datum] = data[datum].text.replace('\n', '')
        csvwriter.writerow(data)

csvfile.close()
