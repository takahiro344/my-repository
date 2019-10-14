# coding: utf-8
# coding=utf-8

import re
import ssl
import sys

import requests
from bs4 import BeautifulSoup

ssl._create_default_https_context = ssl._create_unverified_context

def getIpoInfoFromCodeNo(codeNo):
    minkabuURL = 'https://minkabu.jp/stock/' + str(codeNo) + '/ipo'
    
    bsObj = openTargetURL(minkabuURL)
    companyName = getCompanyName(bsObj)
    if companyName is None:
        return None, (None, None, None), None, None, None
    
    dataList = bsObj.findAll('dl', {'class':'md_data_list'})
    detailInfo = getDetailInfo(dataList)
    if detailInfo[0] is None or detailInfo[1] is None or detailInfo[2] is None:
        # 上場済とみなす。
        return companyName, (None, None, None), None, None, None

    ipokisoURL = getTargetIpoKisoURL(codeNo)
    mainStockHoldersInfo = getMainStockHoldersInfo(ipokisoURL)
    if mainStockHoldersInfo is None:
        # 上場済とみなす。
        return companyName, (None, None, None), None, None, None

    return companyName, detailInfo, mainStockHoldersInfo,\
           minkabuURL, ipokisoURL

def openTargetURL(targetURL):
    html = requests.get(targetURL)
    html.encoding = html.apparent_encoding
    return BeautifulSoup(html.content, 'html.parser')

def getCompanyName(bsObj):
    name = bsObj.find('title').get_text()
    # title == '社名 (銘柄コード)' であることが前提
    if re.search('([0-9][0-9][0-9][0-9])', name):
        return re.sub(' (.*) .*', '', name)
    else:
        return None

def getDetailInfo(dataList):
    try:
        basicInfo = getBasicInfo(dataList[0].findAll('dd'))
        scheduleInfo = getScheduleInfo(dataList[1].findAll('dd'))
        ipoInfo = getIpoInfo(dataList[2].findAll('dd'))
        return (basicInfo, scheduleInfo, ipoInfo)
    except:
        return (None, None, None)

def getBasicInfo(rows):
    try:
        return (rows[1].get_text(), # 市場
                rows[2].get_text(), # 主幹事
                rows[4].get_text()) # 事業内容
    except:
        return None

def getScheduleInfo(rows):
    try:
        return (rows[2].get_text(), # BB期間
                rows[5].get_text()) # 上場日
    except:
        return None

def getIpoInfo(rows):
    try:
        offerPrice = rows[1].get_text()
        issuedStocks = rows[9].get_text()
        marketCapitalization = getMarketCapitalization(offerPrice,
                                                       issuedStocks)
        issuedStocks = re.sub('／ ', '\n', issuedStocks)
        return (offerPrice,           # 公募価格
                rows[2].get_text(),   # 公開価格PER
                rows[4].get_text(),   # 公開価格PBR
                rows[7].get_text(),   # 公募枚数
                rows[8].get_text(),   # 売出枚数
                issuedStocks,         # 発行済株式数
                marketCapitalization) # 時価総額
    except:
        return None

def getMarketCapitalization(offerPrice, issuedStocks):
    stocksNum = re.sub('.*公開日現在：', '', issuedStocks)
    stocksNum = stocksNum.replace(',', '')
    offerPrice = offerPrice.replace(',', '').replace('円', '')
    try:
        marketCap = float(offerPrice) * float(stocksNum)
        return str(marketCap / 100000000.0) + '億円'
    except :
        return '---'

def getTargetIpoKisoURL(codeNo):
    res = requests.get('https://google.com/search?num=3&q='
                       + ' ' + str(codeNo) + ' site:ipokiso.com')
    res.raise_for_status()
 
    bsObj = BeautifulSoup(res.text, 'html.parser')
    urlList = bsObj.select('a[href^="/url?q=https://www.ipokiso.com"]')
    topHref = urlList[0].get('href')
    return re.search(r'https://.*\.html', topHref).group()

def getMainStockHoldersInfo(url):
    bsObj = openTargetURL(url)
    table = bsObj.find('table', {'class':'kobetudate05'})
    elms = table.findAll('td')
    numElms = len(elms)

    try:
        mainStockHoldersInfo = []
        for i in range(0, numElms, 3):
            name = elms[i].get_text()
            name = re.sub(r' +', ' ', name)

            ratio = elms[i + 1].get_text()
        
            lockup = elms[i + 2].get_text()
            lockup = lockup.replace('\r',
                                    '').replace('\n',
                                                '').replace('\u3000', '-')
            lockup = re.sub(r' +', ' ', lockup)
            mainStockHoldersInfo.append((name, ratio, lockup))

        return mainStockHoldersInfo
    except:
        return None

def main():
    if len(sys.argv) < 2:
        print("Please input a code number.")
        return
   
    name, detail, stockHolder, minkabu, ipokiso =\
        getIpoInfoFromCodeNo(sys.argv[1])
    if detail[0] is None or detail[1] is None or detail[2] is None:
        return

    basicInfo = detail[0]
    scheduleInfo = detail[1]
    ipoInfo = detail[2]

    print('【会社名】' + name)
    print('【事業内容】' + basicInfo[2])
    print('【主幹事】' + basicInfo[1])
    print('【市場】' + basicInfo[0])
    print('【BB期間】' + scheduleInfo[0])
    print('【上場日】' + scheduleInfo[1])
    print('【公開価格】' + ipoInfo[0])
    print('【公開価格PER】' + ipoInfo[1])
    print('【公開価格PBR】' + ipoInfo[2])
    print('【発行済株式数】' + ipoInfo[5])
    print('【公募枚数】' + ipoInfo[3])
    print('【売出枚数】' + ipoInfo[4])
    print('【時価総額】' + ipoInfo[6])

    print('【株主、比率、ロックアップ】')
    for s in stockHolder:
        print('  ' + s[0])
        print('  ' + s[1] + '  ' + s[2])

if __name__ == "__main__":
    main()
