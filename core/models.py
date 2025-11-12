from django.db import models
from django.utils.text import slugify

class HeroCard(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    subtitle = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to="hero_cards/", blank=True, verbose_name="Изображение")
    button_text = models.CharField(max_length=50, default="Подробнее", verbose_name="Текст кнопки")
    button_url = models.CharField(max_length=50, default="#", verbose_name="Ссылка кнопки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    

class SmallCard(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    

class SquareCard(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    image = models.ImageField(upload_to="square_cards/", blank=True, null=True, verbose_name="Изображение")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
