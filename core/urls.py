from django.urls import path
from .views import (
    HomeView, ReviewCreateView, SquareCardDetailView, DoctorsListView, DoctorDetailView,
    ServicesListView, PromotionView, ContactsView,
    TermsOfUseView, PrivacyPolicyView,
)

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('info-card/<slug:slug>/', SquareCardDetailView.as_view(), name='square_card_detail'),
    path('doctors/', DoctorsListView.as_view(), name='doctors_list'),
    path("doctors/<slug:slug>/", DoctorDetailView.as_view(), name="doctor_detail"),
    path('doctor/<slug:slug>/review/', ReviewCreateView.as_view(), name='review_create'),
    path('services/', ServicesListView.as_view(), name='services_list'),
    path('promotion/', PromotionView.as_view(), name='promotion_list'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('terms-of-use/', TermsOfUseView.as_view(), name='terms_of_use'),
    path('privacy-policy', PrivacyPolicyView.as_view(), name='privacy_policy'),
]
