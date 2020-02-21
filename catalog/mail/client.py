# from django.shortcuts import render
import requests
import os
from django.conf import settings


class MailGun(object):
    """ Класс, реализующий отправку text/html сообщений через MailGun"""

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    
    def __init__(self):
        self._auth = ("api", settings.EMAIL_MAILGUN_APITOKEN)
        self._url = settings.EMAIL_MAILGUN_URL
    
    @staticmethod
    def generate_random_text():
        return requests.get('http://www.randomtext.me/api/').json().get('text_out')
    
    def send_test_message(self, to=('info@analogpro.ru', ), subj='Text MailGun', text=''):
        # text = self.generate_random_text()
        return requests.post(self._url,
                             auth=self._auth,
                             data={"from": "Excited User <sazonov@analogpro.ru>",
                                   "to": to,
                                   'subject': subj,
                                   'text': text or self.generate_random_text().text
                                   }
                             )
    
    def send_html_invite(self, to=('info@analogpro.ru', ), html='', bcc=("", )):
        html = open(os.path.join(self.PROJECT_ROOT, 'templates/index.html'))
        images = os.path.join(settings.BASE_DIR, 'app/static/email_images')
        return requests.post(self._url,
                             auth=self._auth,
                             files=[("inline",
                                     ("ezgif_com-gif-maker.png",
                                      open(os.path.join(images, "ezgif_com-gif-maker.png"), 'rb').read())),
                                    ("inline",
                                     ("search.png",
                                      open(os.path.join(images, "search.png"), 'rb').read())),
                                    ("inline",
                                     ("time.png",
                                      open(os.path.join(images, "time.png"), 'rb').read())),
                                    ("inline",
                                     ("business.png",
                                      open(os.path.join(images, "business.png"), 'rb').read())),
                                    ],
                             data={"from": "АналогПро <sazonov@analogpro.ru>",
                                   "to": to,
                                   "bcc": bcc,
                                   'subject': 'Перевод кабельных лотков - БЫСТРО и БЕСПЛАТНО!',
                                   'html': html.read(),
                                   'text': '*Инновационный сервис подбора кабельных лотков*\n'
                                           '*Умный подбор аналогов*\n'
                                           'Переводите кабельные лотки с одного производителя на другого на сайте '
                                           'analogpro.ru <http://analogpro.ru>\n'
                                           '*Быстро и бесплатно*\n'
                                           'Не тратьте кучу времени и денегна «перевод» спецификаций!'
                                           'Это можно сделать быстро на analogpro.ru! <http://analogpro.ru>\n'
                                           '*Для производителей и дистрибьюторов*\n'
                                           'Вы производитель или дистрибьютор?\n'
                                           'Разместите виджет analogpro.ru <http://analogpro.ru> на своем сайте БЕСПЛАТНО и '
                                           'увеличивайте продажи!',
                                   "o:tracking": True,
                                   }
                             )
# https://email.uplers.com/blog/step-step-guide-create-html-email/
