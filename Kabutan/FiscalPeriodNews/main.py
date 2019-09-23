from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

latestNewsFile = "LatestNews.txt"

topURL = "https://kabutan.jp"
pageURL = topURL + "/news/?&page="

def main():
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
            print(cols[2].text + ", " + newsURL)
    
    with open(latestNewsFile, "w", encoding="utf-8") as outfile:
      outfile.write(cols[2].text)

if __name__ == "__main__":
    main()
