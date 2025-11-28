from django.urls import path
from .views import CustomSignupView, ProfileView

app_name = 'users'

urlpatterns = [
    path('profile/', ProfileView.as_view(), name="profile"),
]
