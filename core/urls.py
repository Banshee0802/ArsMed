from django.urls import path
from .views import (
    HomeView, SquareCardDetailView, DoctorsListView,
    ServicesListView
)

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('info-card/<slug:slug>/', SquareCardDetailView.as_view(), name='square_card_detail'),
    path('doctors/', DoctorsListView.as_view(), name='doctors_list'),
    path('services/', ServicesListView.as_view(), name='services_list'),
]
