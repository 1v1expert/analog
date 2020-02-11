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
    
    def send_html_invite(self, to=('info@analogpro.ru', ), html=''):
        html = open(os.path.join(self.PROJECT_ROOT, 'templates/invitation.html'))
        return requests.post(self._url,
                             auth=self._auth,
                             data={"from": "Продавец слёз <sazonov@analogpro.ru>",
                                   "to": to,
                                   'subject': 'Подбор кабельных лотков - АналогPRO',
                                   'html': html.read()
                                   }
                             )
# https://email.uplers.com/blog/step-step-guide-create-html-email/
