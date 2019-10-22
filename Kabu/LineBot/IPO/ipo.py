# coding: utf-8
# coding=utf-8

import re
import ssl
import sys
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

ssl._create_default_https_context = ssl._create_unverified_context

def getIpoInfoFromCodeNo(codeNo):
    ipoInfo = defaultdict(lambda: None)
    minkabuURL = 'https://minkabu.jp/stock/' + str(codeNo) + '/ipo'
    
    bsObj = openTargetURL(minkabuURL)
    setCompanyName(ipoInfo, bsObj)

    dataList = bsObj.findAll('dl', {'class':'md_data_list'})
    setDetailInfo(ipoInfo, dataList)

    ipokisoURL = getTargetIpoKisoURL(codeNo)
    setMainStockHoldersInfo(ipoInfo, ipokisoURL)

    ipoInfo["minkabu"] = minkabuURL
    ipoInfo["ipokiso"] = ipokisoURL

    return ipoInfo

def openTargetURL(targetURL):
    html = requests.get(targetURL)
    html.encoding = html.apparent_encoding
    return BeautifulSoup(html.content, 'html.parser')

def setCompanyName(ipoInfo, bsObj):
    name = bsObj.find('title').get_text()
    # title == '社名 (銘柄コード)' であることが前提
    if re.search('([0-9][0-9][0-9][0-9])', name):
        ipoInfo["CompanyName"] = re.sub(' (.*) .*', '', name)

def setDetailInfo(ipoInfo, dataList):
    try:
        setBasicInfo(ipoInfo, dataList[0].findAll('dd'))
        setScheduleInfo(ipoInfo, dataList[1].findAll('dd'))
        setIpoInfo(ipoInfo, dataList[2].findAll('dd'))
    except:
        pass

def setBasicInfo(ipoInfo, rows):
    try:
        ipoInfo["Market"] = rows[1].get_text()        # 市場
        ipoInfo["MainSecretary"] = rows[2].get_text() # 主幹事
        ipoInfo["BussinessDesc"] = rows[4].get_text() # 事業内容
    except:
        pass 

def setScheduleInfo(ipoInfo, rows):
    try:
        ipoInfo["BB"] = rows[2].get_text()          # BB期間
        ipoInfo["ListingDate"] = rows[5].get_text() # 上場日
    except:
        pass

def setIpoInfo(ipoInfo, rows):
    try:
        offerPrice = rows[1].get_text()
        issuedStocks = rows[9].get_text()
        marketCapitalization = getMarketCapitalization(offerPrice,
                                                       issuedStocks)
        issuedStocks = re.sub('／ ', '\n', issuedStocks)

        ipoInfo["OfferPrice"] = offerPrice                     # 公募価格
        ipoInfo["Per"] = rows[2].get_text()                    # 公開価格PER
        ipoInfo["Pbr"] = rows[4].get_text()                    # 公開価格PBR
        ipoInfo["PublicOfferingNum"] = rows[7].get_text()      # 公募枚数
        ipoInfo["IssuedNum"] = rows[8].get_text()              # 売出枚数
        ipoInfo["IssuedStocks"] = issuedStocks                 # 発行済株式数
        ipoInfo["MarketCapitalization"] = marketCapitalization # 時価総額
    except:
        pass

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

def setMainStockHoldersInfo(ipoInfo, url):
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

        ipoInfo["MainStockHolders"] = mainStockHoldersInfo
    except:
        pass

def main():
    if len(sys.argv) < 2:
        print("Please input a code number.")
        return
   
    ipoInfo = getIpoInfoFromCodeNo(sys.argv[1])

    name = ipoInfo["CompanyName"]
    bussinessDesc = ipoInfo["BussinessDesc"]
    mainSecretary = ipoInfo["MainSecretary"]
    market = ipoInfo["Market"]
    bb = ipoInfo["BB"]
    listingDate = ipoInfo["ListingDate"]
    offerPrice = ipoInfo["OfferPrice"]
    per = ipoInfo["Per"]
    pbr = ipoInfo["Pbr"]
    publicOfferingNum = ipoInfo["PublicOfferingNum"]
    issuedNum = ipoInfo["IssuedNum"]
    issuedStocks = ipoInfo["IssuedStocks"]
    marketCapitalization = ipoInfo["MarketCapitalization"]
    stockHolder = ipoInfo["MainStockHolders"]

    if (name is None or
        bussinessDesc is None or
        mainSecretary is None or
        market is None or
        bb is None or
        listingDate is None or
        offerPrice is None or
        per is None or
        pbr is None or
        publicOfferingNum is None or
        issuedNum is None or
        issuedStocks is None or
        marketCapitalization is None or
        stockHolder is None):
        return

    print('【会社名】' + name)
    print('【事業内容】' + bussinessDesc)
    print('【主幹事】' + mainSecretary)
    print('【市場】' + market)
    print('【BB期間】' + bb)
    print('【上場日】' + listingDate)
    print('【公開価格】' + offerPrice)
    print('【公開価格PER】' + per)
    print('【公開価格PBR】' + pbr)
    print('【発行済株式数】' + issuedStocks)
    print('【公募枚数】' + publicOfferingNum)
    print('【売出枚数】' + issuedNum)
    print('【時価総額】' + marketCapitalization)

    print('【株主、比率、ロックアップ】')
    for s in stockHolder:
        print('  ' + s[0])
        print('  ' + s[1] + '  ' + s[2])

if __name__ == "__main__":
    main()
