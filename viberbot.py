from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
import time
import logging
import sched
import threading

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)
viber = Api(BotConfiguration(
    name='Ассистент',
    avatar='http://proforientator.info/wp-content/uploads/2014/05/0_58e02_e09db884_xl.jpg',
    auth_token='4914a9de56a7d22d-8ac2486326693074-ab74616d16bf9123'
))

#Набор сообщений. пускай пока будет тут
walcome_text = "Добро пожаловать в бета-версию бота 'Напомним Всё'!:)\nЯ ваш личный ассистент\nНа данный момент вам доступны такие команды как:\n - 'Старт'\n - 'Инфо'\nЯ ещё не подключёна к основному сайту, поэтому команды и функционал создания заметок и напоминаний - заблокирован.\nОставайтесь с нами!)"
respect_words = ['Инфо', 'Старт']
stupid_questions = ['31.01.2018', 'как дела?']


def send_message(msg):

    if msg.text in respect_words:
        print(msg.text)
        return walcome_text
    elif msg.text in stupid_questions:
        print(msg.text)
        return walcome_text
    else:
        print(msg.text)
        return 'Нет соединения с сайтом( Пока я понимаю только команду "Инфо", остальные функции отключены за ненадобностью!)'



@app.route('/', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))
    viber_request = viber.parse_request(request.get_data())
    if isinstance(viber_request, ViberMessageRequest):
        viber.send_messages(viber_request.sender.id, [TextMessage(text=send_message(viber_request.message))] )
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.get_user.id, [TextMessage(text=walcome_text)])
    elif isinstance(viber_request, ViberUnsubscribedRequest):
        viber.send_messages(viber_request.get_user.id, [TextMessage(text="Back!")])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("client failed receiving message. failure: {0}".format(viber_request))
    elif isinstance(viber_request, ViberConversationStartedRequest):
        viber.send_messages(viber_request.get_user().get_id(), [TextMessage(text=walcome_text)])
    return Response(status=200)


#def set_webhook(viber):
#    viber.set_webhook('https://ae9c1c3b.ngrok.io/')


if __name__ == "__main__":
    scheduler = sched.scheduler(time.time, time.sleep)
    #scheduler.enter(5, 1, set_webhook, (viber,))
    t = threading.Thread(target=scheduler.run)
    t.start()
    context = ('server.crt', 'server.key')
    app.run(host='localhost', port=5000, debug=True)