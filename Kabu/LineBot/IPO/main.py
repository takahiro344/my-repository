import os
import re

from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (CarouselColumn, CarouselTemplate,
                            MessageEvent, TemplateSendMessage, TextMessage,
                            TextSendMessage, URITemplateAction)

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
        if not isCode:
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
    name, details, holders, minkabu, ipokiso =\
        ipo.getIpoInfoFromCodeNo(receivedTxt)
    basicInfo = details[0]
    scheduleInfo = details[1]
    ipoInfo = details[2]
    if basicInfo is None or scheduleInfo is None or ipoInfo is None:
        replyTxt = name + 'は上場済です。'
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text=replyTxt))
        return
    
    holderInfo = createStockHolderInfo(holders)
    urlCols = getCarouselColumn(name, minkabu, ipokiso)

    messages = [
        TextSendMessage(text='【会社名】\n' + name + '\n'\
                             + '【事業内容】\n' + basicInfo[2] + '\n'\
                             + '【主幹事】\n' + basicInfo[1] + '\n'\
                             + '【市場】\n' + basicInfo[0] + '\n'\
                             + '【上場日】\n' + scheduleInfo[1]),
        TextSendMessage(text='【公開価格】\n' + ipoInfo[0] + '\n'\
                             + '【公開価格PER】\n' + ipoInfo[1] + '\n'\
                             + '【公開価格PBR】\n' + ipoInfo[2] + '\n'\
                             + '【発行済株式数】\n' + ipoInfo[5] + '\n'\
                             + '【公募枚数】\n' + ipoInfo[3] + '\n'\
                             + '【売出枚数】\n' + ipoInfo[4]),
        TextSendMessage(text='【株主、比率、ロックアップ】\n' + holderInfo),
        TemplateSendMessage(
            alt_text = '参考サイト',
            template = CarouselTemplate(columns=urlCols,
                                        image_size='cover'),
        )
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
                    label = name,
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
                      label = name,
                  )
            ]
        ),
    ]

    return urlCols

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
