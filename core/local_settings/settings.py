# Super user
# login/pass = admin/2WSX2wsx123
SECRET_KEY = '7b0fm0-2v3s(95g&3u3z18=!bi(4#!@5m_hul)6no++=mdpj@q'
# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

ALLOWED_HOSTS = ['tseluyko.ru', '127.0.0.1', 'analogpro.ru', 'www.analogpro.ru']

INSTALLED_APPS = [
    'catalog.apps.CatalogConfig',
    'catalog.apps.AnalogAuthConfig',
    'jet',
    'django.contrib.admin',
    # 'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'feincms',
    'mptt',
    'app',
    'api',
    'reporters'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'analog',
        'USER': 'postgres',
        'PASSWORD': '@WSX2wsx123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_HOST_USER = "info@analogpro.ru"
EMAIL_HOST_PASSWORD = "@WSX2wsx123"
EMAIL_USE_TLS = True

# for build graph structure db
GRAPH_MODELS = {
  'all_applications': True,
  'group_models': True,
}
