# Super user
# login/pass = admin/2WSX2wsx123
SECRET_KEY = '7b0fm0-2v3s(95g&3u3z18=!bi(4#!@5m_hul)6no++=mdpj@q'
# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
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

# for build graph structure db
GRAPH_MODELS = {
  'all_applications': True,
  'group_models': True,
}