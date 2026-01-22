from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from .models import HeroCard, SmallCard, SquareCard, Doctor, Services, Promotion, Contacts
from users.views import get_available_slots_queryset


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
    

class DoctorDetailView(DetailView):
    model = Doctor
    template_name = "navbar/doctor_detail.html"
    context_object_name="doctor"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Берём доступные слоты для текущего врача
        doctor_slug = self.object.slug
        slots = get_available_slots_queryset(doctor_slug)
        
        # Группируем слоты по дате
        slots_by_date = {}
        for slot in slots:
            slots_by_date.setdefault(slot.date, []).append(slot)
        
        # Кладём в контекст
        context['slots_by_date'] = slots_by_date
        
        return context
    

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


class TermsOfUseView(TemplateView):
    template_name = "core/legal/terms_of_use.html"


class PrivacyPolicyView(TemplateView):
    template_name = "core/legal/privacy_policy.html"