from django.shortcuts import render
from allauth.account.views import SignupView
from .forms import CustomSignupForm
from django.contrib import messages


class CustomSignupView(SignupView):
    form_class = CustomSignupForm

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "На ваш email отправлено письмо с подтверждением."
        )
        return response
