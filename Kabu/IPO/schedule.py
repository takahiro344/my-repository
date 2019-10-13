# coding: utf-8
# coding=utf-8

import datetime
import re
import ssl

import requests
from bs4 import BeautifulSoup

ssl._create_default_https_context = ssl._create_unverified_context

yahooFinanceURL = 'https://info.finance.yahoo.co.jp/ipo/'
def getListingScheduleInfo():
    today = datetime.date.today()
    bsObj = openTargetURL(yahooFinanceURL)
    ipoBrandBox = bsObj.findAll('div', {'class':'ipoBrandBox'})

    info = []
    for box in ipoBrandBox:
        name = getCompanyName(box)
        codeNo = getCodeNo(box)
        date = getListingDate(box)

        if date >= today:
            info.append((name, codeNo, date))
            print(info)
    
    return info

def openTargetURL(targetURL):
    html = requests.get(targetURL)
    html.encoding = html.apparent_encoding
    return BeautifulSoup(html.content, 'html.parser')

def getCompanyName(box):
    return box.find('td', {'class':'ttl'}).get_text()

def getCodeNo(box):
    codeNo = box.findAll('td', {'class': 'text'})[0].get_text()
    return re.search('[0-9][0-9][0-9][0-9]', codeNo).group()

def getListingDate(box):
    date = box.find('td', {'class':'presentation'}).get_text()
    date = re.sub('上場日 ', '', date).split('/')
    return datetime.date(int(date[0]), int(date[1]), int(date[2]))

def main():
    info = getListingScheduleInfo();
    for i in info:
        print('【銘柄名】' + i[0])
        print('【銘柄コード】' + i[1])
        print('【上場日】' + i[2].strftime('%Y/%m/%d'))
        print()

if __name__ == "__main__":
    main()
