from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from .models import HeroCard, SmallCard, SquareCard, Doctor, Services, Promotion, Contacts


class HomeView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero_card'] = HeroCard.objects.filter(is_active=True).first()
        context['small_cards'] = SmallCard.objects.filter(is_active=True)[:2]
        context['square_cards'] = SquareCard.objects.filter(is_active=True)[:6]
        return context
        

class SquareCardDetailView(DetailView):
    model = SquareCard
    template_name = "core/square_card_detail.html"
    context_object_name = "card"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self):
        return get_object_or_404(SquareCard, slug=self.kwargs['slug'])
    

class DoctorsListView(ListView):
    model = Doctor
    template_name="navbar/doctors_list.html"
    context_object_name='doctors'

    def get_queryset(self):
        return Doctor.objects.all()
    

class ServicesListView(ListView):
    model = Services
    template_name = "navbar/services_list.html"
    context_object_name = "services"

    def get_queryset(self):
        return Services.objects.all()
    

class PromotionView(ListView):
    model = Promotion
    template_name = "navbar/promotion_list.html"
    context_object_name = "promotion"

    def get_queryset(self):
        return Promotion.objects.all()
    

class ContactsView(ListView):
    model = Contacts
    template_name = "navbar/contacts.html"
    context_object_name = "contacts"