from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=256, unique=True, primary_key=True)
    born = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

class Tag(models.Model):
    name = models.CharField(max_length=256, unique=True, primary_key=True)

class Quote(models.Model):
    text = models.CharField(max_length=1024, blank=True, null=True)
    author = models.ForeignKey(Author, blank=True, null=True, on_delete=models.DO_NOTHING)
    tags = models.ManyToManyField(Tag)