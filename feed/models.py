from django.db import models
from django_fsm import FSMIntegerField, transition
from feed import utils
from user import models as m


class Article(models.Model):
    """Model for Artcile"""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, null=True, blank=True)
    text = models.TextField(null=True, )
    date = models.DateTimeField(auto_now_add=True, null=True)
    type = FSMIntegerField(choices=utils.ArticleType.choices)
    store = models.ForeignKey(m.Store, on_delete=models.CASCADE, null=True)

    @property
    def images(self):
        return self.articleimages_set.all()


class ArticleImages(models.Model):
    """Models for images"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True)
    link = models.TextField(null=True)
    name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.link