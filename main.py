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

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))


def get_chatgpt_response(prompt: str) -> str:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"{prompt}"},
        ],
        max_tokens=1024,
    )
    response: str = completion.choices[0].message
    return response
