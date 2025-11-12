from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from datetime import date

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
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('square_card_detail', kwargs={'slug': self.slug})


class Doctor(models.Model):
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    patronymic = models.CharField(max_length=50, blank=True, null=True, verbose_name="Отчество")
    specialization = models.CharField(max_length=200, verbose_name="Специальность")
    start_work_year = models.PositiveIntegerField(verbose_name="Год начала работы")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    photo = models.ImageField(upload_to="doctors/", blank=True, null=True, verbose_name="Фото")
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    def __str__(self):
        # Если есть отчество
        if self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic}"
        return f"{self.last_name} {self.first_name}"

    @property
    def experience(self):
        years = date.today().year - self.start_work_year
        if years % 10 == 1 and years % 100 != 11:
            return f"{years} год"
        elif 2 <= years % 10 <= 4 and not 12 <= years % 100 <= 14:
            return f"{years} года"
        else:
            return f"{years} лет"
        
    def save(self, *args, **kwargs):
        if not self.slug: 
            base_slug = slugify(f"{self.last_name} {self.first_name} {self.patronymic or ''}")
            slug = base_slug
            num = 1
            while Doctor.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)
