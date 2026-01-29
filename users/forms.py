from allauth.account.forms import SignupForm
from django import forms
from .models import CustomUser
from core.models import Schedule


class CustomSignupForm(SignupForm):
    last_name = forms.CharField(max_length=50, label="Фамилия")
    first_name = forms.CharField(max_length=50, label="Имя")
    patronymic = forms.CharField(max_length=50, required=False, label="Отчество")
    gender = forms.ChoiceField(
        choices=CustomUser.gender_choices, label="Пол", widget=forms.RadioSelect
    )
    birth_date = forms.DateField(
        label="Дата рождения", widget=forms.DateInput(attrs={"type": "date"})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"id": "id_phone"}),
        label="Номер телефона",
    )
    consent_personal = forms.BooleanField(
        required=True, label="Я даю согласие на обработку персональных данных"
    )
    subscribe_promotions = forms.BooleanField(
        required=True, label="Подписаться на акции"
    )

    def clean_phone(self):
        phone = self.cleaned_data["phone"]

        digits = "".join(c for c in phone if c.isdigit())

        if len(digits) == 10:
            digits = "7" + digits
        elif len(digits) == 11 and digits.startswith("8"):
            digits = "7" + digits[1:]
        elif len(digits) != 11 or not digits.startswith("7"):
            raise forms.ValidationError("Введите корректный российский номер телефона")

        return "+" + digits

    def save(self, request):
        phone = self.cleaned_data["phone"]

        existing = CustomUser.objects.filter(phone=phone).first()

        if existing:
            # активация существующего пациента
            existing.username = self.cleaned_data.get("username", existing.username)
            existing.email = self.cleaned_data.get("email", existing.email)
            existing.set_password(self.cleaned_data["password1"])
            existing.is_active = True

            existing.last_name = self.cleaned_data["last_name"].strip().lower()
            existing.first_name = self.cleaned_data["first_name"].strip().lower()
            existing.patronymic = self.cleaned_data["patronymic"].strip().lower()
            existing.gender = self.cleaned_data["gender"]
            existing.birth_date = self.cleaned_data["birth_date"]
            existing.subscribe_promotions = self.cleaned_data.get(
                "subscribe_promotions", False
            )

            existing.save()
            return existing

        # если пациента не было - обычная регистрация
        user = super().save(request)
        user.last_name = self.cleaned_data["last_name"].strip().lower()
        user.first_name = self.cleaned_data["first_name"].strip().lower()
        user.patronymic = self.cleaned_data["patronymic"].strip().lower()
        user.gender = self.cleaned_data["gender"]
        user.birth_date = self.cleaned_data["birth_date"]
        user.phone = phone
        user.subscribe_promotions = self.cleaned_data.get("subscribe_promotions", False)
        user.save()
        return user


class AdminPatientForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "+7 (XXX) XXX XX XX"}),
        label="Номер телефона",
    )
    gender = forms.ChoiceField(choices=CustomUser.gender_choices, label="Пол")

    class Meta:
        model = CustomUser
        fields = [
            "last_name",
            "first_name",
            "patronymic",
            "gender",
            "birth_date",
            "phone",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        # Приведение ФИО к нижнему регистру
        user.last_name = (user.last_name or "").lower().strip()
        user.first_name = (user.first_name or "").lower().strip()
        user.patronymic = (user.patronymic or "").lower().strip()
        if commit:
            user.save()
        return user


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = [
            "doctor",
            "date",
            "start_time",
            "end_time",
            "status",
            "medical_report",
            "booked_by",
        ]
        widgets = {
            "date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["booked_by"].required = False
        self.fields["booked_by"].widget = forms.HiddenInput()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["subscribe_promotions"]
