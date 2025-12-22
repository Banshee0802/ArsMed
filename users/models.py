from django import forms
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Пациент'),
        ('admin', 'Админ')
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='patient')
    last_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Фамилия")
    first_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Имя")
    patronymic = models.CharField(max_length=50, blank=True, null=True, verbose_name="Отчество")
    gender_choices = (
        ('male', 'Мужской'),
        ('female', 'Женский')
    )
    gender = models.CharField(max_length=6, choices=gender_choices, verbose_name="Пол")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Номер телефона")

    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    def clean(self):
        super().clean()

        if self.role == 'patient':
            errors = {}

            if not self.birth_date:
                errors['birth_date'] = 'Дата рождения обязательна для пациента'

            if not self.phone:
                errors['phone'] = 'Телефон обязателен для пациента'

            if errors:
                raise forms.ValidationError(errors)
