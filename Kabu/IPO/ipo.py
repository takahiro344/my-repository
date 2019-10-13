# coding: utf-8
# coding=utf-8

from bs4 import BeautifulSoup
import ssl
import re, requests
import sys

ssl._create_default_https_context = ssl._create_unverified_context

def getIpoInfoFromCodeNo(codeNo):
    minkabuURL = getTargetMinkabuURL(codeNo)
    
    bsObj = openTargetURL(minkabuURL)
    companyName = getCompanyName(bsObj)
    
    dataList = bsObj.findAll('dl', {'class':'md_data_list'})
    detailInfo = getDetailInfo(dataList)

    ipokisoURL = getTargetIpoKisoURL(codeNo)
    mainStockHoldersInfo = getMainStockHoldersInfo(ipokisoURL)

    return companyName, detailInfo, mainStockHoldersInfo,\
           minkabuURL, ipokisoURL

def getTargetMinkabuURL(codeNo):
    return 'https://minkabu.jp/stock/' + str(codeNo) + '/ipo'

def openTargetURL(targetURL):
    html = requests.get(targetURL)
    html.encoding = html.apparent_encoding
    return BeautifulSoup(html.content, 'html.parser')

def getCompanyName(bsObj):
    name = bsObj.find('title').get_text()
    return re.sub(' (.*) .*', '', name)

def getDetailInfo(dataList):
    basicInfo = getBasicInfo(dataList[0].findAll('dd'))
    scheduleInfo = getScheduleInfo(dataList[1].findAll('dd'))
    ipoInfo = getIpoInfo(dataList[2].findAll('dd'))
    return (basicInfo, scheduleInfo, ipoInfo)

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
        issuedStocks = rows[9].get_text()
        issuedStocks = re.sub('／ ', '\n', issuedStocks)
        return (rows[1].get_text(), # 公募価格
                rows[2].get_text(), # 公開価格PER
                rows[4].get_text(), # 公開価格PBR
                rows[7].get_text(), # 公募枚数
                rows[8].get_text(), # 売出枚数
                issuedStocks) # 発行済株式数
    except:
        return None

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

    print('【会社名】\n' + name)
    print('【事業内容】\n' + basicInfo[2])
    print('【主幹事】\n' + basicInfo[1])
    print('【市場】\n' + basicInfo[0])
    print('【BB期間】\n' + scheduleInfo[0])
    print('【上場日】\n' + scheduleInfo[1])
    print('【公開価格】\n' + ipoInfo[0])
    print('【公開価格PER】\n' + ipoInfo[1])
    print('【公開価格PBR】\n' + ipoInfo[2])
    print('【発行済株式数】\n' + ipoInfo[5])
    print('【公募枚数】\n' + ipoInfo[3])
    print('【売出枚数】\n' + ipoInfo[4])

    print('【株主、比率、ロックアップ】')
    for s in stockHolder:
        print(s[0])
        print(s[1] + '  ' + s[2])

if __name__ == "__main__":
    main()
