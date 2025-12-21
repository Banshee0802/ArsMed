from allauth.account.forms import SignupForm
from django import forms
from .models import CustomUser
from core.models import Schedule


class CustomSignupForm(SignupForm):
    last_name = forms.CharField(max_length=50, label="Фамилия")
    first_name = forms.CharField(max_length=50, label="Имя")
    patronymic = forms.CharField(max_length=50, required=False, label="Отчество")
    gender = forms.ChoiceField(
        choices=CustomUser.gender_choices,
        label="Пол",
        widget=forms.RadioSelect
    )
    birth_date = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}))
    phone = forms.CharField(max_length=15, label="Номер телефона")
    consent_personal = forms.BooleanField(
        required=True,
        label="Я даю согласие на обработку персональных данных"
    )

    def save(self, request):
        user = super().save(request)
        user.last_name = self.cleaned_data['last_name']
        user.first_name = self.cleaned_data['first_name']
        user.patronymic = self.cleaned_data['patronymic']
        user.gender = self.cleaned_data['gender']
        user.birth_date = self.cleaned_data['birth_date']
        user.phone = self.cleaned_data['phone']
        user.save()
        return user
    

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['doctor', 'date', 'start_time', 'end_time', 'status', 'medical_report']
        widgets = {
            'date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }