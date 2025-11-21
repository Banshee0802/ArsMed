from django.urls import path
from .views import CustomSignupView

app_name = 'users'

urlpatterns = [
    path('signup/', CustomSignupView.as_view(), name='signup'),
]
