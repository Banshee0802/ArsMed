from django.urls import path
from django.views.generic import TemplateView

app_name = 'users'

urlpatterns = [
    path('signup/', TemplateView.as_view(template_name='users/signup.html'), name='signup'),
]
