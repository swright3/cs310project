from bs4 import BeautifulSoup
import requests
import csv

source = requests.get('https://en.wikipedia.org/wiki/Opinion_polling_for_the_next_United_Kingdom_general_election#2021').text
soup = BeautifulSoup(source,'lxml')

print(soup.prettify())