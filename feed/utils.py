from django.db import models


class ArticleType(models.IntegerChoices):
    news = 1, 'Новости'
    stock = 2, 'Акция'