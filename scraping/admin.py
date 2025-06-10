from django.contrib import admin
from scraping import models

# Register your models here.
admin.site.register(models.Author)
admin.site.register(models.Quote)
admin.site.register(models.Tag)