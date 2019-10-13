import config
from twitter import Twitter, OAuth

from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

topURL = "https://kabutan.jp"

def main():
    tw = Twitter(
        auth = OAuth(
            config.TW_TOKEN,
            config.TW_TOKEN_SECRET,
            config.TW_CONSUMER_KEY,
            config.TW_CONSUMER_SECRET
        )
    )
    
    latestNews = getSavedLatestNews()
    output = True if not latestNews else False

    for pageNo in reversed(range(1, 22)):
        html = openTargetURL(pageNo)
        bsObj = BeautifulSoup(html, "html.parser")

        table = bsObj.findAll("table", {"class":"s_news_list"})[0]
        rowList = table.findAll("tr")

        for row in reversed(rowList):
            cols = row.find_all('td')
            # cols[2]: <td><a href="/news/?b=...">...</a></td>
            href = cols[2].find('a').get('href')
            newsURL = topURL + href
            
            if output:
                msg = cols[2].text + "\n" + newsURL
                tw.statuses.update(status=msg)
          
            if not output and cols[2].text in latestNews:
                output = True
                continue
    
    with open(latestNewsFile, "w", encoding="utf-8") as outfile:
        outfile.write(cols[2].text)

latestNewsFile = "LatestNews.txt"

def getSavedLatestNews():
    latestNews = ""

    if os.path.exists(latestNewsFile):
        with open(latestNewsFile, "r", encoding="utf-8") as infile:
            latestNews = infile.read()
    
    return latestNews

pageURL = topURL + "/news/?&page="

def openTargetURL(pageNo):
    targetURL = pageURL + str(pageNo)
    return urlopen(targetURL)

if __name__ == "__main__":
    main()
