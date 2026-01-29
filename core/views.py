from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView
from core.forms import ReviewForm
from .models import (
    HeroCard,
    Review,
    Schedule,
    SmallCard,
    SquareCard,
    Doctor,
    Services,
    Promotion,
    Contacts,
)
from users.views import get_available_slots_queryset
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.contrib import messages
from django.db.models import Avg


class HomeView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hero_card"] = HeroCard.objects.filter(is_active=True).first()
        context["small_cards"] = SmallCard.objects.filter(is_active=True)[:2]
        context["square_cards"] = SquareCard.objects.filter(is_active=True)[:6]
        return context


class SquareCardDetailView(DetailView):
    model = SquareCard
    template_name = "core/square_card_detail.html"
    context_object_name = "card"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self):
        return get_object_or_404(SquareCard, slug=self.kwargs["slug"])


class DoctorsListView(ListView):
    model = Doctor
    template_name = "navbar/doctors_list.html"
    context_object_name = "doctors"

    def get_queryset(self):
        return Doctor.objects.all()


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = "navbar/doctor_detail.html"
    context_object_name = "doctor"
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

        # Отзывы только от пациентов завершивших прием
        completed_patients = (
            Schedule.objects.filter(
                doctor=self.object, status="completed", booked_by__isnull=False
            )
            .values_list("booked_by_id", flat=True)
            .distinct()
        )

        reviews = Review.objects.filter(
            doctor=self.object, patient__id__in=completed_patients
        ).select_related("patient")

        # Кладём в контекст
        context["reviews"] = reviews
        context["avg_rating"] = reviews.aggregate(Avg("rating"))["rating__avg"] or 0
        context["review_count"] = reviews.count()
        context["slots_by_date"] = slots_by_date

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


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "navbar/review_form.html"
    success_url = reverse_lazy("core:doctor_detail")

    def dispatch(self, request, *args, **kwargs):
        self.doctor = get_object_or_404(Doctor, slug=kwargs.get("slug"))
        has_completed = Schedule.objects.filter(
            doctor=self.doctor, booked_by=request.user, status="completed"
        ).exists()
        if not has_completed:
            messages.error(
                request, "Вы можете оставить отзыв только после завершённого приёма"
            )
            return redirect("doctor_detail", slug=self.doctor.slug)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.doctor = self.doctor
        form.instance.patient = self.request.user
        messages.success(self.request, "Отзыв успешно добавлен")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("doctor_detail", kwargs={"slug": self.doctor.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctor"] = self.doctor
        return context
