from django.urls import path
from .views import (
    HomeView, SquareCardDetailView
)

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('info-card/<slug:slug>/', SquareCardDetailView.as_view, name='square_card_detail'),
]
