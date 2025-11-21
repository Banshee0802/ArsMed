from django.shortcuts import render
from allauth.account.views import SignupView
from .forms import CustomSignupForm


class CustomSignupView(SignupView):
    form_class = CustomSignupForm

