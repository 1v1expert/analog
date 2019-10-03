from django.contrib.auth import models
from catalog.internal.messages import send_email_with_connection

import hashlib


def registration(request=None):
    if request is None:
        return False, ''
    
    if request.POST['password'] != request.POST['double_password']:
        return False, "Введённые пароли не совпадают"
    
    if len(request.POST['password']) < 8:
        return False, "Введённый пароль слишком короткий. Он должен содержать как минимум 8 символов. "
    
    user, created = models.User.objects.get_or_create(username=request.POST['username'],
                                                      defaults={
                                                          'email': request.POST['email'],
                                                          'is_active': False
                                                      })
    if not created:
        return False, "пользователь уже существует"
    
    # if not user.check_password(request.POST['password']):
    #     user.delete()
    #     return False, 'Введённый пароль некорректен'
    
    user.set_password(request.POST['password'])
    user.save()

    verification_code = hashlib.md5('{}'.format(user.pk).encode()).hexdigest()
    href = 'http://analogpro.ru/email_confirmation/{}-{}/'.format(verification_code, user.pk)
    header = 'Подтверждение почты'
    msg = 'Ваш верификационный код - {}, введите его или перейдите по ссылке: {}\n'.format(verification_code, href)
    try:
        send_email_with_connection(header, msg, [request.POST['email']])
        return True, user
    except Exception as e:
        print(e)
        return False, 'Произошла проблема при отправке email'
    

def confirm_email(verification):
    pass
