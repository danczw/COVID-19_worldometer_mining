import urllib.request
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
import datetime

url = "https://www.worldometers.info/coronavirus/"  # set target url
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'  # user agent
headers = {'User-Agent': user_agent}  # add user agent to request header

# request url content and read / parse response html
request = urllib.request.Request(url, None, headers=headers)
response = urllib.request.urlopen(request)
html = response.read()
soup = BeautifulSoup(html, "html.parser")

"""
1st part looks for data only
"""

table = soup.find("table", {"id": "main_table_countries_today"})  # find table in html
rows = table.findAll("td")  # find table content

table_cells = []  # define list for table cell content

# get cell content from table using regular expression and append to list
for row in rows:
    row = str(row)
    covid_regex = re.compile(r">+[+]?\d*,?\d*,?\d*[.]?\d*\D*<+")
    reg_result = covid_regex.search(row)
    try:
        table_cells.append(reg_result.group())
    except AttributeError:
        table_cells.append("EXCEPT ATTRIBUTE ERROR")

data = []  # define list for cleaned table cell content

# clean and append cell content to list
for cell in table_cells:
    try:
        data.append(float(cell.replace(">", "").replace("<", "").replace("+", "").replace(",", "")))
    except ValueError:
        data.append(cell[1:-1])

data = data[:-13]  # delete last 13 entries (which are total rows in original table)
data_array = np.reshape(np.array(data), (-1, 13))  # reshape list to array of size 212 x 11

# transform array to dataframe and add col names
df = pd.DataFrame(data_array, columns=["Country", "Total Cases", "New Cases", "Total Deaths", "New Deaths",
                                       "Total Recovered", "Active Cases", "Serious, Critical", "Tot Cases/1M pop",
                                       "Deaths/ 1M pop", "Total Tests", "Tests/ 1M pop", "Continent"])

"""
2nd part cleans up country names and saves data to excel
"""

ctry = df["Country"].tolist()  # get country data and save to list
ctry_clean = []  # define new list for cleaned data
ctry_regex = re.compile(r">+\w*-?.?\s?\w*\s?\w*\s?\w*<+")  # define regular expression to extract country name

# iterate through ist and extract country name based on regex (+ filter for e.g. vessels)
for i in ctry:
    reg_result = ctry_regex.search(i)
    try:
        ctry_clean.append(reg_result.group()[1:-1])
    except AttributeError:
        ctry_clean.append("NO COUNTRY")
df["Country"] = ctry_clean  # save cleaned country data to df

df[8:-7].to_csv(f"{datetime.datetime.now().date()} COVID-19 worldwide.csv", sep=";")  # save data to excel
print("Excel printed!")
