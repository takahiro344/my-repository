import os
import re

from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (CarouselColumn, CarouselTemplate, MessageEvent,
                            TemplateSendMessage, TextMessage, TextSendMessage,
                            URITemplateAction)

import ipo
import schedule

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    receivedTxt = event.message.text
    isCodeNo = re.search('[0-9][0-9][0-9][0-9]$', receivedTxt)
    isSchedule = re.search('list|リスト', receivedTxt)

    if not isCodeNo and not isSchedule:
        replyTxt = ''
        if not isCodeNo:
            replyTxt = '取得したい銘柄コードを正しく入力してください。'
        else:
            return

        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text=replyTxt))
        return

    if isSchedule:
        showSchedule(event)
        return

    if isCodeNo:
        showIpoInfo(event, receivedTxt)
        return

def showSchedule(event):
    replyTxt = ''
    scheduleList = schedule.getListingScheduleInfo()

    index = 0
    scheduleNum = len(scheduleList)
    for sch in scheduleList:
         name, codeNo = sch[0], sch[1]
         date = sch[2].strftime('%Y/%m/%d')
         replyTxt = replyTxt\
                    + '【銘柄】' + name + ' (' + codeNo + ')' + '\n'\
                    + '【上場日】' + date
         index += 1
         if index != scheduleNum:
             replyTxt = replyTxt + '\n'
    
    line_bot_api.reply_message(event.reply_token,
                               TextSendMessage(text=replyTxt))

def showIpoInfo(event, receivedTxt):
    ipoInfo = ipo.getIpoInfoFromCodeNo(receivedTxt)
    name = ipoInfo["CompanyName"]
    if name is None:
        replyTxt = '銘柄コードが正しいかどうか確認してください。'
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text=replyTxt))
        return

    bussinessDesc = ipoInfo["BussinessDesc"]
    mainSecretary = ipoInfo["MainSecretary"]
    market = ipoInfo["Market"]
    listingDate = ipoInfo["ListingDate"]
    offerPrice = ipoInfo["OfferPrice"]
    per = ipoInfo["Per"]
    pbr = ipoInfo["Pbr"]
    publicOfferingNum = ipoInfo["PublicOfferingNum"]
    issuedNum = ipoInfo["IssuedNum"]
    issuedStocks = ipoInfo["IssuedStocks"]
    marketCapitalization = ipoInfo["MarketCapitalization"]
    stockHolder = ipoInfo["MainStockHolders"]

    minkabu = ipoInfo["minkabu"]
    ipokiso = ipoInfo["ipokiso"]
    urlCols = getCarouselColumn(name, minkabu, ipokiso)
    urlMsg = TemplateSendMessage(
                 alt_text = '参考サイト',
                 template = CarouselTemplate(columns=urlCols,
                                             image_size='cover')
             )

    if (bussinessDesc is None or
        mainSecretary is None or
        market is None or
        listingDate is None or
        offerPrice is None or
        per is None or
        pbr is None or
        publicOfferingNum is None or
        issuedNum is None or
        issuedStocks is None or
        marketCapitalization is None or
        stockHolder is None):
        messages = [
            TextSendMessage(text=name + \
                            'は、上場済または数日以内に上場の予定です。'),
            urlMsg,
        ]
        line_bot_api.reply_message(event.reply_token, messages=messages)
        return
    
    holderInfo = createStockHolderInfo(stockHolder)

    messages = [
        TextSendMessage(text='【会社名】' + name + '\n'\
                             + '【事業内容】' + bussinessDesc + '\n'\
                             + '【主幹事】' + mainSecretary + '\n'\
                             + '【市場】' + market + '\n'\
                             + '【上場日】' + listingDate + '\n'\
                             + '【公開価格】' + offerPrice + '\n'\
                             + '【時価総額】' + marketCapitalization + '\n'\
                             + '【公開価格PER】' + per + '\n'\
                             + '【公開価格PBR】' + pbr + '\n'\
                             + '【発行済株式数】\n' + issuedStocks + '\n'\
                             + '【公募枚数】' + publicOfferingNum + '\n'\
                             + '【売出枚数】' + issuedNum),
        TextSendMessage(text='【株主、比率、ロックアップ】\n' + holderInfo),
        urlMsg,
    ]

    line_bot_api.reply_message(event.reply_token, messages=messages)

def createStockHolderInfo(holders):
    holderInfo = ''
    index = 0
    holderNum = len(holders)
    for h in holders:
        holderInfo = holderInfo + h[0] + '\n' + h[1] + '  ' + h[2]
        index += 1
        if index != holderNum:
            holderInfo = holderInfo + '\n'
    return holderInfo

def getCarouselColumn(name, minkabu, ipokiso):
    urlCols = [
        CarouselColumn(
            thumbnail_image_url = 'https://assets.minkabu.jp/images/icon/home-icon.png',
            title = 'みんかぶ',
            text = '「みんかぶ」に載っている' + name + 'の情報です。',
            actions = [
                URITemplateAction(
                    uri = minkabu,
                    label = 'みんかぶをみる',
                )
            ]
        ),
        CarouselColumn(
            thumbnail_image_url = 'https://www.ipokiso.com/common/images/apple-touch-icon-precomposed.png',
            title = 'やさしいIPO株のはじめ方',
            text = '「やさしいIPO株のはじめ方」に載っている' + name + 'の情報です。',
            actions = [
                  URITemplateAction(
                      uri = ipokiso,
                      label = 'やさしいIPO株のはじめ方をみる',
                  )
            ]
        ),
    ]

    return urlCols

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
