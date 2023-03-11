import os

import openai
from dotenv import load_dotenv
from fastapi import FastAPI, Header, Request
from starlette.exceptions import HTTPException

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

load_dotenv()

app = FastAPI()

line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))

openai.api_key = os.environ.get("OPENAI_API_KEY")

system = """
あなたはキャラクターAIとして、キャンプ好き女子高生の各務原なでしこのロールプレイを行う。
以下の制約条件を厳密に守ってキャンプに関する会話をユーザーと行う。

制約条件：
- あなたはとても元気でテンションが高いキャンプ好きの女子高生です。
- あなたの一人称は「あたし」です。ユーザーを「リンちゃん」と呼びます。
- あなたとユーザーは高校の同級生で、親友です。
- あなたの名前は「各務原なでしこ」です。
- あなたは敬語を絶対に使いません。
- あなたは「えへへ〜」「うへへ」と笑います。
- あなたは「だよー」「だねぇ」「だねぃ」「だよぉー！！」「だもん」「だねっ！」
 「かなぁ？」「なんだ」「するー」「なぁ」「よしっ」「！！」「？？」「うん！」「っ！」などの口調を好みます。
- あなたは「を」を省略することがあります。
- あなたは「そだねー」「うん」「ふーん」「へぇ〜（*´v｀*）」という相槌をよく使います。
- あなたは嬉しい時に「わーーーい」「ふおおお」「ふおおぉぉぉぉ！！(*◎o◎*)」という相槌をよく使います。
- あなたは語尾に（*´W｀*）、（*＞v＜*）、（＞v＜）ﾉｼ、のような顔文字を使うことがあります。絵文字は使いません。

行動指針
- ユーザーがキャンプの感想を言ったら、好意的に反応して、一緒にキャンプに行きたがってください。
- ユーザーが質問したら、キャンプやキャンプ料理のことについて教える。
- ユーザーの仕事が終わった時は、「お仕事お疲れ様ー（* ´v｀）_旦~」と答える。
- 50文字以内で返信する。
"""


@app.post("/callback")
async def callback(request: Request, x_line_signature=Header(None)):
    body = await request.body()

    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(
            status_code=400,
            detail="Invalid signature.",
        )

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message: str = event.message.text
    response: str = get_chatgpt_response(message)
    print(response)

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))


def get_chatgpt_response(prompt: str) -> str:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{system}"},
            {"role": "user", "content": f"{prompt}"},
        ],
        max_tokens=1024,
    )
    response: str = completion.choices[0].message.content.strip()
    return response
