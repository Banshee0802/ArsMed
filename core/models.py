from django.db import models
from django.utils.text import slugify
from transliterate import translit
from django.urls import reverse
from datetime import date
from users.models import CustomUser


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
    
    class Meta:
        verbose_name = "Главная карточка"
    

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
    
    class Meta:
        verbose_name_plural = "Маленькие карточки"
    

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
    
    class Meta:
        verbose_name_plural = "Квадратные карточки"


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
            name = f"{self.last_name} {self.first_name} {self.patronymic or ''}"
            name_translit = translit(name, 'ru', reversed=True)
            base_slug = slugify(name_translit)
            slug = base_slug or 'doctor'
            num = 1
            while Doctor.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Доктор"
        verbose_name_plural = "Доктора"


class Services(models.Model):
    title = models.CharField(max_length=250, verbose_name="Название услуги")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
    

class Promotion(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название акции")
    image = models.ImageField(upload_to="promotions/", blank=True, null=True, verbose_name="Баннер акции")
    start_date = models.DateField(blank=True, null=True, verbose_name="Дата начала")
    end_date = models.DateField(blank=True, null=True, verbose_name="Дата окончания")
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        if self.start_date and self.end_date:
            return self.start_date <= today <= self.end_date
        return False

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"


class Contacts(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название организации")
    address = models.CharField(max_length=300, verbose_name="Адрес")
    phone = models.CharField(max_length=50, verbose_name="Номер телефона")
    email = models.EmailField(verbose_name="Email")
    latitude = models.FloatField(blank=True, null=True, verbose_name="Широта")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Долгота")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"


class Schedule(models.Model):
    STATUS_CHOICES = [
        ('available', 'Свободно'),
        ('booked', 'Занято'),
        ('confirmed', 'Подтверждено'),
        ('completed', 'Приём состоялся'),
        ('cancelled', 'Отменено'),
        ('closed', 'Закрыто')
    ]
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules', verbose_name='Доктор')
    date = models.DateField(verbose_name="Дата")
    start_time = models.TimeField(verbose_name="Начало приёма")
    end_time = models.TimeField(verbose_name="Конец приёма")
    booked_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Забронировано")
    medical_report = models.FileField(
        upload_to='medical_reports/',
        null=True,
        blank=True,
        verbose_name='Медицинское заключение (PDF)'
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    def __str__(self):
        return f"{self.doctor} - {self.date} {self.start_time}-{self.end_time}"

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')
        ordering = ['date', 'start_time']
        verbose_name = "График"
        verbose_name_plural = "Графики"


class Review(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews', verbose_name="Доктор")
    patient = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name="Пациент")
    rating = models.PositiveSmallIntegerField(default=5, choices=[(i, i) for i in range(1, 6)], verbose_name="Рейтинг")
    comment = models.TextField(blank=True, max_length=1000, verbose_name="Отзыв")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.patient} → {self.doctor} ({self.rating})"
    

class SymptomAnalysis(models.Model):
    user_query = models.TextField(verbose_name="Жалобы пациента")
    ai_result = models.TextField(verbose_name="Анализ ИИ")
    recommended_doctor = models.CharField(max_length=100, blank=True, verbose_name="Рекомендованный врач")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время запроса") 

    class Meta:
        verbose_name = "Анализ симптомов"
        verbose_name_plural = "История анализов ИИ"
        ordering = ["-created_at"]

        def __str__(self):
            return f"Запрос от {self.created_at.strftime("%d.%m.%Y %H:%M")}"