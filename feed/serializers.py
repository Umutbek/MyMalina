from django.contrib.auth import get_user_model
from rest_framework import serializers, exceptions
from feed import models, utils
from item.serializers import MyStore


class ArticleImagesSerializer(serializers.ModelSerializer):
    """Serializer for item Images"""
    id = serializers.IntegerField(required=False)

    class Meta:
        model = models.ArticleImages
        fields = ('id', 'link', 'name')


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer article"""
    images = ArticleImagesSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = models.Article
        fields = ('id', 'title', 'subtitle', 'text', 'images', 'date', 'type', 'store')


    def create(self, validated_data):

        images = validated_data.pop("images", None)
        article = models.Article.objects.create(**validated_data)

        if images:
            for i in images:
                models.ArticleImages.objects.create(article=article, **i)
        return article

    def update(self, instance, validated_data):
        images = validated_data.pop('images')
        articleimage = (instance.images).all()
        articleimage = list(articleimage)
        saveimage = []

        if images:
            for i in images:
                if i['link']:
                    saveimage.append(i['link'])

            for j in instance.images.all():
                if j:
                    if str(j) in saveimage:
                        pass
                    else:
                        j.delete()
        else:
            instance.images.all().delete()

        instance.title = validated_data.get('title', instance.title)
        instance.subtitle = validated_data.get('subtitle', instance.subtitle)
        instance.text = validated_data.get('text', instance.text)
        instance.store = validated_data.get('store', instance.store)
        instance.save()

        # if len(articleimage) == len(saveimage):
        #
        #     for a in images:
        #         if articleimage:
        #             i = articleimage.pop(0)
        #             i.link = a.get('link', i.link)
        #             i.name = a.get('name', i.name)
        #
        #             i.save()
        #         else:
        #             c = models.ArticleImages.objects.create(article=instance, **a)
        #             c.save()
        #             articleimage.append(c.id)

        # if images:
        #     for i in images:
        #         saveimage.append(i['link'])
        #
        #     if len(articleimage)>len(saveimage):
        #         for j in articleimage:
        #             if str(j) not in saveimage:
        #                 j.delete()
        #     elif len(articleimage)<len(saveimage):
        #         for j in images:
        #             if j['link'] not in str(articleimage):
        #                 c = models.ArticleImages.objects.create(article=instance, **j)
        #                 c.save()
        #                 articleimage.append(c.id)
        # else:
        #     instance.images.all().delete()

        if images:
            for a in images:
                if articleimage:
                    i = articleimage.pop(0)
                    i.id = a.get('id', i.id)
                    i.link = a.get('link', i.link)
                    i.name = a.get('name', i.name)
                    i.save()
                else:
                    c = models.ArticleImages.objects.create(article=instance, **a)
                    c.save()
                    articleimage.append(c.id)

        return instance


class GetArticleSerializer(serializers.ModelSerializer):
    """Serializer article"""
    images = ArticleImagesSerializer(many=True, required=False, allow_null=True)
    store = MyStore()

    class Meta:
        model = models.Article
        fields = ('id', 'title', 'subtitle', 'text', 'images', 'date', 'type', 'store')


class DeleteSeveralArticlesSerializer(serializers.Serializer):
    """Create new cart"""
    articles = serializers.ListField(required=False, allow_null=True)

    def save(self):
        items = self.validated_data['articles']