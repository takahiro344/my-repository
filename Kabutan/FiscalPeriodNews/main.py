import config
from twitter import Twitter, OAuth

from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

latestNewsFile = "LatestNews.txt"

topURL = "https://kabutan.jp"
pageURL = topURL + "/news/?&page="

def main():
    tw = Twitter(
        auth = OAuth(
            config.TW_TOKEN,
            config.TW_TOKEN_SECRET,
            config.TW_CONSUMER_KEY,
            config.TW_CONSUMER_SECRET,
        )
    )
    
    latestNews = ""
    if os.path.exists(latestNewsFile):
      with open(latestNewsFile, "r", encoding="utf-8") as infile:
        latestNews = infile.read()

    output = False
    if not latestNews:
        output = True

    for pageNo in reversed(range(1, 22)):
      eachPageURL = pageURL + str(pageNo)
      html = urlopen(eachPageURL)
      bsObj = BeautifulSoup(html, "html.parser")

      table = bsObj.findAll("table", {"class":"s_news_list"})[0]
      rowList = table.findAll("tr")

      for row in reversed(rowList):
          cols = row.find_all('td')
          # cols[2]: <td><a href="/news/?b=...">...</a></td>
          href = cols[2].find('a').get('href')
          newsURL = topURL + href

          if output == False and latestNews == cols[2].text:
              output = True
              continue

          if output == True:
            msg = cols[2].text + "\n" + newsURL
            tw.statuses.update(status=msg)
    
    with open(latestNewsFile, "w", encoding="utf-8") as outfile:
      outfile.write(cols[2].text)

if __name__ == "__main__":
    main()
