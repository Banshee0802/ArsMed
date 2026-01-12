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
    phone = forms.CharField(max_length=20, 
                            widget=forms.TextInput(attrs={'id': 'id_phone'}),
                            label="Номер телефона")
    consent_personal = forms.BooleanField(
        required=True,
        label="Я даю согласие на обработку персональных данных"
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone']
       
        digits = ''.join(c for c in phone if c.isdigit())
 
        if len(digits) == 10:
            digits = '7' + digits
        elif len(digits) == 11 and digits.startswith('8'):
            digits = '7' + digits[1:]
        elif len(digits) != 11 or not digits.startswith('7'):
            raise forms.ValidationError("Введите корректный российский номер телефона")

        return '+' + digits

    def save(self, request):
        user = super().save(request)
        user.last_name = self.cleaned_data['last_name'].lower().strip()
        user.first_name = self.cleaned_data['first_name'].lower().strip()
        user.patronymic = self.cleaned_data['patronymic'].lower().strip()
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