SECRET_KEY = 'django-insecure-y_@@zrr4pc2e5#9v*9=$wkq5dwvf88876^&(xefkwlh@5wi*&*ts'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['138.68.99.168']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'localhost',
        'NAME': 'malinadb',
        'USER': 'malinauser',
        'PASSWORD': 'malina2021'
    }
}
